from app.data_access.base import BaseDataAccess
from app.models.user_models import UserInDB


class UserDataAccess(BaseDataAccess):
    def __init__(self) -> None:
        super().__init__(container_name="users")

    def get_user_by_id(self, user_id: str):
        return self.container.read_item(item=user_id, partition_key=user_id)

    def get_user_by_email(self, email: str) -> UserInDB | None:
        query = "SELECT * FROM users u WHERE u.email = @email"
        params = [dict(name="@email", value=email)]
        users = list(self.container.query_items(
            query=query, parameters=params, enable_cross_partition_query=True  # type: ignore
        ))
        if not users:
            return None
        return UserInDB(**users[0])

    def create_user(self, user: UserInDB) -> UserInDB:
        created_user = self.container.create_item(body=user.model_dump())
        return UserInDB(**created_user)

    def update_user(self, user: UserInDB) -> dict:
        updated_user = self.container.upsert_item(body=user.model_dump())
        return updated_user

    def delete_user(self, user_id: str) -> None:
        self.container.delete_item(item=user_id, partition_key=user_id)
