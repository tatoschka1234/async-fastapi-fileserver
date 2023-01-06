from src.models.user_model import UserModel
from src.models.file_model import FileModel
from src.schemas.users_schema import UserCreate
from src.schemas.files_schema import FileBase
from .base import RepositoryDBUsers, RepositoryDBFiles


class RepositoryUsers(RepositoryDBUsers[UserModel, UserCreate]):
    pass


class RepositoryFiles(RepositoryDBFiles[FileModel, FileBase, UserModel]):
    pass


users_crud = RepositoryUsers(UserModel)
files_crud = RepositoryFiles(FileModel, FileBase)
