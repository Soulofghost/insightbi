import csv
import io
from fastapi import APIRouter, Response
from typing import Optional
from app.database import get_db_connection
from app.engine.analytics import build_filter_clause

router = APIRouter(prefix="/export", tags=["Data Export"])

@router.get("/csv")
def export_csv(
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
    where_clause, params = build_filter_clause(filters)
    query = f"SELECT * FROM transactions WHERE {where_clause} ORDER BY date DESC"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Order ID", "Customer ID", "Region", "Channel", "Category",
        "Product Name", "Units", "Unit Price", "Revenue", "Cost", "Profit", "Margin %", "Date"
    ])

    for r in rows:
        writer.writerow([
            r["id"], r["order_id"], r["customer_id"], r["region"], r["channel"], r["category"],
            r["product_name"], r["units"], r["unit_price"], r["revenue"], r["cost"], r["profit"], r["margin_pct"], r["date"]
        ])

    csv_data = output.getvalue()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=insightbi_transactions_export.csv"}
    )
