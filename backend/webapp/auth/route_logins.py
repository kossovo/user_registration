from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from backend.api.v1.route_auth import login_for_access_token
from backend.db.session import get_db
from backend.webapp.auth.auth_forms import LoginForm

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login")
def login(request: Request):
    return templates.TemplateResponse(
        name="auth/login.html", context={"request": request}
    )


@router.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    form = LoginForm(request=request)
    await form.load_data()

    if await form.is_valid():
        try:
            form.__dict__.update(msg="Login Successfully")
            response = templates.TemplateResponse(
                name="auth/login.html", context=form.__dict__
            )
            await login_for_access_token(response=response, form_data=form, db=db)
            return response

        except HTTPException:
            form.__dict__.update(msg="")  # Remove success message
            form.__dict__.get("errors").append("Incorrect user email or password")
            return templates.TemplateResponse(
                name="auth/login.html", context=form.__dict__
            )

    form.__dict__.get("errors").append("Incorrect user email or password")
    return templates.TemplateResponse(name="auth/login.html", context=form.__dict__)
