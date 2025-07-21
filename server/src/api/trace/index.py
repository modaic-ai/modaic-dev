from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid
from datetime import datetime
from src.core.config import settings

client = MongoClient(
    host=settings.mongo_url,
    maxPoolSize=50,
    minPoolSize=10,
    connectTimeoutMS=10000,
    socketTimeoutMS=30000,
)
db = client[settings.mongo_database]

# Setup time series collection with metaField='metadata'
def create_timeseries_collection():
    if "traces" not in db.list_collection_names():
        try:
            db.create_collection(
                "traces",
                timeseries={
                    "timeField": "timestamp",
                    "metaField": "metadata",
                    "granularity": "seconds"
                }
            )
        except CollectionInvalid:
            pass

create_timeseries_collection()
collection = db["traces"]
router = APIRouter()

# Request model for traces
class PostTraceRequest(BaseModel):
    repoId: str
    commitHash: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    traces: List[Dict[str, Any]]

@router.post("/add")
def post_trace(trace: PostTraceRequest):
    try:
        # Use repoId+commitHash as trace_id
        trace_id = f"{trace.repoId}:{trace.commitHash}"
        docs = []

        for t in trace.traces:
            docs.append({
                "timestamp": trace.timestamp,
                "metadata": {
                    "trace_id": trace_id,
                    "repoId": trace.repoId,
                    "commitHash": trace.commitHash
                },
                "trace_data": t
            })

        result = collection.insert_many(docs)
        return JSONResponse(content={
            "inserted_count": len(result.inserted_ids),
            "trace_id": trace_id
        })

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
