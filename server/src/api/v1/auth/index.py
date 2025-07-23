from src.lib.logger import logger
from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter
from src.api.v1.auth.utils import manager
from fastapi import Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from src.core.config import settings
from src.objects.index import (
    User,
    UserSchema,
    PublicUserSchema,
    CreateUserRequest,
    UpdateUserRequest,
)
from src.db.pg import get_db
from sqlalchemy.orm import Session
from src.utils.user import generate_username
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


@router.post("/")
def authenticate(
    auth_request: CompleteAuthenticationRequest,
    db: Session = Depends(get_db),
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
        user = db.query(User).filter(User.email == email).first()
        if user:
            username = user.username
        else:
            username = generate_username(email, db)

        if not user:
            # create a new user
            create_user_data = CreateUserRequest(
                username=username,
                email=email,
                fullName=f"{first_name} {last_name}".strip(),
                profilePictureUrl=profile_picture_url,
            )

            user_to_create = User(
                userId=userId,
                username=create_user_data.username,
                email=create_user_data.email,
                fullName=create_user_data.fullName,
                profilePictureUrl=create_user_data.profilePictureUrl,
                created=create_user_data.created,
                updated=create_user_data.updated,
            )

            db.add(user_to_create)
            db.commit()
            db.refresh(user_to_create)

            if not user_to_create:
                raise HTTPException(status_code=500, detail="Failed to create user")

        else:
            # use existing user's username
            username = user.username

        # build redirect URL
        redirect = f"/agents"
        params = "?src=oauth"

        full_redirect_url = f"{settings.next_url}{redirect}{params}"

        return JSONResponse(content={"redirect": full_redirect_url, "success": True})

    except Exception as e:
        db.rollback()
        logger.error(f"Authentication error: {str(e)}. Database was rolled back!")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/register")
def register(registerRequest: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user in the system.

    This endpoint creates a new user in both Stytch and the local PostgreSQL database,
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
        usernameCollision = (
            db.query(User).filter(User.username == registerRequest.username).first()
        )
        if usernameCollision:
            logger.error(f"Username already exists: {registerRequest.username}")
            raise HTTPException(
                status_code=400,
                detail="Username already exists",
            )

        # check for email collision
        emailCollision = (
            db.query(User).filter(User.email == registerRequest.email).first()
        )
        if emailCollision:
            logger.error(f"Email already exists: {registerRequest.email}")
            raise HTTPException(
                status_code=400,
                detail="Email already exists",
            )

        userId = registerRequest.stytchUserId

        # create the user in postgres
        create_user_request = CreateUserRequest(
            username=registerRequest.username,
            email=registerRequest.email,
            fullName=registerRequest.fullName,
        )

        user_to_create = User(
            userId=userId,
            username=create_user_request.username,
            email=create_user_request.email,
            fullName=create_user_request.fullName,
            created=create_user_request.created,
            updated=create_user_request.updated,
        )

        db.add(user_to_create)
        db.commit()
        db.refresh(user_to_create)

        if not user_to_create:
            logger.error("Failed to create user")
            raise HTTPException(status_code=500, detail="Failed to create user")

        response = {
            "message": "Welcome to Modaic!",
            "userId": userId,
            "username": registerRequest.username,
            "email": registerRequest.email,
        }

        return JSONResponse(content=response)

    except Exception as e:
        db.rollback()
        logger.error(
            f"Unexpected error in register endpoint: {str(e)}. Database was rolled back!"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me")
def get_current_user(user: Optional[UserSchema] = Depends(manager.optional)):
    """
    Get the current user.

    :return: The current user
    """

    if not user:
        return None

    try:
        public_user = PublicUserSchema(**user.model_dump())
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
    onboarding_payload: OnboardingPayload,
    user: UserSchema = Depends(manager.required),
    db: Session = Depends(get_db),
):
    logger.info(f"user: {user}")
    try:

        logger.info(f"onboarding_payload: {onboarding_payload}")
        updates = UpdateUserRequest(
            userId=user.userId,
            fullName=f"{onboarding_payload.firstName} {onboarding_payload.lastName}",
            username=onboarding_payload.username,
        )

        result = (
            db.query(User)
            .filter(User.userId == user.userId)
            .update(updates.model_dump(exclude_none=True))
        )
        if result == 0:
            raise HTTPException(status_code=404, detail="User not found")

        db.commit()

        return {"result": result}

    except Exception as e:
        db.rollback()
        logger.error(f"Exception in /auth/me: {e}. Database was rolled back!")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/session")
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
