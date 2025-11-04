from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from customer.models import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_if_not_exists(self, data: dict) -> User:
        """Добавляет пользователя, если его нет в базе по crm_id."""
        crm_id = data.get("crm_id")
        if not crm_id:
            raise ValueError("crm_id не может быть пустым")

        existing_user = await self.session.scalar(
            select(User).where(User.crm_id == crm_id)
        )
        if existing_user:
            return existing_user

        user = User(**data)
        self.session.add(user)
        await self.session.commit()
        return user
