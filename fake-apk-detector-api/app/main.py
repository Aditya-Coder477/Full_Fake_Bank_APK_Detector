from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers - make sure these names match your files exactly
from .routes import apk_analysis, url_analysis, bank_verification

app = FastAPI(title="Fake APK Detector API", version="1.0.0")

# Enable CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(apk_analysis.router, prefix="/api/v1", tags=["APK Analysis"])
app.include_router(url_analysis.router, prefix="/api/v1", tags=["URL Analysis"])
app.include_router(bank_verification.router, prefix="/api/v1", tags=["Bank Verification"])

@app.get("/")
async def root():
    return {"message": "Fake APK Detector API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2023-01-01T00:00:00Z"}  # You'll want to use datetime here later

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
