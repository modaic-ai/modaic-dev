from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from typing import Dict, Any
import json
import hmac
import hashlib
from src.core.config import settings
from src.lib.logger import logger
from src.service.agent import AgentService
from src.lib.gittea import gitea_client

router = APIRouter()


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify Gitea webhook signature"""
    if not signature.startswith("sha256="):
        return False

    expected_signature = hmac.new(
        secret.encode("utf-8"), payload, hashlib.sha256
    ).hexdigest()

    received_signature = signature[7:]  # Remove 'sha256=' prefix
    return hmac.compare_digest(expected_signature, received_signature)


@router.post("/gitea/push")
async def handle_gitea_push(request: Request, background_tasks: BackgroundTasks):
    """Handle Gitea push webhooks"""
    try:
        # Get raw payload and signature
        payload = await request.body()
        signature = request.headers.get("X-Gitea-Signature")

        if not signature:
            raise HTTPException(status_code=400, detail="Missing signature")

        # Verify webhook signature
        if not verify_webhook_signature(
            payload, signature, settings.gittea_webhook_secret
        ):
            raise HTTPException(status_code=403, detail="Invalid signature")

        # Parse webhook payload
        webhook_data = json.loads(payload.decode("utf-8"))

        # Extract repository information
        repo_info = webhook_data.get("repository", {})
        repo_owner = repo_info.get("owner", {}).get("login")
        repo_name = repo_info.get("name")

        if not repo_owner or not repo_name:
            raise HTTPException(
                status_code=400, detail="Missing repository information"
            )

        # Process push event in background
        background_tasks.add_task(
            process_push_event, repo_owner, repo_name, webhook_data
        )

        logger.info(f"Received push webhook for {repo_owner}/{repo_name}")
        return {"status": "success", "message": "Webhook processed"}

    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


@router.post("/gitea/repository")
async def handle_gitea_repository(request: Request, background_tasks: BackgroundTasks):
    """Handle Gitea repository events (create/delete)"""
    try:
        # Get raw payload and signature
        payload = await request.body()
        signature = request.headers.get("X-Gitea-Signature")

        if not signature:
            raise HTTPException(status_code=400, detail="Missing signature")

        # Verify webhook signature
        if not verify_webhook_signature(
            payload, signature, settings.gittea_webhook_secret
        ):
            raise HTTPException(status_code=403, detail="Invalid signature")

        # Parse webhook payload
        webhook_data = json.loads(payload.decode("utf-8"))

        action = webhook_data.get("action")
        repo_info = webhook_data.get("repository", {})

        logger.info(f"Received repository webhook: {action}")

        # Process repository event in background
        background_tasks.add_task(process_repository_event, action, repo_info)

        return {"status": "success", "message": "Repository webhook processed"}

    except Exception as e:
        logger.error(f"Repository webhook processing failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Repository webhook processing failed"
        )


async def process_push_event(
    repo_owner: str, repo_name: str, webhook_data: Dict[str, Any]
):
    """Process push event in background"""
    try:
        agent_service = AgentService()

        # Update agent mirror and metadata
        await agent_service.update_agent_from_push(repo_owner, repo_name, webhook_data)

        logger.info(f"Successfully processed push event for {repo_owner}/{repo_name}")

    except Exception as e:
        logger.error(
            f"Failed to process push event for {repo_owner}/{repo_name}: {str(e)}"
        )


async def process_repository_event(action: str, repo_info: Dict[str, Any]):
    """Process repository event in background"""
    try:
        if action == "created":
            # Handle new repository creation
            logger.info(f"New repository created: {repo_info.get('full_name')}")

        elif action == "deleted":
            # Handle repository deletion
            repo_name = repo_info.get("name")
            repo_owner = repo_info.get("owner", {}).get("login")

            if repo_name and repo_owner:
                agent_service = AgentService()
                await agent_service.delete_agent_mirror(repo_owner, repo_name)
                logger.info(f"Repository deleted: {repo_owner}/{repo_name}")

    except Exception as e:
        logger.error(f"Failed to process repository event: {str(e)}")
