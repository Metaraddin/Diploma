from fastapi import APIRouter, Cookie
from fastapi.responses import RedirectResponse, HTMLResponse, Response
from fastapi.security import HTTPBearer
from src.models.token import Token
from typing import Optional

router = APIRouter(prefix="/auth_anilist", tags=["Anilist Auth"])
security = HTTPBearer()


@router.get("/", response_class=RedirectResponse)
async def redirect():
    return 'https://anilist.co/api/v2/oauth/authorize?client_id=7698&response_type=token'


@router.get('/callback')
async def read_token():
    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <script>
                let post = JSON.stringify({ "access_token": window.location.hash });
                const url = "/auth_anilist/token";
                let xhr = new XMLHttpRequest();
                xhr.open('POST', url, true);
                xhr.setRequestHeader('Content-type', 'application/json; charset=UTF-8');
                xhr.onreadystatechange = function() {
                    if(xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200) {
                        document.write(window.location.hash);
                    }
                }
                xhr.send(post);
            </script>
        </head>
        <body>
        </body>
    </html>
    """
    return HTMLResponse(html)


@router.post('/token')
async def save_token(token: Token, response: Response):
    access_token = token.access_token.split('=')[1].split('&')[0]
    response.set_cookie(key='anilist_access_token', value=access_token, httponly=True)
    return {"anilist_access_token": access_token}


@router.get('/token')
async def read_token(anilist_access_token: Optional[str] = Cookie(None)):
    return {'anilist_access_token': anilist_access_token}

