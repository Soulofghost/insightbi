import os
import pytest
from fastapi.testclient import TestClient

os.environ["INSIGHTBI_DB"] = "test_insightbi_api.db"

from app.database import init_db
from app.main import app

@pytest.fixture(scope="module", autouse=True)
def setup_api_db():
    if os.path.exists("test_insightbi_api.db"):
        os.remove("test_insightbi_api.db")
    init_db()
    yield
    if os.path.exists("test_insightbi_api.db"):
        try:
            os.remove("test_insightbi_api.db")
        except Exception:
            pass

client = TestClient(app)

def test_health_check():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "InsightBI" in data["service"]

def test_get_kpis_api():
    res = client.get("/api/v1/metrics/kpis")
    assert res.status_code == 200
    data = res.json()
    assert data["total_revenue"] > 50000.0
    assert data["total_orders"] >= 30

    # Filtered by Europe
    eu_res = client.get("/api/v1/metrics/kpis?region=Europe")
    assert eu_res.status_code == 200
    eu_data = eu_res.json()
    assert eu_data["total_revenue"] < data["total_revenue"]

def test_get_trends_and_categories_api():
    trends_res = client.get("/api/v1/metrics/trends")
    assert trends_res.status_code == 200
    assert len(trends_res.json()) >= 10

    cat_res = client.get("/api/v1/metrics/categories")
    assert cat_res.status_code == 200
    assert len(cat_res.json()) >= 3

def test_get_filter_options_api():
    res = client.get("/api/v1/metrics/filter-options")
    assert res.status_code == 200
    data = res.json()
    assert "North America" in data["regions"]
    assert "Cloud Services" in data["categories"]
    assert "Enterprise SaaS" in data["channels"]

def test_run_adhoc_query_api():
    payload = {
        "dimension": "region",
        "metric": "profit",
        "sort": "DESC"
    }
    res = client.post("/api/v1/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 4
    assert data[0]["metric"] == "profit"
    assert data[0]["dimension"] == "region"

def test_export_csv_api():
    res = client.get("/api/v1/export/csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    lines = res.text.strip().split("\r\n") if "\r\n" in res.text else res.text.strip().split("\n")
    assert len(lines) >= 30
    assert "Revenue" in lines[0]
    assert "Margin %" in lines[0]
