import os
import uuid
from pytz import UTC
from datetime import datetime
from typing import Optional
from pymongo import ReturnDocument
from fastapi import APIRouter, Depends, UploadFile, File, Query, BackgroundTasks
from fastapi.exceptions import HTTPException
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename
from src.models.index import Contributors
from src.api.v1.auth.utils import manager
from src.models.index import (
    Repos,
    RepoModel,
    GetRepoRequest,
    CreateRepoRequest,
    UpdateRepoRequest,
    UserModel,
)
from src.lib.logger import logger
from src.lib.s3 import s3_client
from src.core.config import settings
from src.service.repo import repo_service

router = APIRouter()


@router.get("/user")
def get_user_repos(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    criteria: Optional[str] = None,
    user: UserModel = Depends(manager.required),
):
    """
    Retrieve paginated repos belonging to the authenticated user,
    with optional filtering by visibility (e.g., "Public", "Private").

    Args:
        page (int): The current page number (1-indexed).
        page_size (int): Number of items per page (max 100).
        criteria (str, optional): Visibility filter (e.g., "public", "private").
        user (User): The authenticated user.

    Returns:
        dict: Paginated list of the user's repos with metadata.
    """
    try:
        # construct base filter
        filter_query = {"adminId": user.userId}

        # normalize and apply visibility filter
        visibility = criteria.capitalize() if criteria else None
        if visibility:
            filter_query["visibility"] = visibility

        # query and sort by latest update
        all_repos = list(Repos.find(filter_query, {"_id": 0}, sort=[("updated", -1)]))

        total_repos = len(all_repos)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        paginated_repos = all_repos[start_index:end_index]

        return {
            "items": paginated_repos,
            "total": total_repos,
            "page": page,
            "page_size": page_size,
            "nextCursor": page + 1 if end_index < total_repos else None,
            "prevCursor": page - 1 if page > 1 else None,
        }

    except Exception as e:
        logger.error(f"Error fetching repos: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching user repos {e}")


@router.get("/")
async def get_repos(
    limit: int = 20,
    cursor: str = None,
    visibility: str = None,
    userId: str = None,
    user_making_request: UserModel = Depends(manager.optional),
):
    """
    Retrieve repos with optional filtering by visibility, user ID, and cursor-based pagination.

    Args:
        limit (int): Max number of repos to fetch (default: 20).
        cursor (str): ISO timestamp to paginate older updates.
        visibility (str): Filter by visibility level (e.g., "Public").
        userId (str): Target user ID to fetch owned or contributed repos.
        user_making_request (User): The user making the request (optional).

    Returns:
        dict: A response containing the list of repos, next pagination cursor, and total count.
    """
    try:
        query = {}

        # determine if the requester is the same as the target user
        is_owner = user_making_request and user_making_request.userId == userId

        # apply visibility filter
        if visibility:
            query["visibility"] = visibility

        # filter for user-owned and contributed repos
        if userId:
            contributions = list(
                Contributors.find({"userId": userId}, {"repoId": 1, "_id": 0})
            )
            contributed_ids = [c["repoId"] for c in contributions]

            user_query = {
                "$or": [{"userId": userId}, {"repoId": {"$in": contributed_ids}}]
            }

            if not is_owner:
                # only show public repos to others
                query = {"$and": [user_query, {"visibility": "Public"}]}
            else:
                query.update(user_query)

        # apply cursor-based pagination filter
        if cursor:
            cursor_filter = {"updated": {"$lt": datetime.fromisoformat(cursor)}}

            if "$and" in query:
                query["$and"].append(cursor_filter)
            else:
                query.update(cursor_filter)

        # fetch repos with pagination
        repos_list = list(
            Repos.find(query, {"_id": 0})
            .sort("updated", -1)
            .limit(limit + 1)  # fetch one extra to check for next page
        )

        total_repos = Repos.count_documents(
            query
        )  # this is a bit expensive but way easier to implement here

        has_next = len(repos_list) > limit
        next_cursor = repos_list[-1]["updated"].isoformat() if has_next else None

        if has_next:
            repos_list = repos_list[:-1]

        return {"result": repos_list, "nextCursor": next_cursor, "total": total_repos}

    except Exception as e:
        logger.error(f"Error fetching repos: {e}")
        raise HTTPException(status_code=500, detail="Error fetching repos")


@router.get("/popular")
def get_popular_repos(limit: int = 10, _: UserModel = Depends(manager.optional)):
    """
    Retrieve the most popular repos sorted by number of stars.

    Args:
        limit (int): Maximum number of repos to return (default: 10).
        _ (User): Optional authenticated user (unused but dependency is required).

    Returns:
        dict: A list of the most liked repos.
    """
    try:
        pipeline = [
            {"$addFields": {"likesCount": {"$size": "$likes"}}},
            {"$sort": {"likesCount": -1}},
            {"$limit": limit},
            {"$project": {"_id": 0, "likesCount": 0}},
        ]

        top_repos = list(Repos.aggregate(pipeline))

        return {"result": top_repos}

    except Exception as e:
        logger.error(f"Error fetching popular repos: {e}")
        raise HTTPException(status_code=500, detail="Error fetching popular repos")


@router.get("/liked")
def get_user_liked_repos(user: UserModel = Depends(manager.required)):
    """
    Retrieve all repos liked by the authenticated user,
    sorted by creation date in descending order.

    Args:
        user (UserModel): The currently authenticated user.

    Returns:
        dict: A list of liked repos.
    """
    try:
        liked_repos = list(
            Repos.find({"likes": user.userId}, {"_id": 0}, sort=[("created", -1)])
        )
        return {"result": liked_repos}

    except Exception as e:
        logger.error(f"Error fetching liked repos: {e}")
        raise HTTPException(status_code=500, detail="Error fetching liked repos")


@router.post("/")
def create_repo_endpoint(
    create_repo_payload: CreateRepoRequest,
    background_tasks: BackgroundTasks,
    user: UserModel = Depends(manager.required),
):
    """
    Endpoint to create a new repo for the authenticated user.

    Args:
        create_repo_payload (CreateRepoRequest): The payload containing repo creation data.
        background_tasks (BackgroundTasks): FastAPI's background task manager.
        user (User): The currently authenticated user.

    Returns:
        dict: Contains the ID of the newly created repo.
    """
    try:
        # create the repo and retrieve its ID
        repo = repo_service.create_repo(create_repo_payload)

        # fetch the created repo document
        repo_document = Repos.find_one({"repoId": repo.repoId, "adminId": user.userId})

        # queue background task to embed and upsert the repo
        # background_tasks.add_task(repo_service.embed_and_upsert_repo, repo_document)

        return {"result": repo_document}

    except Exception as e:
        logger.error(f"Error creating repo: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating repo")


@router.post("/{repo_id}/upload/image")
async def upload_image_to_repo(
    repo_id: str,
    files: list[UploadFile] = File(..., description="Multiple files as UploadFile"),
    _: UserModel = Depends(manager.required.WRITE),
):
    """
    Upload multiple image files to a specific repo.

    Args:
        repo_id (str): The target repo's ID.
        files (list[UploadFile]): List of image files to upload.
        user (User): The authenticated user with WRITE access.

    Returns:
        dict: A list of uploaded image URLs.
    """
    # verify that the target repo exists
    repo_data = Repos.find_one({"repoId": repo_id})
    if not repo_data:
        raise HTTPException(status_code=404, detail="Repo not found")

    repo = RepoModel(**repo_data)
    uploaded_image_urls = []

    try:
        for file in files:
            # sanitize filename and prepare storage path
            safe_filename = secure_filename(file.filename)
            object_name = f"files/{repo.adminId}/{repo_id}/images/{safe_filename}"

            temp_dir = "/tmp/repo_uploads"
            os.makedirs(temp_dir, exist_ok=True)

            temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{safe_filename}")

            try:
                # read file content and write to temp location
                contents = await file.read()
                with open(temp_path, "wb") as buffer:
                    buffer.write(contents)

                # upload to s3 and construct public url
                image_url = s3_client.upload_file(temp_path, object_name)
                uploaded_image_urls.append(image_url)

                # update repo document with new image and updated timestamp
                result = Repos.update_one(
                    {"repoId": repo_id},
                    {
                        "$push": {"imageKeys": object_name},
                        "$set": {"updated": datetime.now(UTC)},
                    },
                )

                if result.modified_count == 0:
                    raise HTTPException(status_code=404, detail="Repo not found")

            except Exception as e:
                logger.error(f"Error uploading file {safe_filename}: {str(e)}")
                raise HTTPException(
                    status_code=500, detail=f"Error uploading file: {str(e)}"
                )
            finally:
                # clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        return {"imageUrls": uploaded_image_urls}

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{repo_id}/image/{image_name}")
def delete_image(
    repo_id: str, image_name: str, user: UserModel = Depends(manager.required.WRITE)
):
    """
    Delete an image from a given repo project in both the database and S3 storage.

    Args:
        repo_id (str): The ID of the repo to which the image belongs.
        image_name (str): The filename of the image to delete.
        user (User): The authenticated user with WRITE access to the repo.

    Returns:
        dict: A dictionary indicating whether the deletion was successful.

    Raises:
        HTTPException:
            - 404 if the repo or image is not found.
            - 500 if an unexpected error occurs during deletion.
    """
    try:
        # fetch the repo document
        repo_data = Repos.find_one({"repoId": repo_id})
        if not repo_data:
            raise HTTPException(status_code=404, detail="Repo not found")

        repo = RepoModel(**repo_data)
        file_key = f"files/{repo.adminId}/{repo_id}/images/{image_name}"

        # remove image reference from the database
        result = Repos.update_one(
            {"repoId": repo_id},
            {"$pull": {"imageKeys": file_key}, "$set": {"updated": datetime.now(UTC)}},
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Repo not found")

        # delete the image from s3 storage
        s3_client.delete_file(file_key)

        return {"result": True}

    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repo_id}/images")
def get_repo_images(
    repo_id: str, _: Optional[UserModel] = Depends(manager.optional.READ)
):
    """
    Retrieve all image URLs associated with the specified repo.

    Args:
        repo_id (str): The ID of the repo to fetch image URLs from.
        _ (Optional[User]): Optional authenticated user with read access.

    Returns:
        dict: A dictionary with a "result" key containing a list of image URLs.

    Raises:
        HTTPException:
            - 404 if the repo is not found.
            - 500 if there's an error generating the URLs.
    """
    try:
        repo_data = Repos.find_one({"repoId": repo_id})
        if not repo_data:
            raise HTTPException(status_code=404, detail="Repo not found")

        repo = RepoModel(**repo_data)

        urls = [f"https://{settings.cloudfront_domain}/{key}" for key in repo.imageKeys]

        return {"result": urls}

    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{repo_id}")
def delete_repo(
    repo_id: str,
    background_tasks: BackgroundTasks,
    user: UserModel = Depends(manager.required.ADMIN),
):
    """
    Delete a repo and all associated data, including sources, documents, images,
    embeddings, and S3 files. Also updates the user's file storage usage.

    Args:
        repo_id (str): ID of the repo to delete.
        background_tasks (BackgroundTasks): FastAPI background task runner.
        user (User): Authenticated user with OWNER-level permissions.

    Returns:
        dict: {"result": True} if deleted, {"result": False} if not found or not owned.

    Raises:
        HTTPException: 500 if an unexpected error occurs during deletion.
    """
    try:
        # delete the repo document from the database
        repo_to_delete = Repos.find_one_and_delete(
            {"repoId": repo_id, "adminId": user.userId}
        )
        if not repo_to_delete:
            logger.info(f"Repo {repo_id} not found or not owned by user {user.userId}")
            return {"result": False}

        logger.info(f"Repo {repo_id} deleted by user {user.userId}")
        path_to_clean = f"files/{user.userId}/{repo_id}"
        s3_client.delete_directory(path_to_clean)
        return {"result": True}

    except Exception as e:
        logger.error(f"Error deleting repo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{repo_id}")
def update_repo(
    repo_id: str,
    update_repo_payload: UpdateRepoRequest,
    background_tasks: BackgroundTasks,
    _: UserModel = Depends(manager.required.WRITE),
):
    """
    Update an existing repo with new configuration values.

    Args:
        repo_id (str): The ID of the repo to update.
        update_repo_payload (UpdateRepoRequest): Payload containing updated fields.
        background_tasks (BackgroundTasks): FastAPI background task runner.
        _ (User): Authenticated user with WRITE access.

    Returns:
        dict: {"result": True} if update was successful.

    Raises:
        HTTPException:
            - 404 if the repo is not found or no changes were applied.
            - 500 if an unexpected error occurs.
    """
    try:
        # fetch the existing repo
        repo_data = Repos.find_one({"repoId": repo_id})
        if not repo_data:
            raise HTTPException(status_code=404, detail="Repo not found")

        # prepare fields to update
        update_fields = update_repo_payload.model_dump(exclude_none=True)
        update_fields["updated"] = datetime.now(UTC)

        # perform update in the database
        result = Repos.update_one(
            {"repoId": repo_id},
            {"$set": update_fields},
        )

        if result.modified_count == 0:
            raise HTTPException(
                status_code=404, detail="Repo not found or no changes applied"
            )

        return {"result": True}

    except Exception as e:
        logger.error(f"Error updating repo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repo_id}")
def get_repo_by_id(
    repo_id: str,
    user: Optional[UserModel] = Depends(
        manager.optional.READ
    ),  # Dependency handles visibility check
):
    """
    Retrieve a repo by its unique ID.

    Args:
        repo_id (str): The ID of the repo to retrieve.
        _ (Optional[User]): Optional authenticated user (used for visibility checks).

    Returns:
        dict: A dictionary containing the repo data under the "result" key.

    Raises:
        HTTPException:
            - 404 if the repo is not found.
            - 500 if an unexpected error occurs.
    """
    try:
        repo_data = repo_service.get_repo(
            GetRepoRequest(repoId=repo_id, authorized=True)
        )
        return {"result": repo_data.model_dump()}

    except Exception as e:
        logger.error(f"Error getting repo by id: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{repo_id}/like")
def like_repo(
    repo_id: str,
    user: UserModel = Depends(manager.required),
):
    """
    Like a repo on behalf of the current user.

    Args:
        repo_id (str): The ID of the repo to like.
        user (User): The authenticated user performing the like action.

    Returns:
        dict: A dictionary with the updated number of likes under the "result" key.

    Raises:
        HTTPException:
            - 400 if the user already liked the repo or if the repo does not exist.
            - 500 if an unexpected error occurs.
    """
    try:
        updated_repo = Repos.find_one_and_update(
            {
                "repoId": repo_id,
                "stars": {"$ne": user.userId},
            },  # only update if not already liked
            {"$addToSet": {"stars": user.userId}},  # add user ID to 'likes' array
            return_document=ReturnDocument.AFTER,
        )

        if not updated_repo:
            raise HTTPException(
                status_code=400, detail="Already liked or repo not found"
            )

        return {"result": len(updated_repo["stars"])}

    except Exception as e:
        logger.error(f"Error liking repo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{repo_id}/unlike")
def unlike_repo(
    repo_id: str,
    user: UserModel = Depends(manager.required),
):
    """
    Unlike a previously liked repo on behalf of the current user.

    Args:
        repo_id (str): The ID of the repo to unlike.
        user (User): The authenticated user performing the unlike action.

    Returns:
        dict: A dictionary with the updated number of likes under the "result" key.

    Raises:
        HTTPException:
            - 400 if the repo was not liked by the user or does not exist.
            - 500 if an unexpected error occurs.
    """
    try:
        updated_repo = Repos.find_one_and_update(
            {
                "repoId": repo_id,
                "stars": user.userId,
            },  # only update if user already liked it
            {"$pull": {"stars": user.userId}},  # remove user ID from 'likes' array
            return_document=ReturnDocument.AFTER,
        )

        if not updated_repo:
            raise HTTPException(
                status_code=400, detail="Not liked yet or repo not found"
            )

        return {"result": len(updated_repo["stars"])}

    except Exception as e:
        logger.error(f"Error unliking repo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/saved")
def get_user_saved_repos(
    user_id: str,
    user: Optional[UserModel] = Depends(manager.optional),
):
    """
    Retrieve all saved repos for a user.
    If the requesting user is not the resource owner, only public repos are returned.

    Args:
        user_id (str): ID of the user whose repos are being requested.
        user (Optional[User]): Authenticated user (optional).

    Returns:
        dict: A dictionary with the user's saved repos under the "result" key.

    Raises:
        HTTPException: 500 if an unexpected error occurs.
    """
    query = {"adminId": user_id}
    resource_owner = user is not None and user.userId == user_id

    if not resource_owner:
        query["visibility"] = "Public"

    try:
        result = Repos.find(query, {"_id": 0})
        return {"result": result}

    except Exception as e:
        logger.error(f"Error getting user saved repos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{repo_id}/tag/{tag}")
def add_tag(
    repo_id: str,
    tag: str,
    _: UserModel = Depends(manager.required.WRITE),
):
    """
    Add a tag to a repo.

    Args:
        repo_id (str): The ID of the repo to tag.
        tag (str): The tag to add.
        user (User): Authenticated user with WRITE access.

    Returns:
        dict: {"result": True} if the tag was added successfully.

    Raises:
        HTTPException: 500 if an unexpected error occurs.
    """
    try:
        formatted_tag = tag.lower()
        Repos.update_one(
            {"repoId": repo_id},
            {"$addToSet": {"tags": formatted_tag}},
        )
        return {"result": True}

    except Exception as e:
        logger.error(f"Error adding tag: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{repo_id}/tag/{tag}")
def remove_tag(
    repo_id: str,
    tag: str,
    _: UserModel = Depends(manager.required.WRITE),
):
    """
    Remove a tag from a repo.

    Args:
        repo_id (str): The ID of the repo to update.
        tag (str): The tag to remove.
        user (User): Authenticated user with WRITE access.

    Returns:
        dict: {"result": True} if the tag was removed successfully.

    Raises:
        HTTPException: 500 if an unexpected error occurs.
    """
    try:
        formatted_tag = tag.lower()
        Repos.update_one(
            {"repoId": repo_id},
            {"$pull": {"tags": formatted_tag}},
        )
        return {"result": True}

    except Exception as e:
        logger.error(f"Error removing tag: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repo_id}/contributors")
def get_repo_contributors(
    repo_id: str,
    _: Optional[UserModel] = Depends(manager.optional),
):
    """
    Retrieve the list of contributors for a given repo.

    Args:
        repo_id (str): The unique identifier of the repo.
        user (Optional[User]): The optionally authenticated user making the request.

    Returns:
        dict: A list of public user data for each contributor.
    """
    try:
        # find the repo by ID
        repo = Repos.find_one({"repoId": repo_id})
        if not repo:
            raise HTTPException(status_code=404, detail="Repo not found")

        repo = RepoModel(**repo)

        # collect contributors from iterations list
        contributers = Contributors.find({"repoId": repo_id}, {"_id": 0})
        contributers = list(contributers)

        return {"result": contributers}

    except Exception as e:
        logger.error(f"Error getting repo contributers: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting repo contributers: {e}",
        )
