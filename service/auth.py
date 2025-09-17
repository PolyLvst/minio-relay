import os
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from dotenv import load_dotenv
load_dotenv()

class GoogleOAuthService:
    oauth = OAuth()
    google = oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid email profile"
        }
    )

    @staticmethod
    async def get_authorize_redirect(request: Request, redirect_uri: str):
        return await GoogleOAuthService.oauth.google.authorize_redirect(request, redirect_uri)