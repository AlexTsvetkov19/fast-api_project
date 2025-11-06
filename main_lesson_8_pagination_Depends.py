import uvicorn
from fastapi import FastAPI, Depends
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.testing.schema import mapped_column
from sqlalchemy import select


app = FastAPI()
engine = create_async_engine('sqlite+aiosqlite:///books.db')

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

class Base(DeclarativeBase):
    pass

class BookModel(Base):
    __tablename__ = 'books'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author: Mapped[str]

class BookAddSchema(BaseModel):
    title: str
    author: str

class BookSchema(BookAddSchema):
    id: int

class PaginationParams(BaseModel):
    limit: int = Field(5, ge=0, le=100, description="Кол-во элементов на странице")
    offset: int = Field(0, ge=0, description="Смещение для пагинации")

PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]

@app.post("/setup_database")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    return {"success": True}


@app.post("/books")
async def add_book(data: BookAddSchema, session: SessionDep):
    new_book = BookModel(title=data.title, author=data.author)
    session.add(new_book)
    await session.commit()
    return {"success": True}

@app.get("/books")
async def get_books(session: SessionDep, pagination: PaginationDep) -> list[BookSchema]:
    query = (
        select(BookModel)
        .limit(pagination.limit)
        .offset(pagination.offset)
    )
    result = await session.execute(query)
    return result.scalars().all()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000,reload=True)

