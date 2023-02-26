from pydantic import BaseModel, EmailStr, Field
from datetime import date


class ContactModel(BaseModel):
    first_name: str = Field("John", min_length=1, max_length=25)
    last_name: str = Field("Cena", min_length=1, max_length=40)
    email: EmailStr
    phone: int = Field("777", gt=100, le=999999999)
    birthday: date


class ResponseContact(ContactModel):
    id: int = 1
    first_name: str
    last_name: str
    email: EmailStr
    phone: int
    birthday: date

    class Config:
        orm_mode = True
