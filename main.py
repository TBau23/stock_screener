from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/")
def dashboard(request : Request):
    """
    displays stock screener dashboard
    """
    return templates.TemplateResponse("dashboard.html", {
        "request" : request
    } )


# run server with uvicorn main:app --reload

@app.post("/stock")
def create_stock():
    """
    creates stock and stores it in database
    """
    return {
        "status" : "success",
        "message" : "stock created"
    }