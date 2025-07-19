from src.service.index import *
from src.models.index import *
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/user/{userId}")
def get_user(userId: str):
    try:
        user = user_service.get_user(GetUserRequest(userId=userId, authorized=True))
        return JSONResponse(content=user.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/user/update/{userId}")
def update_user(userId: str, request: UpdateUserRequest):
    try:
        update_user_request = UpdateUserRequest(userId=userId, **request.model_dump())
        result = user_service.update_user(update_user_request)
        return JSONResponse(content=result.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/user/delete/{userId}")
def delete_user(userId: str):
    try:
        deleted_user_id = user_service.delete_user(DeleteUserRequest(userId=userId))
        return JSONResponse(content={"result": deleted_user_id})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
