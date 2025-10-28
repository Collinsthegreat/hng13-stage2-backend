from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from .utils import refresh_countries_and_rates, generate_gdp_summary_chart, ExternalAPIError
from sqlalchemy.orm import Session
from fastapi import Query
from .models import Country
import logging
from datetime import datetime
import os
from .db import SessionLocal, engine
from models import Base
import crud

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI instance
app = FastAPI(title="Country Currency API")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_IMAGE_PATH = "cache/summary.png"


# ✅ COUNTRY REFRESH ENDPOINT (GET + POST)

@app.api_route("/countries/refresh", methods=["GET", "POST"])
async def refresh_countries():
    """
    Fetch and refresh all country data from RESTCountries + ExchangeRate APIs.
    Returns 503 if external APIs fail.
    """
    db = SessionLocal()
    try:
        await refresh_countries_and_rates()

        # Update last refreshed timestamp
        from crud import update_last_refreshed
        now_iso = datetime.utcnow().isoformat()
        update_last_refreshed(db, now_iso)

        # Regenerate GDP summary chart
        chart_path = generate_gdp_summary_chart(db)

        return JSONResponse(
            content={
                "message": "Countries refreshed and chart updated successfully!",
                "chart_path": chart_path,
                "last_refreshed_at": now_iso,
            },
            status_code=200,
        )

    except ExternalAPIError as e:
        # ✅ Return 503 for external API failures
        return JSONResponse(
            content={"error": "External data source unavailable", "details": str(e)},
            status_code=503,
        )

    except Exception as e:
        # All other errors → 500
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"error": "Internal server error", "details": str(e)},
            status_code=500,
        )

    finally:
        db.close()



@app.get("/countries")
def get_countries_endpoint(
    region: str | None = Query(None, description="Filter by region"),
    currency: str | None = Query(None, description="Filter by currency code"),
    sort: str | None = Query(None, description="Sort by estimated GDP: gdp_asc or gdp_desc")
):
    """Return countries with optional filters and sorting."""
    db = SessionLocal()
    try:
        countries = crud.get_countries(db, region=region, currency=currency, sort=sort)

        if not countries:
            raise HTTPException(status_code=404, detail="No countries found")

        # ✅ Simply return the list of dicts
        return countries

    finally:
        db.close()



@app.get("/countries/image")
def get_image():
    """
    Generate (if needed) and return the GDP summary chart by region.
    """
    db = SessionLocal()
    try:
        chart_path = generate_gdp_summary_chart(db)

        if not chart_path or not os.path.exists(chart_path):
            raise HTTPException(status_code=404, detail="Chart file not found")

        return FileResponse(chart_path, media_type="image/png")
    except Exception as e:
        return JSONResponse(
            content={"error": "Failed to generate image", "details": str(e)},
            status_code=500,
        )
    finally:
        db.close()


@app.get("/countries/{name}")
def get_country(name: str):
    db = SessionLocal()
    try:
        country = crud.get_country_by_name(db, name)
        if not country:
            raise HTTPException(status_code=404, detail="Country not found")
        return country
    finally:
        db.close()


@app.delete("/countries/{name}")
def delete_country(name: str):
    db = SessionLocal()
    try:
        success = crud.delete_country(db, name)
        if not success:
            raise HTTPException(status_code=404, detail="Country not found")
        return JSONResponse(content={"message": "Country deleted"}, status_code=200)
    finally:
        db.close()


@app.get("/status")
def get_status():
    db = SessionLocal()
    try:
        total, last = crud.get_status(db)
        out = {
            "total_countries": total,
            "last_refreshed_at": last.isoformat() + "Z" if last else None,
        }
        return out
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Country Currency API is running!"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})
