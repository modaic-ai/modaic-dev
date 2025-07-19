from server.models.index import *
import uuid
from typing import Union


class RepoService:
    def __init__(self):
        pass

    def create_repo(self, request: CreateRepoRequest):
        repo = RepoModel(
            repoId=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            adminId=request.adminId,
            visibility=request.visibility,
        )
        Repos.insert_one(repo.model_dump())
        return repo

    def update_repo(self, request: UpdateRepoRequest):
        repo = RepoModel(
            repoId=request.repoId,
            name=request.name,
            description=request.description,
            adminId=request.adminId,
            visibility=request.visibility,
        )
        Repos.update_one(
            {"repoId": request.repoId}, {"$set": repo.model_dump(exclude_none=True)}
        )  # leave exclude_none=True to not update fields that are None
        return repo

    def delete_repo(self, request: DeleteRepoRequest):
        Repos.delete_one({"repoId": request.repoId})
        return request.repoId

    def get_repo(self, request: GetRepoRequest) -> Union[PublicRepoModel, RepoModel]:
        repo = Repos.find_one({"repoId": request.repoId})
        if request.authorized:
            return RepoModel(**repo)
        return PublicRepoModel(**repo)


repo_service = RepoService()
