from pydantic import BaseModel, Field
from typing import Optional, List

class KPISummaryResponse(BaseModel):
    total_orders: int
    total_revenue: float
    total_cost: float
    total_profit: float
    blended_margin_pct: float
    total_units: int
    unique_customers: int
    avg_order_value: float

class RevenueTrendItem(BaseModel):
    date: str
    revenue: float
    profit: float
    units: int
    orders: int

class CategoryBreakdownItem(BaseModel):
    category: str
    revenue: float
    profit: float
    units: int
    orders: int
    margin_pct: float

class RegionalPerformanceItem(BaseModel):
    region: str
    revenue: float
    profit: float
    orders: int
    avg_order_value: float

class AdhocQueryRequest(BaseModel):
    dimension: str = Field("category", description="Dimension to group by: region, channel, category, product_name, date")
    metric: str = Field("revenue", description="Metric to compute: revenue, profit, units, orders, avg_order_value, avg_margin")
    region: Optional[str] = None
    category: Optional[str] = None
    channel: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    sort: Optional[str] = "DESC"
    limit: Optional[int] = 50

class AdhocQueryResultItem(BaseModel):
    dimension: str
    dimension_value: str
    metric: str
    metric_value: float
    transaction_count: int
    total_revenue: float

class FilterOptionsResponse(BaseModel):
    regions: List[str]
    categories: List[str]
    channels: List[str]
