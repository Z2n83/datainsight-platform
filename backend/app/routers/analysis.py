"""
Analysis router: /api/analysis/*
"""
from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.analysis import AnalysisRequest
from app.services.analysis_service import AnalysisService
from app.services.dataset_service import DatasetService
from app.models.user import User

router = APIRouter()


@router.post("/execute")
async def execute_analysis(
    body: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Execute data analysis (trend / compare / anomaly / ranking).

    POST /api/analysis/execute
    """
    # Verify dataset exists
    ds_svc = DatasetService(db)
    dataset = await ds_svc.get_by_id(body.dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="数据集不存在")

    # Execute analysis
    svc = AnalysisService(db)
    result = await svc.execute(dataset, body.model_dump())

    return {"code": 0, "message": "success", "data": result}
