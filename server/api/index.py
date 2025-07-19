from server.service.index import user_service
from server.models.index import *
from server.api.core.config import settings
from fastapi import Depends, APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/{userId}")
def root(userId: str):
    user = user_service.get_user(GetUserRequest(userId=userId, authorized=True))
    return JSONResponse(content=user)

@router.post("/create")
def create_user(request: CreateUserRequest):
    return JSONResponse(content=user_service.create_user(request))

@router.put("/update")
def update_user(request: UpdateUserRequest):
    return JSONResponse(content=user_service.update_user(request))

@router.delete("/delete")
def delete_user(request: DeleteUserRequest):
    return JSONResponse(content=user_service.delete_user(request))


