from fastapi import FastAPI, Query, HTTPException
from datetime import datetime, timedelta
from typing import List, Optional
from functools import lru_cache
from holidays import Australia

app = FastAPI()

AUSTRALIAN_STATES = ["ACT", "NSW", "NT", "QLD", "SA", "TAS", "VIC", "WA"]


def get_holidays(state: Optional[str] = None):
    return Australia(years=range(2000, 2050), prov=state)


def is_working_day(date: datetime, state: Optional[str] = None) -> bool:
    holidays = get_holidays(state)
    return date.weekday() < 5 and date not in holidays


@lru_cache(maxsize=1000)
def count_working_days(
    start_date: datetime, end_date: datetime, state: Optional[str] = None
) -> int:
    working_days = sum(
        1
        for day in range((end_date - start_date).days + 1)
        if is_working_day(start_date + timedelta(days=day), state)
    )
    return working_days


def parse_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
        )


@app.get("/working-days")
async def get_working_days(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    state: Optional[str] = Query(
        None, description="Australian state code (e.g., NSW, VIC)"
    ),
) -> dict:
    start = parse_date(start_date)
    end = parse_date(end_date)

    if start > end:
        raise HTTPException(
            status_code=400, detail="Start date must be before or equal to end date"
        )

    if state and state not in AUSTRALIAN_STATES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid state. Must be one of {', '.join(AUSTRALIAN_STATES)}",
        )

    working_days = count_working_days(start, end, state)
    return {"working_days": working_days}


@app.get("/working-days-list")
async def get_working_days_list(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    state: Optional[str] = Query(
        None, description="Australian state code (e.g., NSW, VIC)"
    ),
) -> dict:
    start = parse_date(start_date)
    end = parse_date(end_date)

    if start > end:
        raise HTTPException(
            status_code=400, detail="Start date must be before or equal to end date"
        )

    if state and state not in AUSTRALIAN_STATES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid state. Must be one of {', '.join(AUSTRALIAN_STATES)}",
        )

    working_days = [
        start + timedelta(days=x)
        for x in range((end - start).days + 1)
        if is_working_day(start + timedelta(days=x), state)
    ]

    return {"working_days": [day.strftime("%Y-%m-%d") for day in working_days]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
