from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate
from app.services.auth import get_current_user

router = APIRouter()


def _date_for_month_day(year: int, month: int, day: int) -> date:
    try:
        return date(year, month, day)
    except ValueError:
        return date(year, month, 28)


def next_birthday_on_or_after(birthday: date, ref: date) -> date:
    """Next occurrence of birthday's month/day on or after ref (handles Feb 29)."""
    m, d = birthday.month, birthday.day
    for y in (ref.year, ref.year + 1):
        cand = _date_for_month_day(y, m, d)
        if cand >= ref:
            return cand
    return _date_for_month_day(ref.year + 2, m, d)


@router.post("", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
def create_contact(
    payload: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contact = Contact(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=str(payload.email),
        phone=payload.phone,
        birthday=payload.birthday,
        extra_data=payload.extra_data,
        owner_id=current_user.id,
    )
    db.add(contact)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact with this email already exists.",
        )
    db.refresh(contact)
    return contact


@router.get(
    "/birthdays/upcoming",
    response_model=list[ContactRead],
    summary="Contacts with birthday in the next 7 days",
)
def list_upcoming_birthdays(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Returns contacts whose next birthday (month/day, ignoring birth year) falls on
    any calendar day from today through today + 7 days inclusive.
    """
    today = date.today()
    end = today + timedelta(days=7)
    all_contacts = db.scalars(select(Contact).where(Contact.owner_id == current_user.id)).all()
    result: list[Contact] = []
    for c in all_contacts:
        nxt = next_birthday_on_or_after(c.birthday, today)
        if today <= nxt <= end:
            result.append(c)
    result.sort(key=lambda x: next_birthday_on_or_after(x.birthday, today))
    return result


@router.get("", response_model=list[ContactRead])
def list_contacts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    first_name: str | None = Query(None, description="Filter by first name (partial, case-insensitive)"),
    last_name: str | None = Query(None, description="Filter by last name (partial, case-insensitive)"),
    email: str | None = Query(None, description="Filter by email (partial, case-insensitive)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    stmt = select(Contact).where(Contact.owner_id == current_user.id).order_by(Contact.id)
    if first_name is not None and first_name != "":
        stmt = stmt.where(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name is not None and last_name != "":
        stmt = stmt.where(Contact.last_name.ilike(f"%{last_name}%"))
    if email is not None and email != "":
        stmt = stmt.where(Contact.email.ilike(f"%{email}%"))
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get("/{contact_id}", response_model=ContactRead)
def get_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contact = db.scalar(
        select(Contact).where(Contact.id == contact_id, Contact.owner_id == current_user.id)
    )
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.patch("/{contact_id}", response_model=ContactRead)
def update_contact(
    contact_id: int,
    payload: ContactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contact = db.scalar(
        select(Contact).where(Contact.id == contact_id, Contact.owner_id == current_user.id)
    )
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    data = payload.model_dump(exclude_unset=True)
    if "email" in data and data["email"] is not None:
        data["email"] = str(data["email"])
    for key, value in data.items():
        setattr(contact, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact with this email already exists.",
        )
    db.refresh(contact)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contact = db.scalar(
        select(Contact).where(Contact.id == contact_id, Contact.owner_id == current_user.id)
    )
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return None
