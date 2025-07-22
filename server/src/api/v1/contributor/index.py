from typing import Literal, Optional
from fastapi import APIRouter, HTTPException, Depends
from src.objects.index import (
    UserSchema,
    User,
    PublicUserSchema,
    ContributorSchema,
    Contributor,
    RepoSchema,
    Repo,
)
from src.api.v1.auth.utils import manager
from src.lib.logger import logger
from pydantic import BaseModel
from datetime import datetime
from pytz import UTC
import uuid
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from src.db.pg import get_db

router = APIRouter()


class InviteContributer(BaseModel):
    emailToInvite: str


@router.post("/repo/{repo_id}")
def invite_contributer(
    repo_id: str,
    payload: InviteContributer,
    background_tasks: BackgroundTasks,
    sender: UserSchema = Depends(manager.required.ADMIN),
    db: Session = Depends(get_db),
):
    try:
        invite_email = payload.emailToInvite

        if sender.email == invite_email:
            raise HTTPException(status_code=400, detail="You cannot invite yourself")

        # check for existing contributor relationship
        existing_relationship = (
            db.query(Contributor)
            .filter(
                Contributor.email == invite_email,
                Contributor.repoId == repo_id,
            )
            .first()
        )

        if existing_relationship:
            existing_contrib = ContributorSchema(**existing_relationship)
            if existing_contrib.pending:
                raise HTTPException(
                    status_code=400, detail="Invitation already sent to this email"
                )
            raise HTTPException(
                status_code=400, detail="User already has access to this project"
            )

        # check if user already exists
        existing_user = db.query(User).filter(User.email == invite_email).first()

        if existing_user:
            logger.info(f"User found: {existing_user}")

            # check if user is already a contributor
            if (
                db.query(Contributor)
                .filter(
                    Contributor.userId == existing_user.userId,
                    Contributor.repoId == repo_id,
                )
                .first()
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

            db.add(contributor_info)
            db.commit()
            db.refresh(contributor_info)
            logger.info(f"Contributor invited: {contributor_info.contributorId}")

            # send email to user
            repo = db.query(Repo).filter(Repo.repoId == repo_id).first()
            if not repo:
                raise HTTPException(status_code=404, detail="Repo not found")
            repo = RepoSchema(**repo)

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
            return {"result": PublicUserSchema(**existing_user.model_dump())}

        elif not existing_user:
            logger.info(f"User not found in database: {invite_email}...")
            raise HTTPException(status_code=404, detail="User not found")
            # TODO: send email to user to create an account and invite them to the project

    except Exception as e:
        logger.error(f"Error inviting contributor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/repo/{repo_id}/{contributor_id}/invite")
def revoke_invite(
    repo_id: str,
    contributor_id: str,
    _: UserSchema = Depends(manager.required.ADMIN),
    db: Session = Depends(get_db),
):
    try:
        existing_contributor = (
            db.query(Contributor)
            .filter(
                Contributor.contributorId == contributor_id,
                Contributor.repoId == repo_id,
            )
            .first()
        )
        if existing_contributor:
            db.delete(existing_contributor)
            db.commit()
            logger.info(
                f"Contributor revoked invite: {existing_contributor.email} with access level {existing_contributor.accessLevel}. Invited by {existing_contributor.invitedBy}"
            )
            return {"result": True}

        raise HTTPException(status_code=404, detail="Contributor not found")

    except Exception as e:
        db.rollback()
        logger.error(f"Error revoking invite: {e}. Database was rolled back!")
        raise HTTPException(status_code=500, detail="Failed to revoke invite")


@router.get("/repo/{repo_id}")
def get_all_contributors_for_repo(
    repo_id: str,
    _: UserSchema = Depends(manager.optional.READ),
    db: Session = Depends(get_db),
):
    try:
        contributors = db.query(Contributor).filter(Contributor.repoId == repo_id).all()
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
    _: UserSchema = Depends(manager.required.ADMIN),
    db: Session = Depends(get_db),
):
    try:
        existing_contributor = (
            db.query(Contributor)
            .filter(
                Contributor.contributorId == contributor_id,
                Contributor.repoId == repo_id,
            )
            .first()
        )
        if existing_contributor:
            existing_contributor = Contributor(**existing_contributor)
            db.query(Contributor).filter(
                Contributor.contributorId == contributor_id,
                Contributor.repoId == repo_id,
            ).update({"accessLevel": payload.role})
            logger.info(
                f"Contributor role toggled: {existing_contributor.contributorId}"
            )
            return {"result": True}

        raise HTTPException(status_code=404, detail="Contributor not found")

    except Exception as e:
        db.rollback()
        logger.error(f"Error toggling contributor role: {e}. Database was rolled back!")
        raise HTTPException(status_code=500, detail="Failed to toggle contributor role")


@router.delete("/repo/{repo_id}/{contributor_id}")
def delete_contributor(
    repo_id: str,
    contributor_id: str,
    _: UserSchema = Depends(manager.required.ADMIN),
    db: Session = Depends(get_db),
):
    try:
        existing_contributor = (
            db.query(Contributor)
            .filter(
                Contributor.contributorId == contributor_id,
                Contributor.repoId == repo_id,
            )
            .first()
        )
        if existing_contributor:
            existing_contributor = Contributor(**existing_contributor)
            db.delete(existing_contributor)
            db.commit()
            logger.info(f"Contributor deleted: {existing_contributor.contributorId}")
            return {"result": True}

    except Exception as e:
        logger.error(f"Error deleting contributor: {e}. Database was rolled back!")
        raise HTTPException(status_code=500, detail="Failed to delete contributor")


@router.patch("/repo/{repo_id}/{user_id}/accept")
def accept_invite(
    repo_id: str,
    user_id: str,
    user: UserSchema = Depends(manager.required),
    db: Session = Depends(get_db),
):
    try:

        existing_contributor = (
            db.query(Contributor)
            .filter(
                Contributor.userId == user_id,
                Contributor.repoId == repo_id,
            )
            .first()
        )
        if existing_contributor:
            existing_contributor = Contributor(**existing_contributor)
            db.query(Contributor).filter(
                Contributor.userId == user_id,
                Contributor.repoId == repo_id,
            ).update(
                {
                    "pending": False,
                    "acceptedAt": datetime.now(UTC),
                    "username": user.username,
                }
            )
            db.commit()
            logger.info(
                f"Contributor accepted invite: {existing_contributor.email} with access level {existing_contributor.accessLevel}. Invited by {existing_contributor.invitedBy}"
            )
            return {"result": True}

    except Exception as e:
        db.rollback()
        logger.error(f"Error accepting invite: {e}. Database was rolled back!")
        raise HTTPException(status_code=500, detail="Failed to accept invite")


@router.delete("/repo/{repo_id}/{user_id}/invite")
def reject_invite(
    repo_id: str,
    user_id: str,
    user: UserSchema = Depends(manager.required),
    db: Session = Depends(get_db),
):
    try:
        existing_contributor = (
            db.query(Contributor)
            .filter(
                Contributor.userId == user_id,
                Contributor.repoId == repo_id,
            )
            .first()
        )
        if existing_contributor:
            existing_contributor = Contributor(**existing_contributor)
            db.delete(existing_contributor)
            db.commit()
            logger.info(
                f"Contributor rejected invite: {existing_contributor.email} with access level {existing_contributor.accessLevel}. Invited by {existing_contributor.invitedBy}"
            )
            return {"result": True}
    except Exception as e:
        db.rollback()
        logger.error(f"Error rejecting invite: {e}. Database was rolled back!")
        raise HTTPException(status_code=500, detail="Failed to reject invite")


@router.get("/repo/{repo_id}/authorization")
def check_authorized(
    repo_id: str,
    user: Optional[UserSchema] = Depends(manager.optional.READ),
    db: Session = Depends(get_db),
):
    try:
        if not user:
            return {"result": None, "invite": False, "inviter": None}

        # first check if user is the resource owner
        repo = db.query(Repo).filter(Repo.repoId == repo_id).first()
        repo = RepoSchema(**repo) if repo else None
        if repo and repo.adminId == user.userId:
            return {"result": "owner", "invite": False, "inviter": None}

        # then check if user is a contributor
        existing_contributor = (
            db.query(Contributor)
            .filter(Contributor.repoId == repo_id, Contributor.userId == user.userId)
            .first()
        )

        if existing_contributor:
            existing_contributor = ContributorSchema(**existing_contributor)
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
