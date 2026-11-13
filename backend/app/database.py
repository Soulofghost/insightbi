import sqlite3
import os
from contextlib import contextmanager
from app.config import settings

def get_db_path() -> str:
    return os.environ.get("INSIGHTBI_DB", settings.INSIGHTBI_DB)

@contextmanager
def get_db_connection():
    db_path = get_db_path()
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True) if os.path.dirname(db_path) else None
    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                customer_id TEXT NOT NULL,
                region TEXT NOT NULL,
                channel TEXT NOT NULL,
                category TEXT NOT NULL,
                product_name TEXT NOT NULL,
                units INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                revenue REAL NOT NULL,
                cost REAL NOT NULL,
                profit REAL NOT NULL,
                margin_pct REAL NOT NULL,
                date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_date ON transactions(date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_region ON transactions(region);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_category ON transactions(category);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tx_channel ON transactions(channel);")

        cursor.execute("SELECT count(*) FROM transactions")
        if cursor.fetchone()[0] == 0:
            seed_data = [
                # North America
                ("tx-001", "ORD-1001", "CUST-801", "North America", "Enterprise SaaS", "Cloud Services", "Compute Cluster Tier-4", 10, 450.0, 4500.0, 1800.0, 2700.0, 60.0, "2026-10-01"),
                ("tx-002", "ORD-1002", "CUST-802", "North America", "Direct Online", "Subscriptions", "Developer Pro License", 25, 49.0, 1225.0, 245.0, 980.0, 80.0, "2026-10-04"),
                ("tx-003", "ORD-1003", "CUST-803", "North America", "B2B Wholesale", "Hardware", "Edge Gateway Node-8", 4, 1200.0, 4800.0, 3120.0, 1680.0, 35.0, "2026-10-08"),
                ("tx-004", "ORD-1004", "CUST-804", "North America", "Enterprise SaaS", "Professional Consulting", "Architecture Review", 1, 6500.0, 6500.0, 2600.0, 3900.0, 60.0, "2026-10-12"),
                ("tx-005", "ORD-1005", "CUST-805", "North America", "Direct Online", "Cloud Services", "Object Storage 50TB", 5, 500.0, 2500.0, 750.0, 1750.0, 70.0, "2026-10-15"),
                ("tx-006", "ORD-1006", "CUST-806", "North America", "Retail Partner", "Hardware", "Secure HSM Key Module", 8, 850.0, 6800.0, 4420.0, 2380.0, 35.0, "2026-10-18"),
                ("tx-007", "ORD-1007", "CUST-807", "North America", "Enterprise SaaS", "Subscriptions", "Enterprise Security Suite", 15, 299.0, 4485.0, 897.0, 3588.0, 80.0, "2026-10-22"),
                ("tx-008", "ORD-1008", "CUST-808", "North America", "Direct Online", "Cloud Services", "Serverless Ingestion Unit", 30, 80.0, 2400.0, 720.0, 1680.0, 70.0, "2026-10-25"),
                ("tx-009", "ORD-1009", "CUST-809", "North America", "B2B Wholesale", "Subscriptions", "Team Workspace Annual", 12, 1200.0, 14400.0, 2880.0, 11520.0, 80.0, "2026-10-29"),

                # Europe
                ("tx-010", "ORD-1010", "CUST-810", "Europe", "Enterprise SaaS", "Cloud Services", "Compute Cluster Tier-4", 6, 450.0, 2700.0, 1080.0, 1620.0, 60.0, "2026-10-02"),
                ("tx-011", "ORD-1011", "CUST-811", "Europe", "Retail Partner", "Hardware", "Edge Gateway Node-8", 5, 1200.0, 6000.0, 3900.0, 2100.0, 35.0, "2026-10-06"),
                ("tx-012", "ORD-1012", "CUST-812", "Europe", "Direct Online", "Subscriptions", "Developer Pro License", 40, 49.0, 1960.0, 392.0, 1568.0, 80.0, "2026-10-10"),
                ("tx-013", "ORD-1013", "CUST-813", "Europe", "Enterprise SaaS", "Professional Consulting", "Compliance & GDPR Audit", 1, 7500.0, 7500.0, 3000.0, 4500.0, 60.0, "2026-10-14"),
                ("tx-014", "ORD-1014", "CUST-814", "Europe", "B2B Wholesale", "Cloud Services", "Object Storage 50TB", 8, 500.0, 4000.0, 1200.0, 2800.0, 70.0, "2026-10-17"),
                ("tx-015", "ORD-1015", "CUST-815", "Europe", "Direct Online", "Subscriptions", "Enterprise Security Suite", 8, 299.0, 2392.0, 478.4, 1913.6, 80.0, "2026-10-20"),
                ("tx-016", "ORD-1016", "CUST-816", "Europe", "Enterprise SaaS", "Cloud Services", "Compute Cluster Tier-4", 12, 450.0, 5400.0, 2160.0, 3240.0, 60.0, "2026-10-24"),
                ("tx-017", "ORD-1017", "CUST-817", "Europe", "Retail Partner", "Hardware", "Secure HSM Key Module", 6, 850.0, 5100.0, 3315.0, 1785.0, 35.0, "2026-10-28"),

                # Asia-Pacific
                ("tx-018", "ORD-1018", "CUST-818", "Asia-Pacific", "B2B Wholesale", "Hardware", "Edge Gateway Node-8", 10, 1200.0, 12000.0, 7800.0, 4200.0, 35.0, "2026-10-03"),
                ("tx-019", "ORD-1019", "CUST-819", "Asia-Pacific", "Enterprise SaaS", "Cloud Services", "Compute Cluster Tier-4", 8, 450.0, 3600.0, 1440.0, 2160.0, 60.0, "2026-10-07"),
                ("tx-020", "ORD-1020", "CUST-820", "Asia-Pacific", "Direct Online", "Subscriptions", "Developer Pro License", 50, 49.0, 2450.0, 490.0, 1960.0, 80.0, "2026-10-11"),
                ("tx-021", "ORD-1021", "CUST-821", "Asia-Pacific", "Enterprise SaaS", "Professional Consulting", "Kubernetes Mesh Deployment", 1, 8000.0, 8000.0, 3200.0, 4800.0, 60.0, "2026-10-16"),
                ("tx-022", "ORD-1022", "CUST-822", "Asia-Pacific", "Retail Partner", "Subscriptions", "Team Workspace Annual", 6, 1200.0, 7200.0, 1440.0, 5760.0, 80.0, "2026-10-21"),
                ("tx-023", "ORD-1023", "CUST-823", "Asia-Pacific", "Direct Online", "Cloud Services", "Serverless Ingestion Unit", 40, 80.0, 3200.0, 960.0, 2240.0, 70.0, "2026-10-26"),

                # Latin America
                ("tx-024", "ORD-1024", "CUST-824", "Latin America", "Direct Online", "Subscriptions", "Developer Pro License", 20, 49.0, 980.0, 196.0, 784.0, 80.0, "2026-10-05"),
                ("tx-025", "ORD-1025", "CUST-825", "Latin America", "Enterprise SaaS", "Cloud Services", "Compute Cluster Tier-4", 4, 450.0, 1800.0, 720.0, 1080.0, 60.0, "2026-10-13"),
                ("tx-026", "ORD-1026", "CUST-826", "Latin America", "Retail Partner", "Hardware", "Edge Gateway Node-8", 3, 1200.0, 3600.0, 2340.0, 1260.0, 35.0, "2026-10-19"),
                ("tx-027", "ORD-1027", "CUST-827", "Latin America", "Enterprise SaaS", "Professional Consulting", "SecOps Zero-Trust Setup", 1, 5500.0, 5500.0, 2200.0, 3300.0, 60.0, "2026-10-27"),

                # November Cycles (Multi-period trend validation)
                ("tx-028", "ORD-1028", "CUST-828", "North America", "Enterprise SaaS", "Cloud Services", "Compute Cluster Tier-4", 14, 450.0, 6300.0, 2520.0, 3780.0, 60.0, "2026-11-02"),
                ("tx-029", "ORD-1029", "CUST-829", "North America", "Direct Online", "Subscriptions", "Enterprise Security Suite", 18, 299.0, 5382.0, 1076.4, 4305.6, 80.0, "2026-11-05"),
                ("tx-030", "ORD-1030", "CUST-830", "Europe", "Enterprise SaaS", "Professional Consulting", "AI Pipeline Modernization", 1, 9500.0, 9500.0, 3800.0, 5700.0, 60.0, "2026-11-07"),
                ("tx-031", "ORD-1031", "CUST-831", "Asia-Pacific", "B2B Wholesale", "Hardware", "Edge Gateway Node-8", 12, 1200.0, 14400.0, 9360.0, 5040.0, 35.0, "2026-11-09"),
                ("tx-032", "ORD-1032", "CUST-832", "Latin America", "Enterprise SaaS", "Subscriptions", "Team Workspace Annual", 8, 1200.0, 9600.0, 1920.0, 7680.0, 80.0, "2026-11-11")
            ]

            cursor.executemany("""
                INSERT INTO transactions (
                    id, order_id, customer_id, region, channel, category,
                    product_name, units, unit_price, revenue, cost, profit, margin_pct, date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, seed_data)
            conn.commit()
