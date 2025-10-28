import matplotlib
matplotlib.use('Agg')  # Prevent GUI backend errors on servers
import matplotlib.pyplot as plt
import httpx
import os
from .db import SessionLocal
from sqlalchemy.orm import Session
from .models import Country, Metadata
from datetime import datetime
import logging
import numpy as np
import random

logger = logging.getLogger(__name__)

RESTCOUNTRIES_URL = "https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies"
EXCHANGE_RATE_URL = "https://open.er-api.com/v6/latest/USD"


class ExternalAPIError(Exception):
    """Raised when fetching data from external APIs fails."""
    pass


async def refresh_countries_and_rates():
    """
    Fetch countries and exchange rates, then store them in the database.
    """
    logger.info("Fetching countries and exchange rates...")
    db = SessionLocal()
    try:
        async with httpx.AsyncClient() as client:
            countries_response = await client.get(RESTCOUNTRIES_URL)
            exchange_response = await client.get(EXCHANGE_RATE_URL)

        if countries_response.status_code != 200:
            raise ExternalAPIError(f"RESTCountries API failed with {countries_response.status_code}")
        if exchange_response.status_code != 200:
            raise ExternalAPIError(f"ExchangeRate API failed with {exchange_response.status_code}")

        countries_data = countries_response.json()
        exchange_data = exchange_response.json()
        rates = exchange_data.get("rates", {})

        if not isinstance(countries_data, list):
            raise Exception("Unexpected RESTCountries response format")

        # Clear old data
        db.query(Country).delete()

        inserted = 0
        missing_rates = 0

        for c in countries_data:
            name = c.get("name", {}).get("common")
            code = c.get("cca2")
            capital_list = c.get("capital")
            capital = capital_list[0] if capital_list else None
            region = c.get("region")
            population = c.get("population") or 0
            currencies = c.get("currencies", {})
            currency_code = list(currencies.keys())[0] if currencies else None
            flag_url = c.get("flags", {}).get("png")

            if not name or not code:
                continue  # skip malformed entries

            exchange_rate = None
            if currency_code and currency_code in rates:
                exchange_rate = rates[currency_code]
            elif currency_code == "USD":
                exchange_rate = 1.0
            else:
                missing_rates += 1

            estimated_gdp = None
            if population > 0 and exchange_rate:
                random_multiplier = random.randint(1000, 2000)
                estimated_gdp = round(population * random_multiplier / exchange_rate, 2)

            country_obj = Country(
                name=name,
                capital=capital,
                region=region,
                population=population,
                currency_code=currency_code,
                exchange_rate=exchange_rate,
                estimated_gdp=estimated_gdp,
                flag_url=flag_url,
                last_refreshed_at=datetime.utcnow(),
            )
            db.add(country_obj)
            inserted += 1

        db.commit()
        logger.info(f"Inserted {inserted} countries ({missing_rates} missing rates).")
        return inserted

    except Exception as e:
        logger.exception("Error refreshing countries")
        db.rollback()
        raise e
    finally:
        db.close()


def generate_gdp_summary_chart(db: Session, output_path: str = "cache/summary.png"):
    """
    Generate a bar chart summarizing total estimated GDP per region.
    Includes total countries, top 5 countries by estimated GDP, and last refresh timestamp.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    countries = db.query(Country).all()
    if not countries:
        raise ValueError("No countries found in database")

    # GDP by region
    region_gdp = {}
    for c in countries:
        if c.region and c.estimated_gdp:
            region_gdp[c.region] = region_gdp.get(c.region, 0) + c.estimated_gdp

    if not region_gdp:
        raise ValueError("No valid GDP data found")

    sorted_regions = sorted(region_gdp.items(), key=lambda x: x[1], reverse=True)
    regions = [r for r, _ in sorted_regions]
    gdps = [g for _, g in sorted_regions]

    # Top 5 countries by estimated GDP
    top5_countries = sorted(
        [c for c in countries if c.estimated_gdp],
        key=lambda x: x.estimated_gdp,
        reverse=True
    )[:5]

    # Last refresh timestamp
    last_refresh = None
    meta = db.query(Metadata).filter(Metadata.key == "last_refreshed_at").first()
    if meta and meta.value:
        last_refresh = meta.value

    # Plot bar chart
    plt.figure(figsize=(12, 7))
    bars = plt.bar(regions, gdps, color=plt.cm.viridis(np.linspace(0.2, 0.9, len(regions))))
    plt.xlabel("Region", fontsize=12)
    plt.ylabel("Total Estimated GDP (USD)", fontsize=12)
    plt.title("Total Estimated GDP by Region", fontsize=14, fontweight="bold")
    plt.xticks(rotation=25, ha="right")

    # Labels above bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height,
                 f"{height/1e12:.2f}T", ha="center", va="bottom", fontsize=9)

    # Info text box
    total_countries = len(countries)
    top5_text = "\n".join([f"{c.name}: {c.estimated_gdp/1e9:.2f}B" for c in top5_countries])
    last_refresh_text = last_refresh if last_refresh else "N/A"

    info_text = (
        f"Total Countries: {total_countries}\n"
        f"Top 5 Countries by GDP:\n{top5_text}\n"
        f"Last Refresh: {last_refresh_text}"
    )
    plt.gcf().text(0.02, 0.02, info_text, fontsize=10, va="bottom", ha="left",
                   bbox=dict(facecolor='white', alpha=0.6, edgecolor='black'))

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"GDP summary chart saved to {output_path}")
    return output_path
