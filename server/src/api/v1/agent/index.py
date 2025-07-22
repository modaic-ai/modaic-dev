from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from src.objects.index import (
    Agent,
    PublicAgentSchema,
    User,
    UserSchema,
)
from sqlalchemy import or_, desc
from typing import List
from src.lib.logger import logger
from src.db.pg import get_db

router = APIRouter()


@router.get("/user/{username}", response_model=List[PublicAgentSchema])
def get_user_agents(username: str, db: Session = Depends(get_db)):
    """Get all agents for a specific user"""
    try:

        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user = UserSchema(**user)
        agents = db.query(Agent).filter(Agent.adminId == user.userId).all()
        agents = [PublicAgentSchema(**agent) for agent in agents]

        return JSONResponse(content=agents)

    except Exception as e:
        logger.error(f"Failed to get user agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user agents")


@router.get("/{username}/{agent_name}")
async def get_agent(username: str, agent_name: str, db: Session = Depends(get_db)):
    """Get specific agent by username and name"""
    try:

        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user = UserSchema(**user)
        agent = (
            db.query(Agent)
            .filter(Agent.adminId == user.userId, Agent.name == agent_name)
            .first()
        )
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent = PublicAgentSchema(**agent)
        return JSONResponse(content=agent.model_dump())

    except Exception as e:
        logger.error(f"Failed to get agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch agent")


@router.get("/search")
async def search_agents(
    q: Optional[str] = Query(None, description="Search query"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(20, description="Maximum number of results"),
    db: Session = Depends(get_db),
):
    """Search public agents"""
    try:
        # start with base query for public agents
        # query = db.query(Agent).filter(Agent.visibility == "public")
        query = db.query(Agent)

        # add text search filter
        if q:
            search_term = f"%{q}%"
            query = query.filter(
                or_(Agent.name.ilike(search_term), Agent.description.ilike(search_term))
            )

        # add tag filter
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            # assuming tags is stored as JSON array
            query = query.filter(Agent.tags.op("?|")(tag_list))

        # execute search with ordering and limit
        agents = query.order_by(desc(Agent.updated)).limit(limit).all()

        # convert to public schema
        public_agents = []
        for agent in agents:
            public_agent = PublicAgentSchema(**agent)
            public_agents.append(public_agent.model_dump())

        return JSONResponse(content=public_agents)

    except Exception as e:
        logger.error(f"Failed to search agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search agents")


@router.get("/")
def get_featured_agents(
    limit: int = Query(12, description="Number of featured agents"),
    db: Session = Depends(get_db),
):
    """Get featured/popular agents"""
    try:
        # get most recently updated public agents
        # in the future, this could be based on stars, downloads, etc.
        agents = (
            db.query(Agent)
            # .filter(Agent.visibility == "public")
            .order_by(desc(Agent.updated))
            .limit(limit)
            .all()
        )

        # convert to public schema
        featured_agents = []
        for agent in agents:
            public_agent = PublicAgentSchema(**agent)
            featured_agents.append(public_agent.model_dump())

        return JSONResponse(content=featured_agents)

    except Exception as e:
        logger.error(f"Failed to get featured agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch featured agents")
