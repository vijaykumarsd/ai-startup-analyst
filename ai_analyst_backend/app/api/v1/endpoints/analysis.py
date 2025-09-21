from fastapi import APIRouter, Depends, HTTPException
from app.models.analysis import AnalysisRequest, AnalysisResult
from app.services import agent_service

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResult)
async def analyze_document(request: AnalysisRequest):
    """
    Triggers the AI analysis pipeline for a specified document.
    """
    try:
        result = agent_service.run_analysis_pipeline(
            file_name=request.file_name,
            custom_weights=request.custom_weights
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
