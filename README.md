# HNG13 Stage 2 Backend — Country Currency & Exchange API

A robust FastAPI-based RESTful API for HNG13 Backend Stage 2, designed to fetch, store, and query country data including population, currency, exchange rates, and estimated GDP.  

Deployed live on Railway:  
https://<your-deployment-link>.railway.app  

---

## Tech Stack
- **Backend Framework:** FastAPI
- **Runtime:** Python 3.12+
- **Database:** MySQL / SQLite (for local testing)
- **ORM:** SQLAlchemy
- **Server:** Uvicorn
- **Hosting:** Railway
- **Version Control:** Git + GitHub

---

## Features
- Fetch and cache country data from external APIs
- Compute **estimated GDP** for each country
- CRUD operations on countries:
  - Create / Update (via refresh)
  - Retrieve all countries or by name
  - Delete a country
- Filter and sort countries by region, currency, or GDP
- Generate summary GDP chart image by region
- External API error handling (returns 503 if APIs fail)
- Validation: required fields `name`, `population`, `currency_code`
- Auto timestamp `last_refreshed_at` for refresh tracking

---

## 📡 API Endpoints

### 1️⃣ Refresh Countries
**Endpoint:** `POST /countries/refresh`  

Fetch all countries and exchange rates, store in DB, and update summary chart.

**Example Request:**
```bash
curl -X POST https://<your-deployment-link>.railway.app/countries/refresh

Get All Countries

Endpoint: GET /countries

Optional query parameters:

?region=Africa

?currency=NGN

?sort=gdp_desc or gdp_asc

Example Request:

curl "https://<your-deployment-link>.railway.app/countries?region=Africa&sort=gdp_desc"


Example Response:

[
  {
    "name": "Nigeria",
    "capital": "Abuja",
    "region": "Africa",
    "population": 206139587,
    "currency_code": "NGN",
    "exchange_rate": 460.0,
    "estimated_gdp": 450000000,
    "flag_url": "https://flagcdn.com/ng.png"
  }
]

3️⃣ Get Single Country

Endpoint: GET /countries/{name}

Example:

curl https://<your-deployment-link>.railway.app/countries/Nigeria

4️⃣ Delete Country

Endpoint: DELETE /countries/{name}

Example:

curl -X DELETE https://<your-deployment-link>.railway.app/countries/Nigeria


Response:

{
  "message": "Country deleted"
}

5️⃣ Get Status

Endpoint: GET /status

Returns total countries and last refresh timestamp.

Example Response:

{
  "total_countries": 250,
  "last_refreshed_at": "2025-10-28T00:35:36Z"
}

6️⃣ Get Summary Image

Endpoint: GET /countries/image

Serves the generated GDP summary chart image.

Example Response: Returns the PNG file cache/summary.png
If not available:

{
  "error": "Summary image not found"
}

Local Setup Guide
1️⃣ Clone the repo
git clone https://github.com/<your-username>/hng13-stage2-backend.git
cd hng13-stage2-backend/country_currency_api

2️⃣ Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run the API
uvicorn main:app --reload


Visit http://127.0.0.1:8000
 to test locally.

Environment Variables
Variable	Description	Example
DATABASE_URL	MySQL connection string	mysql+pymysql://user:password@localhost/dbname
DEBUG	Enable debug mode	True / False

Example .env File

DATABASE_URL=mysql+pymysql://root:password@127.0.0.1/country_db
DEBUG=True

Testing Endpoints

You can test endpoints using curl or Postman. Ensure your local server is running:

uvicorn main:app --reload

Deployment (Railway)

Push your project to GitHub.

Create a new Railway project → Deploy from GitHub repo.

Add environment variables under Settings → Variables:

DATABASE_URL

DEBUG=False

Ensure your Procfile contains:

web: uvicorn main:app --host=0.0.0.0 --port=${PORT:-8000}


Deploy and confirm your app is live.

Requirements.txt
fastapi==0.95.2
uvicorn==0.21.1
httpx==0.24.1
sqlalchemy==2.0.22
pymysql==1.1.0
python-dotenv==1.0.0
matplotlib==3.8.1
numpy==1.26.5
pillow==10.0.1

Author

Name: Collins The Great
Email: yourname@example.com

GitHub: github.com/your-username
