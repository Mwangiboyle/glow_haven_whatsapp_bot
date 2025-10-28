
from fastapi import APIRouter, HTTPException
import json
from pathlib import Path

router = APIRouter()

@router.get("/")
def get_business_info():
    data_path = Path("business.json")
    if not data_path.exists():
        raise HTTPException(status_code=404, detail="Business data not found")

    with open(data_path) as f:
        business_data = json.load(f)
    return business_data

@router.get("/list")
def get_services():
    data_path = Path("business.json")
    with open(data_path) as f:
        data = json.load(f)
    return {"services": data.get("services", [])}
