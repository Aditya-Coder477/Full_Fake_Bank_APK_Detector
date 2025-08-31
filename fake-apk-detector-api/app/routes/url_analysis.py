from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict

router = APIRouter()

@router.post("/analyze-url")
async def analyze_url(url_data: Dict[str, str]):
    """
    Analyze a URL for potential threats (from WhatsApp/SMS)
    """
    try:
        url = url_data.get("url", "")
        source = url_data.get("source", "unknown")
        
        # Simple simulation - you'll add real logic later
        is_suspicious = any(domain in url for domain in ['.xyz', '.top', '.club'])
        risk_score = 75 if is_suspicious else 15
        
        return JSONResponse({
            "success": True,
            "result": {
                "safe": not is_suspicious,
                "risk_score": risk_score,
                "suspicious_reason": "Suspicious domain detected" if is_suspicious else "No threats detected",
                "url": url,
                "source": source
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status_code=500)