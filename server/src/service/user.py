from src.models.index import *
from src.lib.gittea import gitea_client
from src.lib.logger import logger
from src.utils.date import now
import secrets
from typing import Union


class UserService:
    def __init__(self):
        pass

    def create_user(self, request: CreateUserRequest) -> UserModel:
        try:
            # Create Gitea user account
            gitea_user = gitea_client.create_user(
                username=request.username,
                email=request.email,
                full_name=request.fullName or "",
            )

            # Create API access token for the user
            gitea_token = gitea_client.create_access_token(request.username)

            # Generate API key for SDK access
            api_key = self._generate_api_key()

            user = UserModel(
                userId=request.userId,
                username=request.username,
                email=request.email,
                created=now(),
                updated=now(),
                imageKey=request.imageKey,
                fullName=request.fullName,
                profilePictureUrl=request.profilePictureUrl,
                giteaUserId=gitea_user.get("id"),
                giteaTokenEncrypted=self._encrypt_token(gitea_token.get("sha1", "")),
                apiKey=api_key,
            )
            Users.insert_one(user.model_dump())
            logger.info(f"Created user with Gitea account: {request.username}")
            return user

        except Exception as e:
            logger.error(f"Failed to create user with Gitea account: {str(e)}")
            # Fallback: create user without Gitea integration
            user = UserModel(
                userId=request.userId,
                username=request.username,
                email=request.email,
                created=now(),
                updated=now(),
                imageKey=request.imageKey,
                fullName=request.fullName,
                profilePictureUrl=request.profilePictureUrl,
                apiKey=self._generate_api_key(),
            )
            Users.insert_one(user.model_dump())
            return user

    def _generate_api_key(self) -> str:
        """Generate secure API key for SDK access"""
        return f"modaic_{secrets.token_urlsafe(32)}"

    def _encrypt_token(self, token: str) -> str:
        """Encrypt Gitea token for storage - placeholder implementation"""
        # TODO: Implement proper encryption using your preferred method
        # For now, just storing as-is (not secure for production)
        return token

    def update_user(self, request: UpdateUserRequest) -> UserModel:
        updates = request.model_dump(exclude_none=True)
        Users.update_one(
            {"userId": request.userId}, {"$set": updates}
        )
        return UserModel(**Users.find_one({"userId": request.userId}))

    def delete_user(self, request: DeleteUserRequest) -> str:
        Users.delete_one({"userId": request.userId})
        return request.userId

    def get_user(self, request: GetUserRequest) -> Union[PublicUserModel, UserModel]:
        user = Users.find_one({"userId": request.userId})
        if request.authorized:
            return UserModel(**user)
        return PublicUserModel(**user)

    def regenerate_api_key(self, user_id: str) -> str:
        """Regenerate API key for user"""
        new_api_key = self._generate_api_key()
        Users.update_one(
            {"userId": user_id},
            {"$set": {"apiKey": new_api_key, "updated": datetime.now(UTC)}},
        )
        logger.info(f"Regenerated API key for user: {user_id}")
        return new_api_key

    def email_exists(self, email: str) -> bool:
        """Check if a user exists with the given email"""
        user = Users.find_one({"email": email})
        return user is not None


user_service = UserService()
