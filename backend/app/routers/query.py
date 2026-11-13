from fastapi import APIRouter
from typing import List
from app.schemas import AdhocQueryRequest, AdhocQueryResultItem
from app.engine.analytics import execute_adhoc_query

router = APIRouter(prefix="/query", tags=["Ad-hoc BI Query Engine"])

@router.post("", response_model=List[AdhocQueryResultItem])
def run_adhoc_query(req: AdhocQueryRequest):
    filters = {
        "region": req.region,
        "category": req.category,
        "channel": req.channel,
        "start_date": req.start_date,
        "end_date": req.end_date
    }
    return execute_adhoc_query(
        dimension=req.dimension,
        metric=req.metric,
        filters=filters,
        sort=req.sort or "DESC",
        limit=req.limit or 50
    )
