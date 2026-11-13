import os
import pytest

os.environ["INSIGHTBI_DB"] = "test_insightbi.db"

from app.database import init_db
from app.engine.analytics import (
    compute_kpis, get_revenue_trends, get_category_breakdown,
    get_regional_performance, execute_adhoc_query
)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    if os.path.exists("test_insightbi.db"):
        os.remove("test_insightbi.db")
    init_db()
    yield
    if os.path.exists("test_insightbi.db"):
        try:
            os.remove("test_insightbi.db")
        except Exception:
            pass

def test_compute_kpis_aggregate():
    kpis = compute_kpis({})
    assert kpis["total_orders"] >= 30
    assert kpis["total_revenue"] > 50000.0
    assert kpis["total_profit"] > 20000.0
    assert 40.0 <= kpis["blended_margin_pct"] <= 80.0
    assert kpis["unique_customers"] >= 20
    assert kpis["avg_order_value"] > 0.0

def test_compute_kpis_filtered_region():
    na_kpis = compute_kpis({"region": "North America"})
    all_kpis = compute_kpis({})
    assert na_kpis["total_orders"] < all_kpis["total_orders"]
    assert na_kpis["total_revenue"] < all_kpis["total_revenue"]
    assert na_kpis["total_revenue"] > 10000.0

def test_get_revenue_trends():
    trends = get_revenue_trends({})
    assert len(trends) >= 15
    # Verify temporal ordering
    dates = [t["date"] for t in trends]
    assert dates == sorted(dates)
    assert trends[0]["revenue"] > 0.0

def test_get_category_breakdown():
    cats = get_category_breakdown({})
    assert len(cats) >= 3
    cat_names = [c["category"] for c in cats]
    assert "Cloud Services" in cat_names
    assert "Subscriptions" in cat_names
    # Top revenue should be first
    assert cats[0]["revenue"] >= cats[1]["revenue"]

def test_get_regional_performance():
    regions = get_regional_performance({})
    assert len(regions) >= 4
    reg_names = [r["region"] for r in regions]
    assert "North America" in reg_names
    assert "Europe" in reg_names

def test_execute_adhoc_query():
    # Slice by channel and compute revenue
    result = execute_adhoc_query("channel", "revenue", {}, sort="DESC")
    assert len(result) >= 3
    assert result[0]["metric"] == "revenue"
    assert result[0]["dimension"] == "channel"
    assert result[0]["metric_value"] >= result[1]["metric_value"]
