import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRead
from app.services.auth import get_current_user

router = APIRouter()

cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)


@router.get(
    "/me",
    response_model=UserRead,
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/avatar", response_model=UserRead)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    r = cloudinary.uploader.upload(
        file.file,
        public_id=f"ContactsApp/{current_user.id}",
        overwrite=True,
    )
    src_url = cloudinary.CloudinaryImage(f"ContactsApp/{current_user.id}").build_url(
        width=250, height=250, crop="fill", version=r.get("version")
    )
    current_user.avatar = src_url
    db.commit()
    db.refresh(current_user)
    return current_user
