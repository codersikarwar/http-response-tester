from fastapi import FastAPI, HTTPException, Request, Query, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.openapi.utils import get_openapi
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
            "content_type": response.headers.get("content-type"),
            "final_url": response.url #added to show final url
        }
        return info

    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

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

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="URL HTTPS Info API",
        version="1.0.0",
        description="API to get HTTPS information for a given URL.",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
