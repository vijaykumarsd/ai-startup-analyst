from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services import agent_service
from app.models.analysis import AnalysisResult
import logging

router = APIRouter()

@router.post("/upload-and-analyze", response_model=AnalysisResult)
async def upload_and_analyze_document(
    file: UploadFile = File(...),
    team_weight: float = Form(0.5),
    market_size_weight: float = Form(0.5)
):
    """
    Accepts a file upload, triggers the full analysis pipeline, 
    and returns the results.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    logging.info(f"Received file: {file.filename} with weights: team={team_weight}, market_size={market_size_weight}")

    try:
        # The agent service will handle the upload and the full analysis pipeline.
        custom_weights = {"team": team_weight, "market_size": market_size_weight}
        
        # The analysis pipeline now needs the file content directly.
        # Let's read the file content here and pass it down.
        # NOTE: This is a deviation from the previous plan where the agent handled the upload.
        # The agent's first step is extraction, which needs a GCS path. So the upload must happen first.
        # The agent orchestrator is the right place to handle the GCS path creation.
        
        # The agent's `run_analysis_pipeline` expects a file_name, not content.
        # The agent itself will construct the GCS path and its first tool will perform the upload.
        # Let's adjust the agent service to handle the upload within the pipeline.

        # Correction: The `run_analysis_pipeline` in agent_service.py already orchestrates
        # everything starting from a file_name. The upload itself is handled by the first tool
        # implicitly via the GCS path. The `documents.py` endpoint should first upload the file,
        # then call the analysis pipeline with the filename.

        from app.services.gcp_clients import gcp_clients
        content = await file.read()
        gcs_path = gcp_clients.upload_to_gcs(file.filename, content)
        logging.info(f"File uploaded to {gcs_path}. Now starting analysis.")

        result = agent_service.run_analysis_pipeline(
            file_name=file.filename,
            custom_weights=custom_weights
        )
        
        logging.info(f"Analysis complete for {file.filename}.")
        return result

    except Exception as e:
        logging.error(f"An error occurred during the upload and analysis process: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
