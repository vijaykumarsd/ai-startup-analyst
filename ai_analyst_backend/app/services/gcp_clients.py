from google.cloud import storage, vision, bigquery
from google.cloud.exceptions import NotFound
# --- NEW: Import the Google AI/Gemini library ---
import google.generativeai as genai
from app.core.config import settings
import logging
import time
import json

logging.basicConfig(level=logging.INFO)

class GCPClients:
    def __init__(self):
        # Service Account is still used for GCS, Vision, and BigQuery
        try:
            self.storage_client = storage.Client(project=settings.PROJECT_ID)
            logging.info("Successfully initialized Google Cloud Storage client.")
        except Exception as e:
            logging.error(f"Failed to initialize GCS client: {e}", exc_info=True)
            self.storage_client = None

        try:
            self.vision_client = vision.ImageAnnotatorClient()
            logging.info("Successfully initialized Google Cloud Vision client.")
        except Exception as e:
            logging.error(f"Failed to initialize Vision client: {e}", exc_info=True)
            self.vision_client = None

        try:
            self.bigquery_client = bigquery.Client(project=settings.PROJECT_ID)
            logging.info("Successfully initialized Google BigQuery client.")
            self.setup_bigquery_benchmarks()
        except Exception as e:
            logging.error(f"Failed to initialize BigQuery client: {e}", exc_info=True)
            self.bigquery_client = None

        # --- REMOVED: Vertex AI Initialization ---
        # --- NEW: Configure the Gemini API key ---
        try:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is not set in the environment.")
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel("gemini-1.5-flash-002")
            logging.info("Successfully initialized Google AI (Gemini) client.")
        except Exception as e:
            logging.error(f"Failed to initialize Google AI (Gemini) client: {e}", exc_info=True)
            self.gemini_model = None

    def generate_with_gemini(self, prompt: str) -> dict:
        """Generates insights using the Gemini API (Google AI Studio)."""
        if not self.gemini_model:
            logging.error("Gemini model is not available. Returning mock data.")
            return self.mock_generate_with_gemini(prompt)

        try:
            logging.info("Generating insights with Gemini API (Google AI Studio)...")
            full_prompt = f"""{prompt}

            Please provide the output in a valid JSON format with the following keys:
            - "risk_analysis": list of strings
            - "growth_summary": string
            - "investment_recommendation": string
            """
            
            response = self.gemini_model.generate_content(full_prompt)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)

        except Exception as e:
            logging.error(f"Failed to generate insights with Gemini: {e}", exc_info=True)
            raise

    def setup_bigquery_benchmarks(self):
        if not self.bigquery_client: return
        try:
            table_id = f"{settings.PROJECT_ID}.{settings.BIGQUERY_DATASET}.peer_data"
            try: self.bigquery_client.get_table(table_id); return
            except NotFound: pass
            schema = [bigquery.SchemaField("sector", "STRING"), bigquery.SchemaField("team_size", "INTEGER"), bigquery.SchemaField("seed_round", "INTEGER")]
            table = bigquery.Table(table_id, schema=schema)
            self.bigquery_client.create_table(table)
            rows_to_insert = [{"sector": "SaaS", "team_size": 5, "seed_round": 2000000}, {"sector": "SaaS", "team_size": 8, "seed_round": 3000000}, {"sector": "FinTech", "team_size": 10, "seed_round": 5000000}, {"sector": "HealthTech", "team_size": 4, "seed_round": 1500000}]
            self.bigquery_client.insert_rows_json(table, rows_to_insert)
        except Exception as e: logging.error(f"Failed to set up BigQuery benchmarks: {e}", exc_info=True)

    def query_bigquery(self, query: str) -> dict:
        if not self.bigquery_client: return self.mock_query_bigquery(query)
        try:
            query_job = self.bigquery_client.query(query)
            results = query_job.result()
            if results.total_rows > 0: return dict(list(results)[0].items())
            else: return {}
        except Exception as e: logging.error(f"Failed to execute BigQuery query: {e}", exc_info=True); raise

    def upload_to_gcs(self, file_name: str, content: bytes) -> str:
        if not self.storage_client: return self.mock_upload_to_gcs(file_name, content)
        try:
            bucket = self.storage_client.get_bucket(settings.BUCKET_NAME)
            blob = bucket.blob(file_name)
            blob.upload_from_string(content, content_type="application/pdf")
            return f"gs://{settings.BUCKET_NAME}/{file_name}"
        except Exception as e: logging.error(f"Failed to upload to GCS: {e}", exc_info=True); raise

    def extract_text_with_vision(self, gcs_path: str) -> str:
        if not self.vision_client or not self.storage_client: return self.mock_extract_text_with_vision(gcs_path)
        try:
            gcs_source = vision.GcsSource(uri=gcs_path)
            feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
            gcs_destination = vision.GcsDestination(uri=f"gs://{settings.BUCKET_NAME}/vision-output/")
            output_config = vision.OutputConfig(gcs_destination=gcs_destination, batch_size=2)
            async_request = vision.AsyncAnnotateFileRequest(features=[feature], input_config=vision.InputConfig(gcs_source=gcs_source, mime_type="application/pdf"), output_config=output_config)
            operation = self.vision_client.async_batch_annotate_files(requests=[async_request])
            operation.result(timeout=420)
            bucket = self.storage_client.get_bucket(settings.BUCKET_NAME)
            blob_list = list(bucket.list_blobs(prefix="vision-output/"))
            full_text = ""
            original_file_name = gcs_path.split('/')[-1]
            for blob in blob_list:
                if original_file_name in blob.name:
                    json_string = blob.download_as_string()
                    response = json.loads(json_string)
                    for page_response in response["responses"]:
                        full_text += page_response.get("fullTextAnnotation", {}).get("text", "")
                    blob.delete()
                    break
            return full_text
        except Exception as e: logging.error(f"Failed to extract text with Vision API: {e}", exc_info=True); raise

    # --- Mock Functions ---
    def mock_generate_with_gemini(self, prompt):
        logging.warning("MOCK - Generating insights with Gemini...")
        return {"risk_analysis": ["Mocked risk"], "growth_summary": "Mocked summary", "investment_recommendation": "Mocked recommendation"}

# Singleton instance
gcp_clients = GCPClients()
