from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'

engine = create_async_engine("sqlite+aiosqlite:///./coffee_shop.db", echo=True)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with async_session_maker() as session:
        yield session

#TODO реализовать бд и обновление клиентов и чеков раз в день 
