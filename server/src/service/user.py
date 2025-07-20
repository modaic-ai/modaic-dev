from src.models.index import *
import uuid
from typing import Union


class UserService:
    def __init__(self):
        pass

    def create_user(self, request: CreateUserRequest) -> UserModel:
        user = UserModel(
            userId=request.userId,
            username=request.username,
            email=request.email,
            created=datetime.now(UTC),
            updated=datetime.now(UTC),
            imageKey=request.imageKey,
        )
        Users.insert_one(user.model_dump())
        return user

    def update_user(self, request: UpdateUserRequest) -> UserModel:
        user = UserModel(
            userId=request.userId,
            username=request.username,
            email=request.email,
            imageKey=request.imageKey,
        )
        Users.update_one(
            {"userId": request.userId}, {"$set": user.model_dump(exclude_none=True)}
        )
        return user

    def delete_user(self, request: DeleteUserRequest) -> str:
        Users.delete_one({"userId": request.userId})
        return request.userId

    def get_user(self, request: GetUserRequest) -> Union[PublicUserModel, UserModel]:
        user = Users.find_one({"userId": request.userId})
        if request.authorized:
            return UserModel(**user)
        return PublicUserModel(**user)


user_service = UserService()
