from src.models.user_model import UserModel #, UrlUsageModel
from src.models.file_model import FileModel
from src.schemas.users_schema import UserCreate, HTTPError
from src.schemas.files_schema import FileBase
from .base import RepositoryDBUsers, RepositoryDBFiles


class RepositoryUsers(RepositoryDBUsers[UserModel, UserCreate]):#, HTTPError]):
    pass


class RepositoryFiles(RepositoryDBFiles[FileModel, FileBase, UserModel]):#, HTTPError]):
    pass


users_crud = RepositoryUsers(UserModel)#, HTTPError)
files_crud = RepositoryFiles(FileModel, FileBase)

