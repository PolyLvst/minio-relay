from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from config.minio_client import MinioClient
from model.database_model import Upload
from service.auth import GoogleOAuthService
from service.frontend import FrontendService
from sqlalchemy.orm import Session
from config.connection import get_db
from math import ceil

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/login")
    # picture = user.get("picture")
    picture = None
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
    # picture = user.get("picture")
    picture = None
    email = user.get("email")
    name = user.get("name")
    return templates.TemplateResponse("upload.html", {"request": request, "picture":picture, "email":email, "name":name})



@router.post("/upload", response_class=HTMLResponse)
def upload_file(request: Request, file: UploadFile = File(...), uploader: str = Form(...), db: Session = Depends(get_db)):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/login")
    # picture = user.get("picture")
    picture = None
    email = user.get("email")
    name = user.get("name")
    bucket_name = MinioClient.bucket_name
    is_success = FrontendService.upload(db=db, bucket_name=bucket_name, file=file, uploader=uploader, email=email)
    return templates.TemplateResponse("index.html", {"request": request, "is_success": is_success, "picture":picture, "email":email, "name":name})

@router.get("/data-upload-list", response_class=HTMLResponse)
def get_data_upload_list(
    request: Request,
    db: Session = Depends(get_db),
    page: int = 1,
    per_page: int = 5,
):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login")

    total = db.query(Upload).count()
    uploads = (
        db.query(Upload)
        .order_by(Upload.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    # rows
    rows_html = ""
    for item in uploads:
        rows_html += f"""
        <tr class="border-b border-gray-200 hover:bg-gray-100" id="row-{item.id}">
            <td class="py-3 px-6 text-left whitespace-nowrap">
                <a href="/download/file-id/{item.id}" class="text-blue-500 hover:underline">{item.filename}</a>
            </td>
            <td class="py-3 px-6 text-left">{item.uploader}</td>
            <td class="py-3 px-6 text-left">{FrontendService.convert_utc_to_jakarta(item.created_at).strftime("%Y-%m-%d %H:%M")}</td>
            <td class="py-3 px-6 text-left">
                <button 
                    class="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded"
                    hx-confirm="Are you sure?"
                    hx-delete="/delete-upload/{item.id}"
                    hx-target="#row-{item.id}"
                    hx-swap="outerHTML"
                >
                    Delete
                </button>
            </td>
        </tr>
        """

    # pagination
    total_pages = ceil(total / per_page)
    pagination_html = '<div id="pagination-controls" class="flex justify-center mt-4 space-x-2" hx-swap-oob="true">'
    if page > 1:
        pagination_html += f"""
        <button 
            hx-get="/data-upload-list?page={page-1}&per_page={per_page}"
            hx-target="#upload-tbody"
            hx-swap="innerHTML"
            class="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
        >Prev</button>
        """
    pagination_html += f"<span class='px-3 py-1'>{page} / {total_pages}</span>"
    if page < total_pages:
        pagination_html += f"""
        <button 
            hx-get="/data-upload-list?page={page+1}&per_page={per_page}"
            hx-target="#upload-tbody"
            hx-swap="innerHTML"
            class="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
        >Next</button>
        """
    pagination_html += "</div>"

    return HTMLResponse(rows_html + pagination_html)

@router.get("/download/file-id/{file_id}")
def download_file_by_id(request: Request, file_id:int, db: Session = Depends(get_db)):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/login")
    bucket_name = MinioClient.bucket_name
    expire_seconds = 43200 # 12 Hour
    generated_url = FrontendService.download(db=db, bucket_name=bucket_name, expire_seconds=expire_seconds, file_id=file_id)
    return RedirectResponse(url=generated_url)

@router.delete("/delete-upload/{file_id}")
def delete_upload(request: Request, file_id: int, db: Session = Depends(get_db)):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url="/login")
    bucket_name = MinioClient.bucket_name
    FrontendService.delete(db=db, bucket_name=bucket_name, file_id=file_id)
    # Respond with empty string so row is removed
    return HTMLResponse("")


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
