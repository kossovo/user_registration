from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.repository.users import create_new_user
from db.session import get_db
from schemas.users import UserCreate
from webapp.users.user_forms import UserCreateForm

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/register")
def register(request: Request):
    return templates.TemplateResponse(
        name="users/register.html", context={"request": request}
    )


@router.post("/register")  # Same name, but this is a post resquest
async def register(request: Request, db: Session = Depends(get_db)):
    form = UserCreateForm(request=request)
    await form.load_data()

    if await form.is_valid():
        user = UserCreate(
            email=form.email,
            password=form.password,
        )
        try:
            create_new_user(user=user, db=db)
            return RedirectResponse(
                url="/?msg=Verification-email-send", status_code=status.HTTP_302_FOUND
            )
        except IntegrityError:
            form.__dict__.get("errors").append("Duplicated user")
            return templates.TemplateResponse(
                name="users/register.html", context=form.__dict__
            )
    return templates.TemplateResponse(name="users/register.html", context=form.__dict__)
