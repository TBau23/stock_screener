import models
import yfinance
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from database import SessionLocal, engine
from pydantic import BaseModel 
from models import Stock
from sqlalchemy.orm import Session

 
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

class StockRequest(BaseModel):
    symbol: str #pydantic handles all the validation for requests

def get_db(): # all endpoints that use database need reference to this function before they execute
    try: 
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.get("/")
def dashboard(request : Request, db: Session = Depends(get_db)):
    """
    displays stock screener dashboard
    """
    stocks = db.query(Stock).all()
    

    return templates.TemplateResponse("dashboard.html", {
        "request" : request,
        "stocks" : stocks
    } )

# run server with uvicorn main:app --reload

def fetch_stock_data(id: int):
    db = SessionLocal()
    stock = db.query(Stock).filter(Stock.id == id).first()

    yahoo_data = yfinance.Ticker(stock.symbol)
    print(yahoo_data.info)

    stock.ma200 = yahoo_data.info['twoHundredDayAverage']
    stock.ma50 = yahoo_data.info['fiftyDayAverage']
    stock.price = yahoo_data.info['previousClose']
    stock.forward_pe = yahoo_data.info['forwardPE']
    stock.forward_eps = yahoo_data.info['forwardEps']

    if yahoo_data.info['dividendYield'] is not None:
        stock.dividend_yield = yahoo_data.info['dividendYield'] * 100
    
    db.add(stock)
    db.commit()

@app.post("/stock")
async def create_stock(stock_request : StockRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)): # depends must be at end
    """
    creates stock and stores it in database
    """
    stock = models.Stock()
    stock.symbol = stock_request.symbol
    db.add(stock)
    db.commit()

    background_tasks.add_task(fetch_stock_data, stock.id) 


    return {
        "status" : "success",
        "message" : "stock created"
    }