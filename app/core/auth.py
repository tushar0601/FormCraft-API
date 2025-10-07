from uuid import UUID
from pydantic import BaseModel


class UserData(BaseModel):
    id: UUID
    name: str
    email: str


def get_current_user() -> UserData:
    return UserData(
        id=UUID("38be2da0-f04a-403c-bba8-2e803ff49cf1"),
        name="Tushar",
        email="tusharjan6@gmail.com",
    )
