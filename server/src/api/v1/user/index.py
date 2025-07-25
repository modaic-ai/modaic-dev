from src.objects.schemas.user import PublicUserSchema
from src.service.index import *
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from src.api.v1.auth.utils import manager
from fastapi.responses import JSONResponse
from src.objects.index import (
    User,
    UserSchema,
    UpdateUserRequest,
)
from src.db.pg import get_db
from sqlalchemy.orm import Session
from src.lib.logger import logger

router = APIRouter()


@router.get("/{userId}")
def get_user_by_id(userId: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.userId == userId).first()
        if not user:
            logger.error(f"User not found: {userId}")
            raise HTTPException(status_code=404, detail="User not found")

        user = PublicUserSchema.model_validate(user)
        logger.info(f"User found by id: {user}")
        return JSONResponse(content=user.model_dump())

    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/username/{username}")
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            logger.error(f"User not found: {username}")
            raise HTTPException(status_code=404, detail="User not found")

        user = PublicUserSchema.model_validate(user)
        logger.info(f"User found by username: {user}")
        return JSONResponse(content=user.model_dump())

    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{userId}")
def update_user(
    userId: str,
    request: UpdateUserRequest,
    user: UserSchema = Depends(manager.required),
    db: Session = Depends(get_db),
):
    """Update a user in the database"""
    authorized = user.userId == userId
    if not authorized:
        logger.error(f"Unauthorized: {user.userId} is not authorized to update {userId}")
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        result = (
            db.query(User)
            .filter(User.userId == userId)
            .update(request.model_dump(exclude_none=True))
        )
        db.commit()
        logger.info(f"Users updated:{result}")

        return JSONResponse(content=result)
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{userId}")
def delete_user(
    userId: str,
    user: UserSchema = Depends(manager.required),
    db: Session = Depends(get_db),
):
    authorized = user.userId == userId
    if not authorized:
        logger.error(f"Unauthorized: {user.userId} is not authorized to delete {userId}")
        raise HTTPException(status_code=403, detail="Unauthorized")
    try:

        db.query(User).filter(User.userId == userId).delete()
        db.commit()
        logger.info(f"User deleted: {userId}")
        return JSONResponse(content={"result": userId})

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me/api-key")
def get_api_key(user: UserSchema = Depends(manager.required)):
    """Get user's API key for SDK access"""
    try:
        logger.info(f"User: {user}")
        if not user.apiKey:
            logger.error("API key not found")
            raise HTTPException(status_code=404, detail="API key not found")

        return JSONResponse(content={"apiKey": user.apiKey, "username": user.username})

    except Exception as e:
        logger.error(f"Error getting API key: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/me/api-key/regenerate")
def regenerate_api_key(
    user: UserSchema = Depends(manager.required), db: Session = Depends(get_db)
):
    """Regenerate user's API key"""
    try:
        new_api_key = user_service._generate_api_key()
        db.query(User).filter(User.userId == user.userId).update(
            {"apiKey": new_api_key}
        )
        db.commit()
        logger.info(f"API key regenerated for user: {user.userId}")
        return JSONResponse(
            content={
                "apiKey": new_api_key,
                "message": "API key regenerated successfully",
            }
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error regenerating API key: {str(e)}. Database was rolled back!")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/check/email/")
def check_email(email: str, db: Session = Depends(get_db)):
    """Check if a user exists with the given email"""
    try:
        user = db.query(User).filter(User.email == email).first()
        logger.info(f"User exists: {user is not None}")
        return JSONResponse(content={"exists": user is not None})
    except Exception as e:
        logger.error(f"Error checking email: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
