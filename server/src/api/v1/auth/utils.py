from typing import Optional, Tuple, Callable
from fastapi import HTTPException, Cookie, Header, Depends
from enum import Enum
from src.lib.stytch import client as stytch_client, StytchError, StytchUser
from src.lib.logger import logger
from src.objects.index import (
    UserSchema,
    User,
    AgentSchema,
    Agent,
    ContributorSchema,
    Contributor,
)
from src.db.pg import get_db
from sqlalchemy.orm import Session


# --- Authentication Error ---
class AuthenticationError(Exception):
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# --- Token Extraction ---
class TokenExtractor:
    @staticmethod
    def extract_bearer_token(authorization: Optional[str]) -> Optional[Tuple[str, str]]:
        if not authorization:
            return None
        parts = authorization.split()
        if len(parts) != 2 or parts[0] != "Bearer":
            raise AuthenticationError(
                "Invalid Authorization header format. Expected 'Bearer <token>'."
            )
        return parts[1], "Bearer token"

    @staticmethod
    def extract_cookie_token(
        stytch_session_jwt: Optional[str],
    ) -> Optional[Tuple[str, str]]:
        if not stytch_session_jwt:
            return None
        return stytch_session_jwt, "Cookie (stytch_session_jwt)"


# --- Stytch Auth ---
class StytchAuthenticator:
    @staticmethod
    def authenticate_bearer_token(token: str) -> StytchUser:
        resp = stytch_client.idp.introspect_access_token_local(access_token=token)
        stytch_user = stytch_client.users.get(user_id=resp.subject)
        if not stytch_user:
            raise AuthenticationError(
                "UserModel not found in Stytch after authentication"
            )
        return stytch_user

    @staticmethod
    def authenticate_session_jwt(token: str) -> StytchUser:
        resp = stytch_client.sessions.authenticate(session_jwt=token)
        return resp.user


class UserRepository:
    @staticmethod
    def find_user_by_stytch_data(stytch_user: StytchUser, db: Session) -> UserSchema:
        try:
            user_id = stytch_user.user_id
            user = db.query(User).filter(User.userId == user_id).first()
            if not user:
                raise AuthenticationError(
                    "UserModel not found in local system after authentication"
                )
            return UserSchema.model_validate(user)
        except Exception as e:
            db.rollback()
            raise e


class AccessLevel(str, Enum):
    ADMIN = "admin"
    READ = "read"
    WRITE = "write"


class AuthService:
    def __init__(self):
        self.token_extractor = TokenExtractor()
        self.stytch_auth = StytchAuthenticator()
        self.user_repo = UserRepository()

    def _authenticate_token(
        self, token: str, auth_method: str, is_bearer: bool, db: Session
    ) -> UserSchema:
        try:
            stytch_user = (
                self.stytch_auth.authenticate_bearer_token(token)
                if is_bearer
                else self.stytch_auth.authenticate_session_jwt(token)
            )
            user = self.user_repo.find_user_by_stytch_data(stytch_user, db)
            logger.info(
                f"Authenticated user_id: {stytch_user.user_id} via {auth_method}"
            )
            return user
        except StytchError as e:
            logger.warning(f"Stytch authentication error: {e}")
            detail = f"Authentication failed: {getattr(e, 'details', str(e))}"
            raise AuthenticationError(detail)

    def authenticate_user(
        self,
        authorization: Optional[str] = None,
        stytch_session_jwt: Optional[str] = None,
        db: Session = None,
    ) -> UserSchema:
        bearer_result = self.token_extractor.extract_bearer_token(authorization)
        if bearer_result:
            token, auth_method = bearer_result
            return self._authenticate_token(token, auth_method, is_bearer=True, db=db)
        cookie_result = self.token_extractor.extract_cookie_token(stytch_session_jwt)
        if cookie_result:
            token, auth_method = cookie_result
            return self._authenticate_token(token, auth_method, is_bearer=False, db=db)
        raise AuthenticationError(
            f"Not authenticated: Missing token: {authorization}, {stytch_session_jwt}"
        )

    def check_agent_access(
        self,
        user: Optional[UserSchema],
        agent_id: str,
        required_level: AccessLevel,
        db_session: Session,
    ):
        agent = db_session.query(Agent).filter(Agent.agentId == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent = AgentSchema(**agent)
        # admin has all access levels
        if user and agent.adminId == user.userId:
            return

        # for public agents, everyone gets read access
        if agent.visibility == "Public" and required_level == AccessLevel.READ:
            return

        if not user:
            raise HTTPException(status_code=403, detail="Not authorized")

        # for all other cases (private agents or write/admin access), check contributor status
        contributor = (
            db_session.query(Contributor)
            .filter(
                Contributor.agentId == agent_id,
                Contributor.userId == user.userId,
            )
            .first()
        )
        if not contributor:
            raise HTTPException(status_code=403, detail="Not authorized")
        contributor = ContributorSchema(**contributor)
        contributor_level = contributor.accessLevel

        # check access level hierarchy
        if required_level == AccessLevel.ADMIN:
            # need ADMIN access
            if contributor_level != AccessLevel.ADMIN:
                raise HTTPException(status_code=403, detail="Admin access required")
        elif required_level == AccessLevel.WRITE:
            # need WRITE or ADMIN access
            if contributor_level not in [AccessLevel.WRITE, AccessLevel.ADMIN]:
                raise HTTPException(status_code=403, detail="Write access required")
        elif required_level == AccessLevel.READ:
            # any access level (READ, WRITE, ADMIN) grants READ access
            if contributor_level not in [
                AccessLevel.READ,
                AccessLevel.WRITE,
                AccessLevel.ADMIN,
            ]:
                raise HTTPException(status_code=403, detail="Read access required")


auth_service = AuthService()


# --- FastAPI Dependencies ---
async def get_current_user_from_token(
    authorization: Optional[str] = Header(None),
    stytch_session_jwt: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
) -> UserSchema:
    try:
        return auth_service.authenticate_user(authorization, stytch_session_jwt, db)
    except AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


async def get_optional_user_from_token(
    authorization: Optional[str] = Header(None),
    stytch_session_jwt: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
) -> Optional[UserSchema]:
    try:
        return auth_service.authenticate_user(authorization, stytch_session_jwt, db)
    except AuthenticationError as e:
        if e.status_code == 401:
            logger.info(f"Optional authentication failed: {e.message}")
            return None
        raise HTTPException(status_code=e.status_code, detail=e.message)


# --- Dependency Factory ---
def require_agent_access_level(required_level: AccessLevel) -> Callable:
    async def dependency(
        agent_id: str,
        user: Optional[UserSchema] = Depends(get_current_user_from_token),
        db: Session = Depends(get_db),
    ) -> Optional[UserSchema]:
        auth_service.check_agent_access(user, agent_id, required_level, db)
        return user

    return dependency


# --- NEW: Optional Agent Access Factory ---
def optional_agent_access_level(required_level: AccessLevel) -> Callable:
    async def dependency(
        agent_id: str,
        user: Optional[UserSchema] = Depends(get_optional_user_from_token),
        db: Session = Depends(get_db),
    ) -> Optional[UserSchema]:
        auth_service.check_agent_access(user, agent_id, required_level, db)
        return user

    return dependency


# --- Manager Class with .required.READ / .WRITE ---
class AuthManager:
    def __init__(self):
        self.required = self.Required()
        self.optional = self.Optional()
        logger.info("AUTH MANAGER INITIALIZED")

    class Required:
        def __init__(self):
            # these are now direct dependency functions, not callable classes
            self.READ = require_agent_access_level(AccessLevel.READ)
            self.WRITE = require_agent_access_level(AccessLevel.WRITE)
            self.ADMIN = require_agent_access_level(AccessLevel.ADMIN)

        async def __call__(
            self,
            authorization: Optional[str] = Header(None),
            stytch_session_jwt: Optional[str] = Cookie(None),
            db: Session = Depends(get_db),
        ) -> UserSchema:
            """
            For basic authentication without repo access check.
            Usage: Depends(manager.required)
            """
            try:
                return auth_service.authenticate_user(
                    authorization, stytch_session_jwt, db
                )
            except AuthenticationError as e:
                raise HTTPException(status_code=e.status_code, detail=e.message)

    class Optional:
        def __init__(self):
            # use the new optional agent access factory
            self.READ = optional_agent_access_level(AccessLevel.READ)

        async def __call__(
            self,
            authorization: Optional[str] = Header(None),
            stytch_session_jwt: Optional[str] = Cookie(None),
            db: Session = Depends(get_db),
        ) -> Optional[UserSchema]:
            return await get_optional_user_from_token(
                authorization, stytch_session_jwt, db
            )


manager = AuthManager()
