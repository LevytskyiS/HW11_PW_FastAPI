import time

from typing import List
from fastapi import FastAPI, Depends, HTTPException, Path, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date, timedelta

from connect_db import get_db, Contact
from api_models import ContactModel, ResponseContact

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["Process-Time"] = str(process_time)
    return response


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )


@app.get("/", name="Info page")
def info():
    return {"message": "Welcome to Address Book"}


@app.post(
    "/contacts/create",
    response_model=ResponseContact,
    name="Create contact",
    tags=["contacts"],
)
async def create_contact(body: ContactModel, db: Session = Depends(get_db)):
    contact = Contact(**body.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@app.get(
    "/contacts",
    response_model=List[ResponseContact],
    name="All contacts",
    tags=["contacts"],
)
async def get_contacts(db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    return contacts


@app.get(
    "/contacts/{contact_id}",
    response_model=ResponseContact,
    name="Get contact",
    tags=["contacts"],
)
async def get_contact_by_id(
    contact_id: int = Path(1, ge=1), db: Session = Depends(get_db)
):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return contact


@app.put(
    "/contacts/update/{contact_id}",
    response_model=ResponseContact,
    name="Change contact",
    tags=["contacts"],
)
async def update_contact(
    body: ContactModel,
    contact_id: int = Path(1, ge=1),
    db: Session = Depends(get_db),
):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.email = body.email
    contact.phone = body.phone
    contact.birthday = body.birthday

    db.commit()
    return contact


@app.delete(
    "/contacts/delete/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="Delete contact",
    tags=["contacts"],
)
async def delete_contact(
    contact_id: int = Path(1, ge=1), db: Session = Depends(get_db)
):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    db.delete(contact)
    db.commit()


@app.get(
    "/contacts/search_first_name/{inquiry}",
    response_model=List[ResponseContact],
    name="Search by first name",
    tags=["search"],
)
async def search_first_name(
    inquiry: str = Path(min_length=1), db: Session = Depends(get_db)
):
    contacts = db.query(Contact).filter_by(first_name=inquiry).all()

    if bool(contacts) == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return contacts


@app.get(
    "/contacts/search_last_name/{inquiry}",
    response_model=List[ResponseContact],
    name="Search by last name",
    tags=["search"],
)
async def search_last_name(
    inquiry: str = Path(min_length=1), db: Session = Depends(get_db)
):
    contacts = db.query(Contact).filter_by(last_name=inquiry).all()

    if bool(contacts) == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return contacts


@app.get(
    "/contacts/search_mail/{inquiry}",
    response_model=List[ResponseContact],
    name="Search by email",
    tags=["search"],
)
async def search_email(
    inquiry: str = Path(min_length=1), db: Session = Depends(get_db)
):
    contacts = db.query(Contact).filter_by(email=inquiry).all()

    if bool(contacts) == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return contacts


@app.get(
    "/bdays",
    response_model=List[ResponseContact],
    name="Bdays in the next 7 days",
    tags=["search"],
)
async def show_bdays(db: Session = Depends(get_db)):
    current_date = date.today()
    delta = timedelta(days=7)
    contacts = db.query(Contact).all()

    bdays_in_next_days = [
        contact for contact in contacts if contact.birthday - current_date <= delta
    ]

    if bdays_in_next_days == False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return bdays_in_next_days
