from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI()

templates = Jinja2Templates(directory="templates")  # Create a "templates" directory

def get_https_info(url):
    try:
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()

        info = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "url": response.url,
            "history": [r.url for r in response.history],
            "content_length": len(response.content),
            "encoding": response.encoding,
            "cookies": response.cookies.get_dict(),
            "elapsed": response.elapsed.total_seconds(),
            "reason": response.reason,
            "content_type": response.headers.get("content-type")
        }
        return info

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.get("/info", response_class=HTMLResponse)
async def get_url_info(request: Request, url: str):
    try:
        result = get_https_info(url)
        return templates.TemplateResponse("index.html", {"request": request, "result": result})

    except HTTPException as e:
        return templates.TemplateResponse("index.html", {"request": request, "error": e.detail})
