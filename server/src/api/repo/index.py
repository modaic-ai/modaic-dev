from src.service.index import *
from src.models.index import *
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()
