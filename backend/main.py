"""
Main FastAPI Application - AstroLogic AI Backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
import traceback

from astrology_core import geocode_city, local_to_utc, calculate_western_vedic
from mahabote import calculate_mahabote
from ai_engine import generate_reading

app = FastAPI(
    title="AstroLogic AI API",
    description="Astrology synthesis engine combining Western, Vedic, and Burmese Mahabote traditions.",
    version="1.0.0"
)

# Allow Next.js frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BirthDataRequest(BaseModel):
    name: str = Field(default="User", description="User's name")
    gender: str = Field(default="Unknown", description="User's gender")
    dob: str = Field(..., description="Date of birth in YYYY-MM-DD format")
    time: str = Field(..., description="Time of birth in HH:MM format (24h)")
    city: str = Field(..., description="City of birth")


class SynthesisResponse(BaseModel):
    synthesis: dict
    reading: str | None = None
    error: str | None = None


@app.get("/")
def root():
    return {"message": "AstroLogic AI API is running. POST to /api/synthesis to get a reading."}


@app.post("/api/synthesis", response_model=SynthesisResponse)
async def create_synthesis(data: BirthDataRequest):
    """
    Main endpoint: takes birth data and returns the full astrological synthesis + AI reading.
    """
    try:
        # 1. Parse the birth datetime
        birth_dt_str = f"{data.dob} {data.time}"
        birth_dt_local = datetime.strptime(birth_dt_str, "%Y-%m-%d %H:%M")

        # 2. Geocode the city
        geo = geocode_city(data.city)

        # 3. Convert local time to UTC
        try:
            birth_dt_utc = local_to_utc(birth_dt_local, data.city)
        except Exception:
            # If timezone resolution fails, treat as UTC
            import pytz
            birth_dt_utc = pytz.utc.localize(birth_dt_local)

        # 4. Calculate Western + Vedic data
        astro_data = calculate_western_vedic(birth_dt_utc.replace(tzinfo=None), geo["lat"], geo["lon"])

        # 5. Calculate Mahabote data
        mahabote_data = calculate_mahabote(birth_dt_local.date())

        # 6. Build the Synthesis Object
        synthesis = {
            "user": {
                "name": data.name,
                "gender": data.gender,
                "dob": data.dob,
                "time": data.time,
                "city": data.city,
                "coordinates": {"lat": geo["lat"], "lon": geo["lon"]},
            },
            "western": astro_data["western"],
            "vedic": astro_data["vedic"],
            "mahabote": mahabote_data,
        }

        # 7. Get AI reading
        try:
            reading = generate_reading(synthesis)
        except Exception as ai_err:
            reading = None
            print(f"AI reading failed: {ai_err}")

        return SynthesisResponse(synthesis=synthesis, reading=reading)

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/synthesis/data-only")
async def get_synthesis_data_only(data: BirthDataRequest):
    """
    Returns only the calculated synthesis data (no AI reading). Useful for testing the math.
    """
    try:
        birth_dt_str = f"{data.dob} {data.time}"
        birth_dt_local = datetime.strptime(birth_dt_str, "%Y-%m-%d %H:%M")
        geo = geocode_city(data.city)

        try:
            birth_dt_utc = local_to_utc(birth_dt_local, data.city)
        except Exception:
            import pytz
            birth_dt_utc = pytz.utc.localize(birth_dt_local)

        astro_data = calculate_western_vedic(birth_dt_utc.replace(tzinfo=None), geo["lat"], geo["lon"])
        mahabote_data = calculate_mahabote(birth_dt_local.date())

        return {
            "user": {"name": data.name, "dob": data.dob, "city": data.city},
            "western": astro_data["western"],
            "vedic": astro_data["vedic"],
            "mahabote": mahabote_data,
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
