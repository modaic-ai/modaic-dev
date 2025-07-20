from src.models.repo import CreateRepoRequest
from src.lib.logger import logger
from pydantic import BaseModel
from typing import Optional
from fastapi import BackgroundTasks
from fastapi import APIRouter
from src.api.auth.utils import manager
from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from src.core.config import settings
from src.models.index import (
    Users,
    UserModel,
    PublicUserModel,
    CreateUserRequest,
    UpdateUserRequest,
)
from src.utils.user import generate_username
from src.service.index import email_service, user_service, repo_service
from src.lib.stytch import client as stytch_client, StytchError

router = APIRouter()


class RegisterRequest(BaseModel):
    email: str  # better pydantic types needed
    password: str
    username: str
    fullName: Optional[str] = None
    stytchUserId: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class CompleteAuthenticationRequest(BaseModel):
    stytchUserId: str
    email: str
    firstName: str
    lastName: str
    profilePictureUrl: str


@router.post("/authenticate")
def authenticate(
    auth_request: CompleteAuthenticationRequest,
    background_tasks: BackgroundTasks,
):
    try:
        # extract and validate required fields
        email = auth_request.email
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        userId = auth_request.stytchUserId
        if not userId:
            raise HTTPException(status_code=400, detail="Stytch user ID is required")

        first_name = auth_request.firstName or ""
        last_name = auth_request.lastName or ""
        profile_picture_url = auth_request.profilePictureUrl or ""

        # find existing user
        user_doc = Users.find_one({"email": email}, {"_id": 0})
        user = UserModel(**user_doc) if user_doc else None
        username = generate_username(email) if not user else user.username

        new_repo_id = None

        if not user:
            # create a new user
            create_user_data = CreateUserRequest(
                userId=userId,
                username=username,
                email=email,
                fullName=f"{first_name} {last_name}".strip(),
                profilePictureUrl=profile_picture_url,
            )

            created_user = user_service.create_user(request=create_user_data)
            if not created_user:
                raise HTTPException(status_code=500, detail="Failed to create user")

            # create welcome repo for new user
            create_repo_data = CreateRepoRequest(
                name="Welcome to Modaic!",
                description="This is your first repo! Create a new repo to get started.",
                visibility="Private",
                adminId=userId,
            )

            created_repo = repo_service.create_repo(request=create_repo_data)
            if not created_repo:
                raise HTTPException(
                    status_code=500, detail="Failed to create default repo"
                )

            new_repo_id = created_repo.repoId

            # send onboarding message in the background when we make modaic business gmail
            """
            background_tasks.add_task(
                email_service.onboarding_message,
                recipient_email=auth_request.email,
                recipient_name=auth_request.firstName or username,
            )
            """
        else:
            # use existing user's username
            username = user.username

        # build redirect URL
        if new_repo_id:
            redirect = "/auth/onboarding"
            params = f"?firstName={first_name}&lastName={last_name}&username={username}&isGoogleSignup=true&defaultRepoId={new_repo_id}"
        else:
            redirect = f"/{username}"
            params = "?src=oauth"

        full_redirect_url = f"{settings.next_url}{redirect}{params}"

        return JSONResponse(content={"redirect": full_redirect_url, "success": True})

    except HTTPException:
        # re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/register")
def register(registerRequest: RegisterRequest, background_tasks: BackgroundTasks):
    """
    Register a new user in the system.

    This endpoint creates a new user in both Stytch and the local MongoDB database,
    and creates their default repo.

    Args:
        registerRequest: The request payload containing the user's information.
        background_tasks: The background tasks to run after the user is registered.

    Returns:
        A JSONResponse with the user's id and web id.

    Raises:
        HTTPException: If the user could not be registered.
    """
    try:
        # validate required fields
        if not registerRequest.username:
            raise HTTPException(status_code=400, detail="Username is required")
        if not registerRequest.email:
            raise HTTPException(status_code=400, detail="Email is required")
        if not registerRequest.stytchUserId:
            raise HTTPException(status_code=400, detail="Stytch user ID is required")

        # check for username collision
        usernameCollision = Users.find_one({"username": registerRequest.username})
        if usernameCollision:
            logger.error(f"Username already exists: {registerRequest.username}")
            raise HTTPException(
                status_code=400,
                detail="Username already exists",
            )

        # check for email collision
        emailCollision = Users.find_one({"email": registerRequest.email})
        if emailCollision:
            logger.error(f"Email already exists: {registerRequest.email}")
            raise HTTPException(
                status_code=400,
                detail="Email already exists",
            )

        userId = registerRequest.stytchUserId

        # create the user in mongo
        createUserPayload = CreateUserRequest(
            userId=userId,
            username=registerRequest.username,
            email=registerRequest.email,
            fullName=registerRequest.fullName,
        )

        created_user = user_service.create_user(request=createUserPayload)
        if not created_user:
            raise HTTPException(status_code=500, detail="Failed to create user")

        # create their default repo
        createRepoPayload = CreateRepoRequest(
            name="Welcome to Modaic!",
            description="This is your first repo! Create a new repo to get started.",
            visibility="Private",
            adminId=userId,
        )

        repoId = None
        try:
            repo = repo_service.create_repo(request=createRepoPayload)
            repoId = repo.repoId
            if not repoId:
                logger.error("create_repo returned None or falsy value")
                raise HTTPException(
                    status_code=500, detail="Failed to create default web"
                )

            # send account creation email in the background
            background_tasks.add_task(
                email_service.account_creation,
                recipient_email=registerRequest.email,
                recipient_name=registerRequest.fullName or registerRequest.username,
            )
        except Exception as e:
            logger.error(f"Error creating default web: {str(e)}")
            # If web creation fails, we should still return success for user creation
            # but log the error for investigation

        response_content = {
            "message": "Welcome to Modaic!",
            "userId": userId,
            "username": registerRequest.username,
            "email": registerRequest.email,
        }

        # Only include repoId if it was successfully created
        if repoId:
            response_content["repoId"] = repoId

        return JSONResponse(content=response_content)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in register endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me")
def get_current_user(user: Optional[UserModel] = Depends(manager.optional)):
    """
    Get the current user.

    :return: The current user
    """

    if not user:
        return None

    try:
        public_user = PublicUserModel(**user.model_dump())
        logger.debug(f"User found in /auth/me: {public_user.model_dump()}")
        return public_user.model_dump()

    except Exception as e:
        logger.error(f"Exception in /auth/me: {e}")
        return None


class OnboardingPayload(BaseModel):
    firstName: str
    lastName: Optional[str] = ""
    username: str
    bio: Optional[str] = ""
    occupation: str
    company: Optional[str] = ""
    purpose: str
    interest: Optional[str] = ""


@router.post("/onboarding")
def complete_onboarding(
    onboarding_payload: OnboardingPayload, user: UserModel = Depends(manager.required)
):
    logger.info(f"user: {user}")
    try:

        logger.info(f"onboarding_payload: {onboarding_payload}")
        updates = UpdateUserRequest(
            userId=user.userId,
            fullName=f"{onboarding_payload.firstName} {onboarding_payload.lastName}",
            username=onboarding_payload.username,
        )

        logger.info(f"updates: {updates}")
        Users.update_one(
            {"userId": user.userId},
            {"$set": updates.model_dump(exclude_none=True)},
        )
        return {"result": True}
    except Exception as e:
        logger.error(f"Exception in /auth/me: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/logout")
def logout(request: Request):
    """
    Log out the current user.

    This endpoint clears the authentication cookie, effectively logger out the user.

    Args:
        response (Response): The response object to set the cookie.
        user (User): The user making the request, obtained from the dependency.

    Returns:
        dict: A JSON response with a message indicating successful logout.
    """
    session_token = request.cookies.get("stytch_session")
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        resp = stytch_client.sessions.revoke(session_token=session_token)
        logger.info(f"Logout response: {resp}")
    except StytchError as e:
        raise HTTPException(status_code=400, detail=str(e))

    resp = JSONResponse(content={"message": "Successfully logged out"})
    resp.delete_cookie("stytch_session", path="/")
    resp.delete_cookie("stytch_session_jwt", path="/")
    return resp
