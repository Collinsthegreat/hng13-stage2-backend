from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

import country_currency_api.models  # make sure this matches your actual filename (models.py) and modifications for deployment



def get_countries(db: Session, region: str = None, currency: str = None, sort: str = None):
    """Retrieve countries filtered by region, currency, and sorted by GDP if specified."""
    q = db.query(country_currency_api.models.Country)

    if region:
        q = q.filter(func.lower(country_currency_api.models.Country.region) == region.lower())
    if currency:
        q = q.filter(func.lower(country_currency_api.models.Country.currency_code) == currency.lower())

    if sort:
        if sort == "gdp_desc":
            q = q.order_by(country_currency_api.models.Country.estimated_gdp.desc())
        elif sort == "gdp_asc":
            q = q.order_by(country_currency_api.models.Country.estimated_gdp.asc())

    countries = q.all()

    # Return clean dicts
    return [
        {
            "name": c.name,
            "capital": c.capital,
            "region": c.region,
            "population": c.population,
            "currency_code": c.currency_code,
            "exchange_rate": c.exchange_rate,
            "estimated_gdp": c.estimated_gdp,
            "flag_url": c.flag_url,
        }
        for c in countries
    ]


def get_country_by_name(db: Session, name: str):
    """Fetch a single country by name (case-insensitive)."""
    return db.query(country_currency_api.models.Country).filter(func.lower(country_currency_api.models.Country.name) == name.lower()).first()


def delete_country(db: Session, name: str) -> bool:
    """Delete a country by name and return True if successful."""
    country = get_country_by_name(db, name)
    if not country:
        return False
    db.delete(country)
    db.commit()
    return True


def get_status(db: Session):
    """Return total number of countries and last refresh time."""
    total = db.query(func.count(country_currency_api.models.Country.id)).scalar()
    meta = db.query(country_currency_api.models.Metadata).filter(country_currency_api.models.Metadata.key == "last_refreshed_at").first()
    last = None
    if meta and meta.value:
        try:
            last = datetime.fromisoformat(meta.value)
        except ValueError:
            last = None
    return total, last


def upsert_country(db: Session, data: dict):
    """
    Insert or update a Country record (match by name, case-insensitive).
    Raises ValueError if required fields are missing.
    """
    required_fields = ["name", "population", "currency_code"]
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    existing = db.query(country_currency_api.models.Country).filter(
        func.lower(country_currency_api.models.Country.name) == data["name"].lower()
    ).first()

    if existing:
        # Update existing record
        for k, v in data.items():
            setattr(existing, k, v)
        existing.last_refreshed_at = datetime.utcnow()
        db.add(existing)
    else:
        # Insert new record
        new = country_currency_api.models.Country(**data)
        db.add(new)

    db.commit()


def update_last_refreshed(db: Session, timestamp_iso: str):
    """Update or insert the last_refreshed_at metadata entry."""
    meta = db.query(country_currency_api.models.Metadata).filter(country_currency_api.models.Metadata.key == "last_refreshed_at").first()
    if meta:
        meta.value = timestamp_iso
    else:
        meta = country_currency_api.models.Metadata(key="last_refreshed_at", value=timestamp_iso)
        db.add(meta)
    db.commit()
