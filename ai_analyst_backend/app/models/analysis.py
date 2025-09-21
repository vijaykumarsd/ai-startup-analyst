from pydantic import BaseModel
from typing import Dict, List

class AnalysisRequest(BaseModel):
    """
    Request model to start an analysis on an uploaded document.
    """
    file_name: str
    custom_weights: Dict[str, float] = {"team": 0.4, "market": 0.3, "product": 0.3}

class AnalysisResult(BaseModel):
    """
    Response model containing the generated startup analysis.
    """
    file_name: str
    risk_analysis: List[str]
    growth_summary: str
    investment_recommendation: str
    # Corrected peer_benchmarks to expect float values
    peer_benchmarks: Dict[str, float]

class UploadResponse(BaseModel):
    """
    Response model after a file is successfully uploaded.
    """
    file_name: str
    file_size: int
    gcs_path: str
