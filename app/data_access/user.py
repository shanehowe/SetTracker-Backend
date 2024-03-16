from .base import BaseDataAccess
from app.models.user_models import UserInDB


class UserDataAccess(BaseDataAccess):
    def __init__(self) -> None:
        super().__init__(container_name="users")

    def get_user(self, user_id: str):
        return self.container.read_item(item=user_id, partition_key=user_id)

    def create_user(self, user: UserInDB) -> dict:
        created_user = self.container.create_item(body=user.model_dump())
        return created_user

    def update_user(self, user: UserInDB) -> dict:
        updated_user = self.container.upsert_item(body=user.model_dump())
        return updated_user

    def delete_user(self, user_id: str) -> None:
        self.container.delete_item(item=user_id, partition_key=user_id)
