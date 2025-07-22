import base64
import yaml
from typing import Dict, Any, Optional
from src.objects.index import AgentSchema, Agent, RepoSchema
from src.lib.gittea import gitea_client
from src.lib.logger import logger
from src.utils.date import now
import uuid


class AgentService:

    def __init__(self):
        pass
