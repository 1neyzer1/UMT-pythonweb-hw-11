from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactBase(BaseModel):
    first_name: str = Field(..., max_length=120)
    last_name: str = Field(..., max_length=120)
    email: EmailStr
    phone: str = Field(..., max_length=64)
    birthday: date
    extra_data: str | None = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=120)
    last_name: str | None = Field(default=None, max_length=120)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=64)
    birthday: date | None = None
    extra_data: str | None = None


class ContactRead(ContactBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
