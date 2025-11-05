from __future__ import annotations
import uvicorn
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel, EmailStr, Field, ConfigDict

app = FastAPI()

books = [
    {
        "id": 1,
        "title": "Асинхронность в Python",
        "author": "Alexey",
    },
    {
        "id": 2,
        "title": "Backend разработка в Python",
        "author": "Alex",
    },
]

users = []

@app.get(
    "/books",
    summary="Получить все книги",
    tags=["Книги 📚"])
async def read_books():
    return books

@app.get(
    "/books/{id}",
    summary="Получить книгу",
    tags=["Книги 📚"])
async def get_book(id: int):
    for book in books:
        if book["id"] == id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")

class NewBook(BaseModel):
    title: str
    author: str

class UserSchema(BaseModel):
    email: EmailStr
    bio: str = Field(max_length=10)
    age: int = Field(gt=0, le=130)

    model_config = ConfigDict(extra='forbid')

@app.post(
    "/users",
    tags=["Пользователи 👨‍👨"])
async def create_user(user: UserSchema):
    users.append(user)
    return {"success": True, "message": "User created"}

@app.get(
    "/users",
    tags=["Пользователи 👨‍👨"])
async def get_users() -> list[UserSchema]:
    return users

@app.post(
    "/books",
    tags=["Книги 📚"])
async def create_book(new_book: NewBook):
    books.append({
        "id": len(books) + 1,
        "title": new_book.title,
        "author": new_book.author,
    })
    return {"success": True, "message": "Книга успешно добавлена"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000,reload=True)

