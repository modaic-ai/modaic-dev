import base64
import yaml
from typing import Dict, Any, Optional
from src.models.agent import AgentModel, Agents
from src.models.repo import RepoModel, Repos
from src.lib.gittea import gitea_client
from src.lib.logger import logger
from datetime import datetime
from pytz import UTC
import uuid


class AgentService:

    async def update_agent_from_push(
        self, repo_owner: str, repo_name: str, webhook_data: Dict[str, Any]
    ) -> bool:
        """Update agent mirror and metadata from push webhook"""
        try:
            # Find the repository in our database
            repo_doc = await Repos.find_one({"name": repo_name, "adminId": repo_owner})
            if not repo_doc:
                logger.warning(
                    f"Repository not found in database: {repo_owner}/{repo_name}"
                )
                return False

            # Convert to Pydantic model
            repo = RepoModel(**repo_doc)

            # Get agent from database or create new one
            agent_doc = await Agents.find_one({"repoId": repo.repoId})

            # Fetch updated files from Gitea
            modaic_config = await self._get_modaic_config(repo_owner, repo_name)
            readme_content = await self._get_readme_content(repo_owner, repo_name)

            if agent_doc:
                # Convert to Pydantic model
                agent = AgentModel(**agent_doc)

                # Update existing agent
                update_data = {
                    "configYaml": modaic_config or {},
                    "readmeContent": readme_content or "",
                    "lastMirrored": datetime.now(UTC),
                }

                # Extract tags and description from config
                if modaic_config:
                    update_data["tags"] = modaic_config.get("tags", [])
                    update_data["description"] = modaic_config.get(
                        "description", agent.description
                    )
                    update_data["version"] = modaic_config.get("version", "1.0.0")

                await Agents.update_one(
                    {"agentId": agent.agentId}, {"$set": update_data}
                )
                logger.info(f"Updated agent: {agent.agentId}")

            else:
                # Create new agent
                agent_data = {
                    "agentId": str(uuid.uuid4()),
                    "repoId": repo.repoId,
                    "name": repo_name,
                    "description": (
                        modaic_config.get("description", "") if modaic_config else ""
                    ),
                    "adminId": repo_owner,
                    "configYaml": modaic_config or {},
                    "readmeContent": readme_content or "",
                    "tags": modaic_config.get("tags", []) if modaic_config else [],
                    "version": (
                        modaic_config.get("version", "1.0.0")
                        if modaic_config
                        else "1.0.0"
                    ),
                    "lastMirrored": datetime.now(UTC),
                    "created": datetime.now(UTC),
                    "updated": datetime.now(UTC),
                }

                await Agents.insert_one(agent_data)
                logger.info(f"Created new agent: {agent_data['agentId']}")

            return True

        except Exception as e:
            logger.error(f"Failed to update agent from push: {str(e)}")
            return False

    async def delete_agent_mirror(self, repo_owner: str, repo_name: str) -> bool:
        """Delete agent mirror when repository is deleted"""
        try:
            # Find and delete the agent
            repo_doc = await Repos.find_one({"name": repo_name, "adminId": repo_owner})
            if repo_doc:
                repo = RepoModel(**repo_doc)
                result = await Agents.delete_many({"repoId": repo.repoId})
                logger.info(
                    f"Deleted {result.deleted_count} agents for repository {repo_owner}/{repo_name}"
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete agent mirror: {str(e)}")
            return False

    async def _get_modaic_config(
        self, repo_owner: str, repo_name: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch and parse modaic.yaml from repository"""
        try:
            content = gitea_client.get_repo_contents(
                repo_owner, repo_name, "modaic.yaml"
            )
            if content and content.get("content"):
                # Decode base64 content
                yaml_content = base64.b64decode(content["content"]).decode("utf-8")
                return yaml.safe_load(yaml_content)
        except Exception as e:
            logger.warning(
                f"Could not fetch modaic.yaml for {repo_owner}/{repo_name}: {str(e)}"
            )

        return None

    async def _get_readme_content(
        self, repo_owner: str, repo_name: str
    ) -> Optional[str]:
        """Fetch README.md content from repository"""
        try:
            content = gitea_client.get_repo_contents(repo_owner, repo_name, "README.md")
            if content and content.get("content"):
                # Decode base64 content
                return base64.b64decode(content["content"]).decode("utf-8")
        except Exception as e:
            logger.warning(
                f"Could not fetch README.md for {repo_owner}/{repo_name}: {str(e)}"
            )

        return None
