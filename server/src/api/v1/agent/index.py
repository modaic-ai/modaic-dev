from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from src.models.agent import AgentModel, Agents, PublicAgentModel
from src.lib.logger import logger

router = APIRouter()


@router.get("/user/{username}")
async def get_user_agents(username: str):
    """Get all agents for a specific user"""
    try:
        agents_cursor = Agents.find({"adminId": username})
        agents = []
        
        async for agent_doc in agents_cursor:
            agent = PublicAgentModel(**agent_doc)
            agents.append(agent.model_dump())
        
        return JSONResponse(content=agents)
        
    except Exception as e:
        logger.error(f"Failed to get user agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user agents")


@router.get("/{username}/{agent_name}")
async def get_agent(username: str, agent_name: str):
    """Get specific agent by username and name"""
    try:
        agent_doc = await Agents.find_one({
            "adminId": username, 
            "name": agent_name
        })
        
        if not agent_doc:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent = PublicAgentModel(**agent_doc)
        return JSONResponse(content=agent.model_dump())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch agent")


@router.get("/search")
async def search_agents(
    q: Optional[str] = Query(None, description="Search query"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(20, description="Maximum number of results")
):
    """Search public agents"""
    try:
        # Build search filter
        search_filter = {}
        
        if q:
            # Search in name and description
            search_filter["$or"] = [
                {"name": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}}
            ]
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            search_filter["tags"] = {"$in": tag_list}
        
        # Execute search
        agents_cursor = Agents.find(search_filter).limit(limit)
        agents = []
        
        async for agent_doc in agents_cursor:
            agent = PublicAgentModel(**agent_doc)
            agents.append(agent.model_dump())
        
        # Sort by updated date (most recent first)
        agents.sort(key=lambda x: x.get("updated", ""), reverse=True)
        
        return JSONResponse(content=agents)
        
    except Exception as e:
        logger.error(f"Failed to search agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search agents")


@router.get("/")
async def get_featured_agents(limit: int = Query(12, description="Number of featured agents")):
    """Get featured/popular agents"""
    try:
        # For now, just return most recently updated agents
        # In the future, this could be based on stars, downloads, etc.
        agents_cursor = Agents.find({}).sort("updated", -1).limit(limit)
        agents = []
        
        async for agent_doc in agents_cursor:
            agent = PublicAgentModel(**agent_doc)
            agents.append(agent.model_dump())
        
        return JSONResponse(content=agents)
        
    except Exception as e:
        logger.error(f"Failed to get featured agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch featured agents")