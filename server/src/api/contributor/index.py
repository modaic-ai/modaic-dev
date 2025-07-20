from typing import Literal, Optional
from fastapi import APIRouter, HTTPException, Depends
from src.models.index import UserModel, PublicUserModel
from src.api.auth.utils import manager
from src.lib.logger import logger
from src.models.index import Repos, Contributors, Contributor, Users, RepoModel
from pydantic import BaseModel
from datetime import datetime
from pytz import UTC
import uuid
from fastapi import BackgroundTasks

router = APIRouter()


class InviteContributer(BaseModel):
    emailToInvite: str


@router.post("/repo/{repo_id}")
def invite_contributer(
    repo_id: str,
    payload: InviteContributer,
    background_tasks: BackgroundTasks,
    sender: UserModel = Depends(manager.required.ADMIN),
):
    try:
        invite_email = payload.emailToInvite

        if sender.email == invite_email:
            raise HTTPException(status_code=400, detail="You cannot invite yourself")

        # check for existing contributor relationship
        existing_relationship = Contributors.find_one(
            {"email": invite_email, "repoId": repo_id}, {"_id": 0}
        )

        if existing_relationship:
            existing_contrib = Contributor(**existing_relationship)
            if existing_contrib.pending:
                raise HTTPException(
                    status_code=400, detail="Invitation already sent to this email"
                )
            raise HTTPException(
                status_code=400, detail="User already has access to this project"
            )

        # check if user already exists
        existing_user_doc = Users.find_one({"email": invite_email}, {"_id": 0})

        if existing_user_doc:
            existing_user = UserModel(**existing_user_doc)
            logger.info(f"User found: {existing_user}")

            # check if user is already a contributor
            if Contributors.find_one(
                {"userId": existing_user.userId, "repoId": repo_id}, {"_id": 0}
            ):
                logger.info("User already has access to this project")
                raise HTTPException(
                    status_code=400, detail="User already has access to this project"
                )

            contributor_info = Contributor(
                contributorId=str(uuid.uuid4()),
                userId=existing_user.userId,
                username=existing_user.username,
                email=existing_user.email,
                repoId=repo_id,
                invitedBy=sender.userId,
            )

            Contributors.insert_one(contributor_info.model_dump())
            logger.info(f"Contributor invited: {contributor_info.contributorId}")

            # send email to user
            repo_doc = Repos.find_one({"repoId": repo_id}, {"_id": 0})
            repo = RepoModel(**repo_doc)

            """
            background_tasks.add_task(
                email_service.user_invited_to_repo,
                recipient_email=invite_email,
                recipient_name=existing_user.fullName or existing_user.username,
                repo_name=repo.name,
                repo_link=f"{settings.next_url}/repo/{repo_id}",
                sender_name=sender.fullName or sender.username,
            )
            """
            return {"result": PublicUserModel(**existing_user.model_dump())}

        elif not existing_user_doc:
            logger.info(f"User not found: {invite_email}..")
            raise HTTPException(status_code=404, detail="User not found")
            # TODO: send email to user to create an account and invite them to the project

    except Exception as e:
        logger.error(f"Error inviting contributor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/repo/{repo_id}/{contributor_id}/invite")
def revoke_invite(
    repo_id: str, contributor_id: str, _: UserModel = Depends(manager.required.ADMIN)
):
    try:
        existing_contributor = Contributors.find_one(
            {"contributorId": contributor_id, "repoId": repo_id}, {"_id": 0}
        )
        if existing_contributor:
            existing_contributor = Contributor(**existing_contributor)
            Contributors.delete_one(
                {"contributorId": existing_contributor.contributorId}
            )
            logger.info(
                f"Contributor revoked invite: {existing_contributor.email} with access level {existing_contributor.accessLevel}. Invited by {existing_contributor.invitedBy}"
            )
            return {"result": True}

        raise HTTPException(status_code=404, detail="Contributor not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking invite: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke invite")


@router.get("/repo/{repo_id}")
def get_all_contributors_for_repo(
    repo_id: str, _: UserModel = Depends(manager.optional.READ)
):
    try:
        contributors = Contributors.find({"repoId": repo_id}, {"_id": 0})
        contributors = list(contributors)
        logger.info(f"Contributors for repo {repo_id}: {contributors}")
        return {"result": contributors}

    except Exception as e:
        logger.error(f"Error getting contributors: {e}")
        raise HTTPException(status_code=500, detail="Failed to get contributors")


class ToggleContributorRole(BaseModel):
    role: Literal["owner", "write", "read"]


@router.patch("/repo/{repo_id}/{contributor_id}/role")
def toggle_contributor_role(
    repo_id: str,
    contributor_id: str,
    payload: ToggleContributorRole,
    _: UserModel = Depends(manager.required.ADMIN),
):
    try:
        existing_contributor = Contributors.find_one(
            {"contributorId": contributor_id, "repoId": repo_id}, {"_id": 0}
        )
        if existing_contributor:
            existing_contributor = Contributor(**existing_contributor)
            Contributors.update_one(
                {"contributorId": existing_contributor.contributorId},
                {"$set": {"accessLevel": payload.role}},
            )
            logger.info(
                f"Contributor role toggled: {existing_contributor.contributorId}"
            )
            return {"result": True}

        raise HTTPException(status_code=404, detail="Contributor not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling contributor role: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle contributor role")


@router.delete("/repo/{repo_id}/{contributor_id}")
def delete_contributor(
    repo_id: str, contributor_id: str, _: UserModel = Depends(manager.required.ADMIN)
):
    try:
        existing_contributor = Contributors.find_one(
            {"contributorId": contributor_id, "repoId": repo_id}, {"_id": 0}
        )
        if existing_contributor:
            existing_contributor = Contributor(**existing_contributor)
            Contributors.delete_one(
                {"contributorId": existing_contributor.contributorId}
            )
            logger.info(f"Contributor deleted: {existing_contributor.contributorId}")
            return {"result": True}

        raise HTTPException(status_code=404, detail="Contributor not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting contributor: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete contributor")


@router.patch("/repo/{repo_id}/{user_id}/accept")
def accept_invite(
    repo_id: str, user_id: str, user: UserModel = Depends(manager.required)
):
    try:
        existing_contributor = Contributors.find_one(
            {"userId": user_id, "repoId": repo_id}, {"_id": 0}
        )
        if existing_contributor:
            existing_contributor = Contributor(**existing_contributor)
            Contributors.update_one(
                {"userId": existing_contributor.userId, "repoId": repo_id},
                {
                    "$set": {
                        "pending": False,
                        "acceptedAt": datetime.now(UTC),
                        "username": user.username,
                    }
                },
            )
            logger.info(
                f"Contributor accepted invite: {existing_contributor.email} with access level {existing_contributor.accessLevel}. Invited by {existing_contributor.invitedBy}"
            )
            return {"result": True}

        raise HTTPException(status_code=404, detail="Contributor not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting invite: {e}")
        raise HTTPException(status_code=500, detail="Failed to accept invite")


@router.delete("/repo/{repo_id}/{user_id}/invite")
def reject_invite(
    repo_id: str, user_id: str, user: UserModel = Depends(manager.required)
):
    try:
        existing_contributor = Contributors.find_one(
            {"userId": user_id, "repoId": repo_id}, {"_id": 0}
        )
        if existing_contributor:
            existing_contributor = Contributor(**existing_contributor)
            Contributors.delete_one(
                {"userId": existing_contributor.userId, "repoId": repo_id}
            )
            logger.info(
                f"Contributor rejected invite: {existing_contributor.email} with access level {existing_contributor.accessLevel}. Invited by {existing_contributor.invitedBy}"
            )
            return {"result": True}

        raise HTTPException(status_code=404, detail="Contributor not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting invite: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject invite")


@router.get("/repo/{repo_id}/authorization")
def check_authorized(
    repo_id: str, user: Optional[UserModel] = Depends(manager.optional.READ)
):
    try:
        if not user:
            return {"result": None, "invite": False, "inviter": None}

        # first check if user is the resource owner
        repo = Repos.find_one({"repoId": repo_id}, {"_id": 0})
        repo = RepoModel(**repo) if repo else None
        if repo and repo.adminId == user.userId:
            return {"result": "owner", "invite": False, "inviter": None}

        # then check if user is a contributor
        existing_contributor = Contributors.find_one(
            {"repoId": repo_id, "userId": user.userId}, {"_id": 0}
        )

        if existing_contributor:
            existing_contributor = Contributor(**existing_contributor)
            status = "invite" if existing_contributor.pending else "contributor"
            logger.info(
                f"Found authorized {status}: {existing_contributor.email} with access level {existing_contributor.accessLevel}. Invited by {existing_contributor.invitedBy}"
            )
            return {
                "result": existing_contributor.accessLevel,
                "invite": existing_contributor.pending,
                "inviter": existing_contributor.invitedBy,
            }
        # no access found
        return {"result": None, "invite": False, "inviter": None}

    except Exception as e:
        logger.error(f"Error checking authorized: {e}")
        raise HTTPException(status_code=500, detail="Failed to check authorized")
