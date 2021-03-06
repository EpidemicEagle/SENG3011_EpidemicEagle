from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Query, Request, Form
from fastapi.openapi.utils import get_openapi
from typing import List,Optional
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json

app = FastAPI(openapi_url="/api/v2/openapi.json")
# add stylesheet
app.mount("/css", StaticFiles(directory="templates/css"), name="css")
app.mount("/js", StaticFiles(directory="templates/js"), name="js")
app.mount("/images", StaticFiles(directory="templates/images"), name="images")
app.mount("/webfonts", StaticFiles(directory="templates/webfonts"), name="webfonts")


templates = Jinja2Templates(directory="templates")
# Global Constants for regex
date_exact = r"^(\d{4})-(\d\d|xx)-(\d\d|xx) (\d\d|xx):(\d\d|xx):(\d\d|xx)$"
date_range = r"^(\d{4})-(\d\d|xx)-(\d\d|xx) (\ d\d|xx):(\d\d|xx):(\d\d|xx) to (\d{4})-(\d\d|xx)-(\d\d|xx) (\d\d|xx):(\d\d|xx):(\d\d|xx)$"

# Query Parameter Models

class SearchTerms(BaseModel):
    key_terms: str
    location: str
    start_date: str = Query(..., regex=date_exact)
    end_date: str = Query(..., regex=date_exact)
    page_number: Optional[int] = None   
    class Config:
        orm_mode = True

# Singular Models

class Location(BaseModel):
    country: str
    location: str
    class Config:
        orm_mode = True

class SearchResult(BaseModel):
    article_id: int
    url: str
    date_of_publication: str
    headline: str
    class Config:
        orm_mode = True

class Report(BaseModel):
    diseases: List[str]
    syndromes: List[str]
    event_date: str = Query(..., regex=date_range)
    locations: List[Location]
    class Config:
        orm_mode = True

class Article(BaseModel):
    url: str
    date_of_publication: str
    headline: str
    main_text: str
    reports: List[Report]
    class Config:
        orm_mode = True

# Pagination Models

class Pagination(BaseModel):
    num_pages: int
    page_number: int
    class Config:
        orm_mode = True

class ListSearchResult(Pagination):
    results: List[SearchResult]

class ListArticle(Pagination):
    articles: List[Article]

class ListReport(Pagination):
    reports: List[Report]


responses = {
    404: {"description": "Item not found"}
}

## API functions
@app.get("/api/v2/articles", response_model=ListArticle, tags=["v2"])
def list_all_articles_with_params(
    key_terms: str,
    location: str,
    start_date: str = Query(..., regex=date_exact),
    end_date: str = Query(..., regex=date_exact),
    page_number: Optional[int] = None  
):
    """
    Lists all the articles specified within the parameters: start_date to end_date, key_terms and location.
    page_number can be specified to go to the corresponding page.
    """
    return {
        "articles": [],
        "num_pages": 1,
        "page_number": 1
    }

@app.get("/api/v2/articles/{article_id}", response_model=Article, tags=["v2"], responses={**responses})
def finds_article_by_id(article_id : int):
    """
    Lists all the information about an article from given id.
    """
    if article_id > 1000:
       raise HTTPException(status_code=404, detail="Article not found")

    return Article(
        url="sample_url",
        date_of_publication="2018-xx-xx xx:xx:xx",
        headline="sample headline",
        main_text="sample text",
        reports=[Report(diseases=[],
                        syndromes=[],
                        event_date="2018-xx-xx xx:xx:xx to 2018-xx-xx xx:xx:xx",
                        locations=[]
                )]
        )

@app.get("/api/v2/reports", response_model=ListReport, tags=["v2"])
def list_reports(
    key_terms: str,
    location: str,
    start_date: str = Query(..., regex=date_exact),
    end_date: str = Query(..., regex=date_exact),
    page_number: Optional[int] = None  
):
    """
    Lists all the reports specified within the parameters: start_date to end_date, key_terms and location.
    page_number can be specified to go to the corresponding page.
    """
    #    if item_id not in items:
    #    raise HTTPException(status_code=404, detail="Item not found")
    # print(model)


    return {
        "reports": [],
        "num_pages": 1,
        "page_number": 1

    }

@app.get("/api/v2/reports/{report_id}", response_model=Report, tags=["v2"], responses={**responses})
def finds_report_by_id(report_id : int):
    """
    Lists all the information about a report from given id.
    """
    if report_id > 1000:
       raise HTTPException(status_code=404, detail="Report not found")

    # report format has to be sent
    return Report(diseases=[],
                    syndromes=[],
                    event_date="2018-xx-xx xx:xx:xx to 2018-xx-xx xx:xx:xx",
                    locations=[]
                )

@app.get("/api/v2/search", response_model=ListSearchResult, tags=["v2"])
def list_reports(
    key_terms: str,
    location: str,
    start_date: str = Query(..., regex=date_exact),
    end_date: str = Query(..., regex=date_exact),
    page_number: Optional[int] = None  
):
    """
    Lists all the search results specified within the parameters: start_date to end_date, key_terms and location.
    page_number can be specified to go to the corresponding page.
    """
    # check input is valid

    # HARD-CODED RESPONSE

    if "covid" in key_terms.lower() and "sydney" in location.lower():
        return {
            "results": [SearchResult(article_id=1, url="www.promed.com/mail",date_of_publication="2018-12-02", headline="Covid Strikes Sydney")],
            "num_pages": 1,
            "page_number": 1
        }           



    # TODO: GET id, url, date, heading from articles
    # WHERE word in keywords
    # AND location=location
    # OFFSET 10*page_number
    return {
        "results": [],
        "num_pages": 1,
        "page_number": 1
    } 


@app.get("/api/v1/articles", response_model=ListArticle, tags=["v1"])
def list_all_articles_with_params(
    key_terms: str,
    location: str,
    start_date: str = Query(..., regex=date_exact),
    end_date: str = Query(..., regex=date_exact),
    page_number: Optional[int] = None  
):
    """
    Lists all the articles specified within the parameters: start_date to end_date, key_terms and location.
    page_number can be specified to go to the corresponding page.
    """
    return {
        "articles": [],
        "num_pages": 1,
        "page_number": 1
    }

@app.get("/api/v1/articles/{article_id}", response_model=Article, tags=["v1"], responses={**responses})
def finds_article_by_id(article_id : int):
    """
    Lists all the information about an article from given id.
    """
    if article_id > 1000:
       raise HTTPException(status_code=404, detail="Article not found")

    return Article(
        url="sample_url",
        date_of_publication="2018-xx-xx xx:xx:xx",
        headline="sample headline",
        main_text="sample text",
        reports=[Report(diseases=[],
                        syndromes=[],
                        event_date="2018-xx-xx xx:xx:xx to 2018-xx-xx xx:xx:xx",
                        locations=[]
                )]
        )

@app.get("/api/v1/reports", response_model=ListReport, tags=["v1"])
def list_reports(
    key_terms: str,
    location: str,
    start_date: str = Query(..., regex=date_exact),
    end_date: str = Query(..., regex=date_exact),
    page_number: Optional[int] = None  
):
    """
    Lists all the reports specified within the parameters: start_date to end_date, key_terms and location.
    page_number can be specified to go to the corresponding page.
    """
    #    if item_id not in items:
    #    raise HTTPException(status_code=404, detail="Item not found")
    # print(model)


    return {
        "reports": [],
        "num_pages": 1,
        "page_number": 1

    }

@app.get("/api/v1/reports/{report_id}", response_model=Report, tags=["v1"], responses={**responses})
def finds_report_by_id(report_id : int):
    """
    Lists all the information about a report from given id.
    """
    if report_id > 1000:
       raise HTTPException(status_code=404, detail="Report not found")

    # report format has to be sent
    return Report(diseases=[],
                    syndromes=[],
                    event_date="2018-xx-xx xx:xx:xx to 2018-xx-xx xx:xx:xx",
                    locations=[]
                )

@app.get("/api/v1/search", response_model=ListSearchResult, tags=["v1"])
def list_reports(
    key_terms: str,
    location: str,
    start_date: str = Query(..., regex=date_exact),
    end_date: str = Query(..., regex=date_exact),
    page_number: Optional[int] = None  
):
    """
    Lists all the search results specified within the parameters: start_date to end_date, key_terms and location.
    page_number can be specified to go to the corresponding page.
    """
    # check input is valid

    # HARD-CODED RESPONSE

    if "covid" in key_terms.lower() and "sydney" in location.lower():
        return {
            "results": [SearchResult(article_id=1, url="www.promed.com/mail",date_of_publication="2018-12-02", headline="Covid Strikes Sydney")],
            "num_pages": 1,
            "page_number": 1
        }           



    # TODO: GET id, url, date, heading from articles
    # WHERE word in keywords
    # AND location=location
    # OFFSET 10*page_number
    return {
        "results": [],
        "num_pages": 1,
        "page_number": 1
    } 



def custom_openapi():
    """Boilerplate to return swagger on /doc and prettySwagger on /redoc
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="EpidemicEagle API",
        version="v1",
        description="""
        This is an API to get news articles, reports and search results for diseases.
        Sample dates:
        - 2018-xx-xx xx:xx:xx
        - 2018-11-01 xx:xx:xx
        - 2018-11-xx 17:00:xx
        """,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
