import requests
import secrets
import json
from typing import Optional, Dict, Any, List
from src.core.config import settings
from src.lib.logger import logger


class GitteaClient:
    def __init__(self):
        self.base_url = settings.gittea_url
        self.admin_token = settings.gittea_admin_token
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"token {self.admin_token}",
                "Content-Type": "application/json",
            }
        )

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated request to Gitea API"""
        url = f"{self.base_url}/api/v1{endpoint}"

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Gitea API request failed: {e}")
            raise

    def create_user(
        self, username: str, email: str, full_name: str = ""
    ) -> Dict[str, Any]:
        """Create Gitea user account"""
        password = secrets.token_urlsafe(32)

        user_data = {
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name or username,
            "must_change_password": False,
            "send_notify": False,
        }

        logger.info(f"Creating Gitea user: {username}")
        return self._make_request("POST", "/admin/users", json=user_data)

    def create_repo(
        self, owner: str, repo_name: str, description: str = "", private: bool = False
    ) -> Dict[str, Any]:
        """Create repository for agent"""
        repo_data = {
            "name": repo_name,
            "description": description,
            "private": private,
            "auto_init": True,
            "readme": "Default",
            "license": "MIT",
        }

        logger.info(f"Creating repository: {owner}/{repo_name}")

        # Use user's token if available, otherwise admin creates it
        endpoint = f"/user/repos"
        return self._make_request("POST", endpoint, json=repo_data)

    def create_access_token(
        self, username: str, token_name: str = "modaic-api"
    ) -> Dict[str, Any]:
        """Generate API token for user"""
        token_data = {
            "name": f"{token_name}-{secrets.token_hex(8)}",
            "scopes": ["write:repository", "read:user"],
        }

        logger.info(f"Creating access token for user: {username}")
        return self._make_request("POST", f"/users/{username}/tokens", json=token_data)

    def setup_webhook(self, owner: str, repo: str, webhook_url: str) -> Dict[str, Any]:
        """Set up push webhooks"""
        webhook_data = {
            "type": "gitea",
            "config": {
                "url": webhook_url,
                "content_type": "json",
                "secret": settings.gittea_webhook_secret,
            },
            "events": ["push", "repository"],
            "active": True,
        }

        logger.info(f"Setting up webhook for {owner}/{repo}")
        return self._make_request(
            "POST", f"/repos/{owner}/{repo}/hooks", json=webhook_data
        )

    def get_repo_contents(
        self, owner: str, repo: str, filepath: str, ref: str = "main"
    ) -> Optional[Dict[str, Any]]:
        """Get file contents from repository"""
        try:
            return self._make_request(
                "GET", f"/repos/{owner}/{repo}/contents/{filepath}?ref={ref}"
            )
        except requests.exceptions.RequestException:
            logger.warning(f"File not found: {owner}/{repo}/{filepath}")
            return None

    def get_user_repos(self, username: str) -> List[Dict[str, Any]]:
        """Get user's repositories"""
        try:
            return self._make_request("GET", f"/users/{username}/repos")
        except requests.exceptions.RequestException:
            return []

    def delete_repo(self, owner: str, repo: str) -> bool:
        """Delete repository"""
        try:
            self._make_request("DELETE", f"/repos/{owner}/{repo}")
            logger.info(f"Deleted repository: {owner}/{repo}")
            return True
        except requests.exceptions.RequestException:
            return False

    def get_repo_info(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Get repository information"""
        try:
            return self._make_request("GET", f"/repos/{owner}/{repo}")
        except requests.exceptions.RequestException:
            return None


# Global client instance
gitea_client = GitteaClient()
