from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from service.auth import GoogleOAuthService

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/login")
    picture = user.get("picture")
    email = user.get("email")
    name = user.get("name")
    return templates.TemplateResponse("index.html", {"request": request, "picture":picture, "email":email, "name":name})

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/login")
    picture = user.get("picture")
    email = user.get("email")
    name = user.get("name")
    return templates.TemplateResponse("upload.html", {"request": request, "picture":picture, "email":email, "name":name})



@router.get('/logout')
async def logout(request: Request):
    # Clear the user session
    request.session.pop('user', None)
    return RedirectResponse(url="/")

@router.get("/login-google")
async def login_google(request: Request):
    redirect_uri = request.url_for('auth')
    return await GoogleOAuthService.get_authorize_redirect(request, redirect_uri)

@router.get("/auth")
async def auth(request: Request):
    try:
        token = await GoogleOAuthService.oauth.google.authorize_access_token(request)
        user = token.get("userinfo")
        if user:
            request.session['user'] = dict(user)
        return RedirectResponse(url="/")
    except Exception as e:
        print("ERROR:", e)
        print(e.with_traceback())
        raise HTTPException(status_code=400, detail=str(e))
