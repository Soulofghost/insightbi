from fastapi import APIRouter, Query
from typing import Optional, List
from app.database import get_db_connection
from app.schemas import (
    KPISummaryResponse, RevenueTrendItem, CategoryBreakdownItem,
    RegionalPerformanceItem, FilterOptionsResponse
)
from app.engine.analytics import (
    compute_kpis, get_revenue_trends, get_category_breakdown, get_regional_performance
)

router = APIRouter(prefix="/metrics", tags=["Analytics & KPIs"])

@router.get("/kpis", response_model=KPISummaryResponse)
def get_kpis(
    region: Optional[str] = None,
    category: Optional[str] = None,
    channel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    filters = {
        "region": region,
        "category": category,
        "channel": channel,
        "start_date": start_date,
        "end_date": end_date
    }
    return compute_kpis(filters)

@router.get("/trends", response_model=List[RevenueTrendItem])
def get_trends(
    region: Optional[str] = None,
    category: Optional[str] = None,
    channel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    filters = {
        "region": region,
        "category": category,
        "channel": channel,
        "start_date": start_date,
        "end_date": end_date
    }
    return get_revenue_trends(filters)

@router.get("/categories", response_model=List[CategoryBreakdownItem])
def get_categories(
    region: Optional[str] = None,
    channel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    filters = {
        "region": region,
        "channel": channel,
        "start_date": start_date,
        "end_date": end_date
    }
    return get_category_breakdown(filters)

@router.get("/regions", response_model=List[RegionalPerformanceItem])
def get_regions(
    category: Optional[str] = None,
    channel: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    filters = {
        "category": category,
        "channel": channel,
        "start_date": start_date,
        "end_date": end_date
    }
    return get_regional_performance(filters)

@router.get("/filter-options", response_model=FilterOptionsResponse)
def get_filter_options():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        regions = [r[0] for r in cursor.execute("SELECT DISTINCT region FROM transactions ORDER BY region").fetchall()]
        categories = [r[0] for r in cursor.execute("SELECT DISTINCT category FROM transactions ORDER BY category").fetchall()]
        channels = [r[0] for r in cursor.execute("SELECT DISTINCT channel FROM transactions ORDER BY channel").fetchall()]
        return FilterOptionsResponse(
            regions=regions,
            categories=categories,
            channels=channels
        )
