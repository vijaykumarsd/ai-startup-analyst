from app.services.gcp_clients import gcp_clients
from app.models.analysis import AnalysisResult
from app.core.config import settings

# --- Agentic Tools ---

def intelligent_data_extraction(gcs_path: str) -> str:
    """
    Tool 1: Extracts text from a document in GCS using the real Vision API.
    """
    print(f"AGENT_TOOL: Running intelligent_data_extraction on {gcs_path}")
    extracted_text = gcp_clients.extract_text_with_vision(gcs_path)
    return extracted_text

def dynamic_peer_benchmarking(sector: str = "SaaS") -> dict:
    """
    Tool 2: Queries BigQuery to get peer benchmarks for a given sector.
    """
    print(f"AGENT_TOOL: Running dynamic_peer_benchmarking for sector '{sector}'")
    table_id = f"`{settings.PROJECT_ID}.{settings.BIGQUERY_DATASET}.peer_data`"
    benchmark_query = f"SELECT AVG(team_size) as avg_team_size, AVG(seed_round) as avg_seed_round FROM {table_id} WHERE sector = '{sector}'"
    benchmarks = gcp_clients.query_bigquery(benchmark_query)
    return benchmarks

def rag_and_insight_generation(extracted_text: str, benchmarks: dict, custom_weights: dict) -> dict:
    """
    Tool 3: Generates insights using a RAG approach with the real Gemini Pro model.
    """
    print("AGENT_TOOL: Running rag_and_insight_generation")
    prompt = f"""
    Analyze the following startup based on its pitch deck text and peer benchmarks.
    Custom investor weights: {custom_weights}
    Extracted Text: {extracted_text[:10000]}...
    Benchmarks: {benchmarks}
    Generate a risk analysis, growth summary, and investment recommendation.
    """
    # This now calls the real Gemini implementation
    generated_insights = gcp_clients.generate_with_gemini(prompt)
    return generated_insights

# --- Agentic Orchestrator ---
def run_agentic_analysis(file_name: str, custom_weights: dict) -> AnalysisResult:
    """
    This agent orchestrates the analysis by using a predefined set of tools.
    """
    print(f"AGENT: Starting analysis for {file_name} with weights {custom_weights}")
    gcs_path = f"gs://{settings.BUCKET_NAME}/{file_name}"

    available_tools = {
        "intelligent_data_extraction": intelligent_data_extraction,
        "dynamic_peer_benchmarking": dynamic_peer_benchmarking,
        "rag_and_insight_generation": rag_and_insight_generation,
    }

    plan = [
        {"tool": "intelligent_data_extraction", "params": {"gcs_path": gcs_path}, "output": "extracted_text"},
        {"tool": "dynamic_peer_benchmarking", "params": {"sector": "SaaS"}, "output": "benchmarks"},
        {"tool": "rag_and_insight_generation", "params": {"custom_weights": custom_weights, "extracted_text": "extracted_text", "benchmarks": "benchmarks"}, "output": "generated_insights"},
    ]

    execution_context = {}
    for step in plan:
        tool_name = step["tool"]
        tool_function = available_tools[tool_name]

        params = {}
        for param_name, param_value in step["params"].items():
            if isinstance(param_value, str) and param_value in execution_context:
                params[param_name] = execution_context[param_value]
            else:
                params[param_name] = param_value
        
        result = tool_function(**params)
        execution_context[step["output"]] = result

    print("AGENT: Analysis complete.")

    generated_insights = execution_context["generated_insights"]
    benchmarks = execution_context["benchmarks"]

    return AnalysisResult(
        file_name=file_name,
        risk_analysis=generated_insights["risk_analysis"],
        growth_summary=generated_insights["growth_summary"],
        investment_recommendation=generated_insights["investment_recommendation"],
        peer_benchmarks=benchmarks
    )

# --- Main Entry Point ---

def run_analysis_pipeline(file_name: str, custom_weights: dict) -> AnalysisResult:
    """
    Main entry point for the analysis pipeline.
    """
    return run_agentic_analysis(file_name, custom_weights)
