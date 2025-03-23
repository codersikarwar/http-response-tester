from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI()

templates = Jinja2Templates(directory="templates")

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
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/url", response_class=JSONResponse)
async def get_url_info_api(url: str = Query(..., description="The URL to fetch HTTPS information from")):
    try:
        result = get_https_info(url)
        return JSONResponse(content=result)

    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
