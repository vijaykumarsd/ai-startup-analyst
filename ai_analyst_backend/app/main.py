from fastapi import FastAPI
from app.api.v1.endpoints import documents
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Analyst for Startup Evaluation")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows the React frontend to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the new, combined documents router
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Analyst API"}
