from src.service.index import *
from src.models.index import *
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from src.api.v1.auth.utils import manager
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/{userId}")
def get_user(userId: str):
    try:
        user = user_service.get_user(GetUserRequest(userId=userId, authorized=True))
        return JSONResponse(content=user.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{userId}")
def update_user(
    userId: str, request: UpdateUserRequest, user: UserModel = Depends(manager.required)
):
    try:
        update_user_request = UpdateUserRequest(userId=userId, **request.model_dump())
        result = user_service.update_user(update_user_request)
        return JSONResponse(content=result.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{userId}")
def delete_user(userId: str, user: UserModel = Depends(manager.required)):
    try:
        deleted_user_id = user_service.delete_user(DeleteUserRequest(userId=userId))
        return JSONResponse(content={"result": deleted_user_id})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me/api-key")
def get_api_key(user: UserModel = Depends(manager.required)):
    """Get user's API key for SDK access"""
    try:
        if not user.apiKey:
            raise HTTPException(status_code=404, detail="API key not found")

        return JSONResponse(content={"apiKey": user.apiKey, "username": user.username})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/me/api-key/regenerate")
def regenerate_api_key(user: UserModel = Depends(manager.required)):
    """Regenerate user's API key"""
    try:
        new_api_key = user_service.regenerate_api_key(user.userId)
        return JSONResponse(
            content={
                "apiKey": new_api_key,
                "message": "API key regenerated successfully",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/check/email/")
def check_email(email: str):
    """Check if a user exists with the given email"""
    try:
        exists = user_service.email_exists(email)
        return {"exists": exists}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
