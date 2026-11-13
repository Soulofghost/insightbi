from typing import Dict, Any, List, Optional
from app.database import get_db_connection

VALID_DIMENSIONS = {"region", "channel", "category", "product_name", "date"}
VALID_METRICS = {
    "revenue": "SUM(revenue)",
    "profit": "SUM(profit)",
    "units": "SUM(units)",
    "orders": "COUNT(*)",
    "avg_order_value": "AVG(revenue)",
    "avg_margin": "AVG(margin_pct)"
}

def build_filter_clause(filters: Dict[str, Any]) -> (str, list):
    clauses = ["1=1"]
    params = []

    if filters.get("region"):
        clauses.append("region = ?")
        params.append(filters["region"])
    if filters.get("category"):
        clauses.append("category = ?")
        params.append(filters["category"])
    if filters.get("channel"):
        clauses.append("channel = ?")
        params.append(filters["channel"])
    if filters.get("start_date"):
        clauses.append("date >= ?")
        params.append(filters["start_date"])
    if filters.get("end_date"):
        clauses.append("date <= ?")
        params.append(filters["end_date"])

    return " AND ".join(clauses), params

def compute_kpis(filters: Dict[str, Any]) -> Dict[str, Any]:
    where_clause, params = build_filter_clause(filters)
    query = f"""
        SELECT 
            COUNT(*) as total_orders,
            COALESCE(SUM(revenue), 0.0) as total_revenue,
            COALESCE(SUM(cost), 0.0) as total_cost,
            COALESCE(SUM(profit), 0.0) as total_profit,
            COALESCE(SUM(units), 0) as total_units,
            COUNT(DISTINCT customer_id) as unique_customers,
            COALESCE(AVG(revenue), 0.0) as avg_order_value
        FROM transactions
        WHERE {where_clause}
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        row = cursor.fetchone()

        rev = float(row["total_revenue"])
        profit = float(row["total_profit"])
        cost = float(row["total_cost"])
        margin_pct = round((profit / rev * 100.0), 2) if rev > 0 else 0.0

        return {
            "total_orders": int(row["total_orders"]),
            "total_revenue": round(rev, 2),
            "total_cost": round(cost, 2),
            "total_profit": round(profit, 2),
            "blended_margin_pct": margin_pct,
            "total_units": int(row["total_units"]),
            "unique_customers": int(row["unique_customers"]),
            "avg_order_value": round(float(row["avg_order_value"]), 2)
        }

def get_revenue_trends(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(filters)
    query = f"""
        SELECT 
            date,
            SUM(revenue) as daily_revenue,
            SUM(profit) as daily_profit,
            SUM(units) as daily_units,
            COUNT(*) as daily_orders
        FROM transactions
        WHERE {where_clause}
        GROUP BY date
        ORDER BY date ASC
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [
            {
                "date": r["date"],
                "revenue": round(float(r["daily_revenue"]), 2),
                "profit": round(float(r["daily_profit"]), 2),
                "units": int(r["daily_units"]),
                "orders": int(r["daily_orders"])
            }
            for r in rows
        ]

def get_category_breakdown(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(filters)
    query = f"""
        SELECT 
            category,
            SUM(revenue) as category_revenue,
            SUM(profit) as category_profit,
            SUM(units) as category_units,
            COUNT(*) as order_count,
            AVG(margin_pct) as avg_margin
        FROM transactions
        WHERE {where_clause}
        GROUP BY category
        ORDER BY category_revenue DESC
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [
            {
                "category": r["category"],
                "revenue": round(float(r["category_revenue"]), 2),
                "profit": round(float(r["category_profit"]), 2),
                "units": int(r["category_units"]),
                "orders": int(r["order_count"]),
                "margin_pct": round(float(r["avg_margin"]), 2)
            }
            for r in rows
        ]

def get_regional_performance(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    where_clause, params = build_filter_clause(filters)
    query = f"""
        SELECT 
            region,
            SUM(revenue) as region_revenue,
            SUM(profit) as region_profit,
            COUNT(*) as order_count,
            AVG(revenue) as aov
        FROM transactions
        WHERE {where_clause}
        GROUP BY region
        ORDER BY region_revenue DESC
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [
            {
                "region": r["region"],
                "revenue": round(float(r["region_revenue"]), 2),
                "profit": round(float(r["region_profit"]), 2),
                "orders": int(r["order_count"]),
                "avg_order_value": round(float(r["aov"]), 2)
            }
            for r in rows
        ]

def execute_adhoc_query(dimension: str, metric: str, filters: Dict[str, Any], sort: str = "DESC", limit: int = 50) -> List[Dict[str, Any]]:
    dim = dimension.lower() if dimension.lower() in VALID_DIMENSIONS else "category"
    metric_key = metric.lower() if metric.lower() in VALID_METRICS else "revenue"
    metric_expr = VALID_METRICS[metric_key]
    sort_dir = "ASC" if sort.upper() == "ASC" else "DESC"

    where_clause, params = build_filter_clause(filters)
    query = f"""
        SELECT 
            {dim} as dimension_value,
            {metric_expr} as metric_value,
            COUNT(*) as count_rows,
            SUM(revenue) as total_rev
        FROM transactions
        WHERE {where_clause}
        GROUP BY {dim}
        ORDER BY metric_value {sort_dir}
        LIMIT ?
    """
    params.append(limit)

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [
            {
                "dimension": dim,
                "dimension_value": r["dimension_value"],
                "metric": metric_key,
                "metric_value": round(float(r["metric_value"]), 2) if isinstance(r["metric_value"], (int, float)) else r["metric_value"],
                "transaction_count": int(r["count_rows"]),
                "total_revenue": round(float(r["total_rev"]), 2)
            }
            for r in rows
        ]
