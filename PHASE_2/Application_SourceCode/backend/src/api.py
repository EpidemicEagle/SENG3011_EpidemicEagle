from datetime import date, datetime, timedelta
from resource import RLIMIT_CPU
from fastapi import FastAPI, HTTPException, Query, Request, Form
from fastapi.openapi.utils import get_openapi
from typing import List,Optional
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
from starlette.responses import PlainTextResponse, RedirectResponse
import json

app = FastAPI(openapi_url="/api/v1/openapi.json")
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

class foo(BaseModel):
    id : int



responses = {
    404: {"description": "Item not found"}
}

users = []

################################
#
# REAL FUNCTIONS
#
################################

def parse_report_info(keyword, article):
    return set([_ for _ in [_[keyword] for _ in article['reports']] for _ in _])

# unify index calls
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/index.html", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request,
    rname: str = Form(...),
    remail: str = Form(...),
    rphone: str = Form(...),
    rmessage: str = Form(...)
):
    print(rname, remail, rphone, rmessage)
    f = open('users.json', 'r+')
    data = json.load(f)
    f.close()
    # print(data)
    agencies = data['agencies']   
    for agency in agencies:
        agency['new_requests'].append({'email': remail,'message':rmessage, 'name': rname, 'phone':rphone})

    jsonFile = open("users.json", "w+")
    jsonFile.write(json.dumps(data, indent=2))
    jsonFile.close()

    return templates.TemplateResponse("index.html", {"request": request, 'success':True})

@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

def covid_api(dest):
    url = "https://disease.sh/v3/covid-19/countries/" + dest + "?strict=true"
    response = requests.get(url)
    return response.json()

def report_find(start_date, end_date, location):
    f = open('reports_file_v2.json')
    data = json.load(f)['reports']
    f.close()
    reports = []
    count = 0
    locations = ["Afghanistan","Albania","Algeria","Andorra","Angola","Anguilla","Antigua & Barbuda","Argentina","Armenia","Aruba","Australia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize","Benin","Bermuda","Bhutan","Bolivia","Bosnia & Herzegovina","Botswana","Brazil","British Virgin Islands","Brunei","Bulgaria","Burkina Faso","Burundi","Cambodia","Cameroon","Canada","Cape Verde","Cayman Islands","Central Arfrican Republic","Chad","Chile","China","Colombia","Congo","Cook Islands","Costa Rica","Cote D Ivoire","Croatia","Cuba","Curacao","Cyprus","Czech Republic","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea","Estonia","Ethiopia","Falkland Islands","Faroe Islands","Fiji","Finland","France","French Polynesia","French West Indies","Gabon","Gambia","Georgia","Germany","Ghana","Gibraltar","Greece","Greenland","Grenada","Guam","Guatemala","Guernsey","Guinea","Guinea Bissau","Guyana","Haiti","Honduras","Hong Kong","Hungary","Iceland","India","Indonesia","Iran","Iraq","Ireland","Isle of Man","Israel","Italy","Jamaica","Japan","Jersey","Jordan","Kazakhstan","Kenya","Kiribati","Kosovo","Kuwait","Kyrgyzstan","Laos","Latvia","Lebanon","Lesotho","Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Macau","Macedonia","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Marshall Islands","Mauritania","Mauritius","Mexico","Micronesia","Moldova","Monaco","Mongolia","Montenegro","Montserrat","Morocco","Mozambique","Myanmar","Namibia","Nauro","Nepal","Netherlands","Netherlands Antilles","New Caledonia","New Zealand","Nicaragua","Niger","Nigeria","North Korea","Norway","Oman","Pakistan","Palau","Palestine","Panama","Papua New Guinea","Paraguay","Peru","Philippines","Poland","Portugal","Puerto Rico","Qatar","Reunion","Romania","Russia","Rwanda","Saint Pierre & Miquelon","Samoa","San Marino","Sao Tome and Principe","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovakia","Slovenia","Solomon Islands","Somalia","South Africa","South Korea","South Sudan","Spain","Sri Lanka","St Kitts & Nevis","St Lucia","St Vincent","Sudan","Suriname","Swaziland","Sweden","Switzerland","Syria","Taiwan","Tajikistan","Tanzania","Thailand","Timor L'Este","Togo","Tonga","Trinidad & Tobago","Tunisia","Turkey","Turkmenistan","Turks & Caicos","Tuvalu","Uganda","Ukraine","United Arab Emirates","United Kingdom","United States of America","Uruguay","Uzbekistan","Vanuatu","Vatican City","Venezuela","Vietnam","Virgin Islands (US)","Yemen","Zambia","Zimbabwe"];
    
    for report in data:
        if count >= 10:
            break
        # check date of report
        date = datetime.strptime(report['eventDate'], "%Y-%M-%d")
        if start_date < date and date < end_date:

            #check each location of report
            for replocation in report['locations']:
                # check report location is valid and is searched location
                if replocation in locations and replocation == location:
                    # check key terms
                    # if key_terms in report['diseases']:
                    report["l_diseases"] = ", ".join(report['diseases'])
                    report["l_locations"] = ", ".join(report['locations'])
                    # change the report for html
                    reports.append(report)
                    count += 1
                    # can stop checking report locations
                    break
    return reports

@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def q(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse, include_in_schema=False)
async def q(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "wrong_user": True})

@app.post("/traveller", response_class=HTMLResponse, include_in_schema=False)
async def q(request: Request,
    email: str = Form(...),
    password: str = Form(...),
    ):
    print(email, password)
    f = open('users.json', 'r+')
    data = json.load(f)
    users = data['travellers']
    for user in users:
        if user['email'] == email and user['password'] == password:
            return templates.TemplateResponse("person.html", {
                "request": request, 
                "user": user, 
                "covid_data" : covid_api(user['destination']),
                "risk_level" : risk_level(user['destination']),
                "reports": report_find(datetime.now() - timedelta(days=180), datetime.now(), user['destination'])
                })
    return RedirectResponse("/login") 

@app.post("/inquiry", response_class=HTMLResponse, include_in_schema=False)
async def q(request: Request,
    message: str = Form(...),
    problem: str = Form(...),
    email: str = Form(...),
    name: str = Form(...)
    ): 
    print(message,problem, email, name)
    # change the json to include the request
    f = open('users.json', 'r+')
    data = json.load(f)
    f.close()
    # print(data)
    agencies = data['agencies']   
    for agency in agencies:
        d = agency['users']
        for user in d:
            if user['email'] == email and user['name'] == name:
                print('hi')
                agency['current_requests'].append({'name': name,'message':message})
                print(agency)
                print(data)
                jsonFile = open("users.json", "w+")
                jsonFile.write(json.dumps(data, indent=2))
                jsonFile.close()
                break

    return templates.TemplateResponse("index.html", {"request": request, "success": True})
    # return templates.TemplateResponse("index.html", {"request": request})

@app.get("/agency", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse("agency.html", {"request": request})

# QUICK SEARCH
# qsearch search box
@app.get("/qsearch", response_class=HTMLResponse, include_in_schema=False)
async def q(request: Request):
    return templates.TemplateResponse("qsearch.html", {"request": request})

def risk_level(location):
    f = open("country_codes.json", 'r')
    data = json.load(f)
    code = data.get(location, "not found")
    if code == 'not found':
        return "No risk data detected."
    else:
        response = requests.get('https://www.travel-advisory.info/api')
        a = response.json()['data'][code]['advisory']
    return a


# qsearch table
@app.post("/qsearch", response_class=HTMLResponse, include_in_schema=False)
async def q(request: Request,
    location: Optional[str] = Form(...),
):
    f = open('sample_file.json')
    data= json.load(f)['articles']
    f.close()
    searches = []
    count = 0
    start_date = datetime.now() - timedelta(days=90)
    end_date = datetime.now()

    # average time is 3000 ms (3 seconds)
    for article in data:
        if count == 10:
            break
        # exclude and pagination
        date = datetime.strptime(article['dateOfPublication'], '%d %B %Y')

        if start_date < date and date < end_date:
            locations = parse_report_info('locations', article)
            if location in locations:
                searches.append(article)
                count += 1
        count += 1
    
    rl = risk_level(location)
    # print(rl)
    return templates.TemplateResponse("qsearch.html", 
    {
        "location": location,
        "request": request,
        "searches": searches,
        "risk_level": rl
    }
    )

# REPORT SEARCH
# reports get
@app.get("/reports", response_class=HTMLResponse, include_in_schema=False)
async def reports(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request})

# reports post
@app.post("/reports", response_class=HTMLResponse, include_in_schema=False)
async def reports(request: Request,
    location: str = Form(...),
    start_date: datetime = Form(...),
    end_date: datetime = Form(...),
    # page_number: Optional[int] = None  
):
    return templates.TemplateResponse("reports.html", 
    {
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        # "page_number": page_number,
        "request": request,
        "reports": report_find(start_date, end_date, location),
    }
    )


# COMPLETE SEARCH
# search get
@app.get("/completesearch", response_class=HTMLResponse, include_in_schema=False)
async def search(request: Request):
    return templates.TemplateResponse("completesearch.html", {"request": request})

# search post
@app.post("/completesearch", response_class=HTMLResponse, include_in_schema=False)
async def search_post(request: Request,
    disease: str = Form(...),
    location: str = Form(...),
    start_date: datetime  = Form(...),
    end_date: datetime = Form(...),
    page_number: Optional[int] = None  
):
    # test dates
    # test location


    f = open('sample_file.json')
    data= json.load(f)['articles']
    f.close()
    searches = []
    count = 0

    # average time is 3000 ms (3 seconds)
    for article in data:
        if count == 10:
            break
        # exclude and pagination
        date = datetime.strptime(article['dateOfPublication'], '%d %B %Y')

        # do easy comparision before hard comparision
        if start_date < date and date < end_date:
            # then limit by the harder values
            diseases = parse_report_info('diseases', article)
            locations = parse_report_info('locations', article)
            if disease in diseases and location in locations:
                # change response to fit html better
                article.update(dateOfPublication=date)
                searches.append(article)
                count += 1
        
    # print(searches)

    return templates.TemplateResponse("completesearch.html", 
    {
        "disease": disease,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "page_number": page_number,
        "request": request,
        "searches": searches
    }
    )

from bs4 import BeautifulSoup as bs
import requests as rq
def getsoup(url):
    res = rq.get(url)
    soup = bs(res.content, features="lxml")
    paras = []
    i = 0
    for link in soup.findAll('p'):
        # print(link)
        if link != 'None' or link != "":
            paras.append({"string":link.string,
            "id":"para"+str(i)})
            i += 1
    return paras
# articles id get
@app.post("/article", response_class=HTMLResponse, include_in_schema=False)
async def id_articles(request: Request,
id: str = Form(...)):
    f = open("articles.json")
    data = json.load(f)['articles']
    length = len(data)

    # return 'no articles found if greater than num of articles"
    if int(id) > length or int(id) < 0:
        return templates.TemplateResponse("entry_article.html", {"request": request, "id": id})
    article = data[int(id)]    
    paras = getsoup(article['url'])

    return templates.TemplateResponse("entry.html", {"request": request, "id": id, "article": article, 'paras': paras})

# traveller get
@app.get("/edit", response_class=HTMLResponse, include_in_schema=False)
async def traveller_edit(request: Request):
    return templates.TemplateResponse("traveller_edit.html", {"request": request})


# traveller post
@app.post("/edit", response_class=HTMLResponse, include_in_schema=False)
async def traveller_dash_edit(request: Request):
    found_user = None
    for user in users:
        if user["id"] == id:
            found_user = user
            break
    found_user = {
        "name": "testing",
    }
    if found_user: 
        """
            "traveller": request,
            "start_loc": start_loc,
            "end_loc": end_loc,
            "start_date": start_date,
            "end_date": end_date,
            "reports": reports,
        """
        return templates.TemplateResponse("traveller_edit.html", 
        {
            
            "user": found_user,
            "request": request,
            
        }
        

    
        )
    else:
        # user not found, try again
        return templates.TemplateResponse("traveller_edit.html", 
        {
            
            "request": request,
        }
        )



# traveller get
@app.get("/traveller_edit", response_class=HTMLResponse, include_in_schema=False)
async def traveller_edit(request: Request,
    name: str,
    email: str,
    phone: str,
    destination: str,
    location: str,
    type: str,
):
    if type =='edit':
        return templates.TemplateResponse("edit.html", {"request": request,
        'name': name,
        'email': email,
        'phone': phone,
        'destination': destination,
        'location': location
        })
    elif type == 'new':
        # change the json 
        f = open('users.json', 'r+')
        data = json.load(f)
        f.close()
        # print(data)
        ln = len(data['travellers']) + 2
        user = {
            'name': name,
            'email': email,
            'phone': phone,
            'destination': destination,
            'location': location,
            'u_id':str(ln),
            'password': 'abc123'
        }
        agencies = data['agencies'][0]
        agencies['users'].append(ln)
        data['travellers'].append(user)

        with open('users.json', 'w') as fp:
            fp.write(json.dumps(data, indent=2, sort_keys=True, default=str))
        return templates.TemplateResponse("index.html", {
            "request": request,
            "edit": True
        })


# /traveller_edit
@app.post("/traveller_edit", response_class=HTMLResponse, include_in_schema=False)
async def traveller_edit(request: Request,
    phone: str = Form(...),
    destination: str = Form(...),
    location: str = Form(...),
    name: str = Form(...),

):
    print(phone,destination,location, name)
    f = open('users.json', 'r+')
    data = json.load(f)
    f.close() 
    for traveller in data['travellers']:
        if traveller['name'] == name:
            # change if not null
            print("Matched")
            if location != "":
                traveller.update(location=location)
            if destination != "":
                traveller.update(destination=destination)
            if phone != "":
                traveller.update(phone=phone)   
            break
    
    with open('users.json', 'w') as fp:
        fp.write(json.dumps(data, indent=2, sort_keys=True, default=str))
        
    return templates.TemplateResponse("index.html", {
        "request": request,
        "edit": True
        })

@app.get("/remove", response_class=HTMLResponse, include_in_schema=False)
async def traveller_edit(request: Request,
    name: str,
    msg: str, 
    type: str
):


    # change the json
    f = open('users.json', 'r+')
    data = json.load(f)
    f.close() 
    if type == "cur":
        t = {'name':name, 'message':msg}
        for i in data['agencies']:
            if t in i['current_requests']:
                i['current_requests'].remove(t)
    elif type == 'new':
        for i in data['agencies']:
            for k in i['new_requests']:
                if k['name'] == name and k['message'] == msg:
                    i['new_requests'].remove(k)
    with open('users.json', 'w') as fp:
        fp.write(json.dumps(data, indent=2, sort_keys=True, default=str))
    return templates.TemplateResponse("index.html", {
        "request": request,
        "removed": True
    })


# travel agency get
@app.get("/travelagency", response_class=HTMLResponse, include_in_schema=False)
async def travelagency(request: Request):
    return templates.TemplateResponse("travelagency.html", {"request": request})


def getusers(l):
    l = [str(_) for _ in l]
    f = open('users.json', 'r+')
    data = json.load(f)
    users = data['travellers']
    things = []
    for u in users:
        if u['u_id'] in l:
            things.append(u)
    return things     

@app.post("/travelagency", response_class=HTMLResponse, include_in_schema=False)
async def q(request: Request,
    email: str = Form(...),
    password: str = Form(...),
    ):
    f = open('users.json', 'r+')
    data = json.load(f)
    users = data['agencies']
    f.close()
    for agency in users:
        if agency['email'] == email and agency['password'] == password:
            return templates.TemplateResponse("travelagency.html", {
                "request": request, 
                "agency": agency,
                "users": getusers(agency['users'])
                })
    return RedirectResponse("/login") 

## API functions
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