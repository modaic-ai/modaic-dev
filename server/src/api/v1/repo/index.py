import uuid
from pytz import UTC
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException
from src.objects.schemas.repo import RepoSchema
from src.api.v1.auth.utils import manager
from src.objects.index import (
    Repo,
    PublicRepoSchema,
    Contributor,
    CreateRepoRequest,
    UpdateRepoRequest,
    UserSchema,
    Star,
    RepoTag,
    ContributorSchema,
)
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from datetime import datetime
from src.db.pg import get_db
from src.lib.logger import logger
from src.lib.s3 import s3_client
from sqlalchemy import func

router = APIRouter()


@router.get("/user")
def get_user_repos(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    criteria: Optional[str] = None,
    user: UserSchema = Depends(manager.required),
    db: Session = Depends(get_db),
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
        all_repos = (
            db.query(Repo).filter_by(**filter_query).order_by(Repo.updated.desc()).all()
        )

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


from sqlalchemy import or_, and_, desc
from datetime import datetime


@router.get("/")
async def get_repos(
    limit: int = 20,
    cursor: str = None,
    visibility: str = None,
    userId: str = None,
    user_making_request: UserSchema = Depends(manager.optional),
    db: Session = Depends(get_db),
):
    """
    Retrieve repos with optional filtering by visibility, user ID, and cursor-based pagination.

    Args:
        limit (int): Max number of repos to fetch (default: 20).
        cursor (str): ISO timestamp to paginate older updates.
        visibility (str): Filter by visibility level (e.g., "public").
        userId (str): Target user ID to fetch owned or contributed repos.
        user_making_request (User): The user making the request (optional).

    Returns:
        dict: A response containing the list of repos, next pagination cursor, and total count.
    """
    try:
        # start with base query
        query = db.query(Repo)
        count_query = db.query(Repo)

        # determine if the requester is the same as the target user
        is_owner = user_making_request and user_making_request.userId == userId

        # build filters list
        filters = []
        count_filters = []

        # apply visibility filter
        if visibility:
            visibility_filter = Repo.visibility == visibility
            filters.append(visibility_filter)
            count_filters.append(visibility_filter)

        # filter for user-owned and contributed repos
        if userId:
            # get contributed repo IDs
            contributions = (
                db.query(Contributor).filter(Contributor.userId == userId).all()
            )
            contributed_ids = [c.repoId for c in contributions]

            # create user ownership/contribution filter
            user_filters = [Repo.adminId == userId]  # user owns the repo
            if contributed_ids:
                user_filters.append(
                    Repo.repoId.in_(contributed_ids)
                )  # user contributed

            user_filter = or_(*user_filters)

            if not is_owner:
                # only show public repos to others
                combined_filter = and_(user_filter, Repo.visibility == "public")
            else:
                combined_filter = user_filter

            filters.append(combined_filter)
            count_filters.append(combined_filter)

        # apply cursor-based pagination filter
        if cursor:
            try:
                cursor_datetime = datetime.fromisoformat(cursor.replace("Z", "+00:00"))
                cursor_filter = Repo.updated < cursor_datetime
                filters.append(cursor_filter)
                count_filters.append(cursor_filter)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid cursor format")

        # apply all filters
        if filters:
            query = query.filter(and_(*filters))
            count_query = count_query.filter(and_(*count_filters))

        # get total count (expensive but easier to implement)
        total_repos = count_query.count()

        # fetch repos with pagination
        repos_list = (
            query.order_by(desc(Repo.updated))
            .limit(limit + 1)  # fetch one extra to check for next page
            .all()
        )

        # check if there's a next page
        has_next = len(repos_list) > limit
        next_cursor = None

        if has_next:
            # remove the extra repo and set cursor
            next_cursor = repos_list[-1].updated
            if isinstance(next_cursor, str):
                next_cursor = next_cursor
            else:
                next_cursor = next_cursor.isoformat().replace("+00:00", "Z")
            repos_list = repos_list[:-1]

        # convert to dictionaries
        repos_dicts = []
        for repo in repos_list:
            # use your Pydantic schema here - adjust based on what you have
            repo_schema = PublicRepoSchema.model_validate(
                repo
            )  # or RepoSchema if owner
            repos_dicts.append(repo_schema.model_dump())

        return {"result": repos_dicts, "nextCursor": next_cursor, "total": total_repos}

    except Exception as e:
        logger.error(f"Error fetching repos: {e}")
        raise HTTPException(status_code=500, detail="Error fetching repos")


@router.get("/popular")
def get_popular_repos(
    limit: int = 10,
    _: UserSchema = Depends(manager.optional),
    db: Session = Depends(get_db),
):
    """
    Retrieve the most popular repos sorted by number of stars.

    Args:
        limit (int): Maximum number of repos to return (default: 10).
        _ (User): Optional authenticated user (unused but dependency is required).

    Returns:
        dict: A list of the most liked repos.
    """
    try:
        # query with subquery to count stars
        popular_repos = (
            db.query(Repo, func.count(Star.starId).label("stars_count"))
            .outerjoin(Star)  # left join to include repos with 0 stars
            .filter(Repo.visibility == "public")
            .group_by(Repo.repoId)
            .order_by(desc("stars_count"))
            .limit(limit)
            .all()
        )

        # convert to dictionaries
        repos_dicts = []
        for repo_tuple in popular_repos:
            repo = PublicRepoSchema(**repo_tuple[0])  # the Repo object
            likes_count = repo_tuple[1]  # the count

            repo_dict = repo.model_dump()
            # optionally add star count to response
            repo_dict["likes_count"] = likes_count

            repos_dicts.append(repo_dict)

        return {"result": repos_dicts}

    except Exception as e:
        logger.error(f"Error fetching popular repos: {e}")
        raise HTTPException(status_code=500, detail="Error fetching popular repos")


@router.get("/starred")
def get_user_starred_repos(
    limit: int = Query(20, description="Maximum number of starred repos to return"),
    offset: int = Query(0, description="Number of repos to skip"),
    user: UserSchema = Depends(manager.required),
    db: Session = Depends(get_db),
):
    """
    Retrieve all repos starred by the authenticated user,
    sorted by creation date in descending order.

    Args:
        limit (int): Maximum number of repos to return (default: 20).
        offset (int): Number of repos to skip for pagination (default: 0).
        user (UserSchema): The currently authenticated user.

    Returns:
        dict: A list of starred repos with pagination info.
    """
    try:
        # get total count
        total_count = (
            db.query(func.count(Star.starId))
            .filter(Star.userId == user.userId)
            .scalar()
        )

        # get starred repos with pagination
        starred_repos = (
            db.query(Repo)
            .join(Star, Repo.repoId == Star.repoId)
            .filter(Star.userId == user.userId)
            .order_by(desc(Star.created))
            .offset(offset)
            .limit(limit)
            .all()
        )

        # convert to dictionaries
        starred_repos_list = []
        for repo in starred_repos:
            repo_schema = PublicRepoSchema(**repo)
            starred_repos_list.append(repo_schema.model_dump())

        return {
            "result": starred_repos_list,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(starred_repos_list) < total_count,
        }

    except Exception as e:
        logger.error(f"Error fetching starred repos: {e}")
        raise HTTPException(status_code=500, detail="Error fetching starred repos")


@router.post("/")
def create_repo_endpoint(
    create_repo_payload: CreateRepoRequest,
    user: UserSchema = Depends(manager.required),
    db: Session = Depends(get_db),
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
        repo_to_create = RepoSchema(**create_repo_payload.model_dump())

        db.add(repo_to_create)
        db.commit()
        db.refresh(repo_to_create)

        return {"result": repo_to_create}

    except Exception as e:
        logger.error(f"Error creating repo: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating repo")


@router.delete("/{repo_id}")
def delete_repo(
    repo_id: str,
    user: UserSchema = Depends(manager.required.ADMIN),
    db: Session = Depends(get_db),
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
        repo_to_delete = db.query(Repo).filter(Repo.repoId == repo_id).first()
        repo_to_delete = RepoSchema(**repo_to_delete)

        if not repo_to_delete or repo_to_delete.adminId != user.userId:
            logger.info(f"Repo {repo_id} not found or not owned by user {user.userId}")
            return {"result": False}

        db.delete(repo_to_delete)
        db.commit()

        logger.info(f"Repo {repo_id} deleted by user {user.userId}")
        path_to_clean = f"files/{user.userId}/{repo_id}"
        s3_client.delete_directory(path_to_clean)
        return {"result": True}

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting repo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{repo_id}")
def update_repo(
    repo_id: str,
    update_repo_payload: UpdateRepoRequest,
    _: UserSchema = Depends(manager.required.WRITE),
    db: Session = Depends(get_db),
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

        # prepare fields to update
        update_fields = update_repo_payload.model_dump(exclude_none=True)
        update_fields["updated"] = datetime.now(UTC)

        # perform update in the database
        result = db.query(Repo).filter(Repo.repoId == repo_id).update(update_fields)

        if result == 0:
            raise HTTPException(
                status_code=404, detail="Repo not found or no changes applied"
            )

        return {"result": True}

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating repo: {str(e)}. Database was rolled back!")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repo_id}")
def get_repo_by_id(
    repo_id: str,
    user: Optional[UserSchema] = Depends(
        manager.optional.READ
    ),  # Dependency handles visibility check
    db: Session = Depends(get_db),
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
        repo_data = db.query(Repo).filter(Repo.repoId == repo_id).first()
        repo_data = RepoSchema(**repo_data)
        return {"result": repo_data.model_dump()}

    except Exception as e:
        logger.error(f"Error getting repo by id: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{repo_id}/star")
def star_repo(
    repo_id: str,
    user: UserSchema = Depends(manager.required),
    db: Session = Depends(get_db),
):
    """
    Star a repo on behalf of the current user.

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
        repo_data = db.query(Repo).filter(Repo.repoId == repo_id).first()
        repo_data = RepoSchema(**repo_data)

        if not repo_data or user.userId in repo_data.stars:
            raise HTTPException(
                status_code=400, detail="Already liked or repo not found"
            )

        # create star
        star = Star(
            starId=str(uuid.uuid4()),
            repoId=repo_id,
            userId=user.userId,
        )
        db.add(star)
        db.commit()

        db.query(Repo).filter(Repo.repoId == repo_id).update(
            {Repo.stars: Repo.stars + 1}
        )
        db.commit()

        return {"result": len(repo_data.stars)}

    except Exception as e:
        db.rollback()
        logger.error(f"Error liking repo: {str(e)}. Database was rolled back!")
        raise HTTPException(status_code=500, detail="Failed to like repo")


@router.post("/{repo_id}/unlike")
def unlike_repo(
    repo_id: str,
    user: UserSchema = Depends(manager.required),
    db: Session = Depends(get_db),
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

        repo_data = db.query(Repo).filter(Repo.repoId == repo_id).first()
        repo_data = RepoSchema(**repo_data)

        if not repo_data or user.userId not in repo_data.stars:
            raise HTTPException(
                status_code=400, detail="Not liked yet or repo not found"
            )

        db.query(Repo).filter(Repo.repoId == repo_id).update(
            {Repo.stars: Repo.stars - 1}
        )
        db.commit()

        db.query(Star).filter(
            Star.repoId == repo_id, Star.userId == user.userId
        ).delete()
        db.commit()

        return {"result": len(repo_data.stars)}

    except Exception as e:
        db.rollback()
        logger.error(f"Error unliking repo: {str(e)}. Database was rolled back!")
        raise HTTPException(status_code=500, detail="Failed to unlike repo")


@router.patch("/{repo_id}/tag/{tag}")
def add_tag(
    repo_id: str,
    tag: str,
    _: UserSchema = Depends(manager.required.WRITE),
    db: Session = Depends(get_db),
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

        tag_to_create = RepoTag(
            tagId=str(uuid.uuid4()),
            repoId=repo_id,
            tag=tag,
        )
        db.add(tag_to_create)
        db.commit()

        return {"result": True}

    except Exception as e:
        db.rollback()
        logger.error(f"Error adding tag: {str(e)}. Database was rolled back!")
        raise HTTPException(status_code=500, detail="Failed to add tag")


@router.delete("/{repo_id}/tag/{tag}")
def remove_tag(
    repo_id: str,
    tag: str,
    _: UserSchema = Depends(manager.required.WRITE),
    db: Session = Depends(get_db),
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
        db.query(RepoTag).filter(
            RepoTag.tag == formatted_tag, RepoTag.repoId == repo_id
        ).delete()
        db.commit()
        return {"result": True}

    except Exception as e:
        db.rollback()
        logger.error(f"Error removing tag: {str(e)}. Database was rolled back!")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repo_id}/contributors")
def get_repo_contributors(
    repo_id: str,
    _: Optional[UserSchema] = Depends(manager.optional),
    db: Session = Depends(get_db),
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
        repo = db.query(Repo).filter(Repo.repoId == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repo not found")

        repo = RepoSchema(**repo)

        # collect contributors from iterations list
        contributers = db.query(Contributor).filter(Contributor.repoId == repo_id).all()
        contributers = [
            ContributorSchema(**contributer) for contributer in contributers
        ]

        return {"result": contributers}

    except Exception as e:
        logger.error(f"Error getting repo contributers: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting repo contributers: {e}",
        )
