from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import tempfile
import os
import json
from datetime import datetime
from typing import Optional

# Import your migrated functions
from app.services.apk_analysis import (
    extract_apk_metadata, 
    scan_apk, 
    detect_fraud_keywords,
    simulate_dynamic_analysis,
    generate_apk_dna,
    detect_mimic_apps
)

router = APIRouter()

@router.post("/analyze-apk")
async def analyze_apk(
    file: UploadFile = File(...),
    native_metadata: Optional[str] = Form(None),
    certificate_info: Optional[str] = Form(None),
    permission_info: Optional[str] = Form(None)
):
    """
    Analyze an uploaded APK file using your migrated Streamlit logic
    """
    if not file.filename.endswith('.apk'):
        raise HTTPException(status_code=400, detail="File must be an APK")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".apk") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Parse native-extracted data if provided
        native_data = {}
        if native_metadata:
            native_data["metadata"] = json.loads(native_metadata)
        if certificate_info:
            native_data["certificate"] = json.loads(certificate_info)
        if permission_info:
            native_data["permissions"] = json.loads(permission_info)
        
        # Extract metadata from APK (use native data if available)
        if native_data.get("metadata"):
            metadata = native_data["metadata"]
            metadata["file_size"] = os.path.getsize(tmp_path) / (1024 * 1024)
        else:
            metadata = extract_apk_metadata(tmp_path)
        
        # Enhance metadata with native data if available
        if native_data.get("certificate"):
            if "certificate" not in metadata:
                metadata["certificate"] = {}
            metadata["certificate"]["hash"] = native_data["certificate"].get("sha256", "")
            metadata["certificate"]["sha1"] = native_data["certificate"].get("sha1", "")
        
        if native_data.get("permissions"):
            metadata["permissions"] = native_data["permissions"].get("permissions", [])
            metadata["dangerous_permissions"] = native_data["permissions"].get("dangerousPermissions", [])
        
        # Perform analysis using your migrated Streamlit functions
        result = scan_apk(metadata, tmp_path)
        
        # Add additional analysis
        result["fraud_keywords"] = detect_fraud_keywords(metadata.get("app_name", ""))[0]
        result["dynamic_analysis"] = simulate_dynamic_analysis(tmp_path, metadata)
        result["apk_dna"] = generate_apk_dna(tmp_path, metadata)
        result["mimic_detection"] = detect_mimic_apps(result["apk_dna"], metadata)
        result["native_analysis_used"] = bool(native_data)
        
        return JSONResponse({
            "success": True,
            "result": result,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status_code=500)
    finally:
        # Clean up
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
            
            
            
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
from datetime import datetime
from typing import Optional

from app.services.apk_analysis import (
    extract_apk_metadata, 
    scan_apk, 
    detect_fraud_keywords,
    simulate_dynamic_analysis,
    generate_apk_dna,
    detect_mimic_apps
)

router = APIRouter()

@router.post("/analyze-apk")
async def analyze_apk(
    file: UploadFile = File(...),
    native_metadata: Optional[str] = None,
    certificate_info: Optional[str] = None,
    permission_info: Optional[str] = None
):
    """
    Analyze an uploaded APK file, optionally using native-extracted data
    """
    if not file.filename.endswith('.apk'):
        raise HTTPException(status_code=400, detail="File must be an APK")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".apk") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Parse native-extracted data if provided
        native_data = {}
        if native_metadata:
            import json
            native_data["metadata"] = json.loads(native_metadata)
        if certificate_info:
            native_data["certificate"] = json.loads(certificate_info)
        if permission_info:
            native_data["permissions"] = json.loads(permission_info)
        
        # Extract metadata from APK (use native data if available)
        if native_data.get("metadata"):
            metadata = native_data["metadata"]
            # Add additional metadata that might not be available natively
            metadata["file_size"] = os.path.getsize(tmp_path) / (1024 * 1024)
        else:
            metadata = extract_apk_metadata(tmp_path)
        
        # Enhance metadata with native certificate info if available
        if native_data.get("certificate"):
            if "certificate" not in metadata:
                metadata["certificate"] = {}
            metadata["certificate"]["hash"] = native_data["certificate"].get("sha256", "")
            metadata["certificate"]["sha1"] = native_data["certificate"].get("sha1", "")
        
        # Enhance with native permission info if available
        if native_data.get("permissions"):
            metadata["permissions"] = native_data["permissions"].get("permissions", [])
            metadata["dangerous_permissions"] = native_data["permissions"].get("dangerousPermissions", [])
        
        # Perform analysis
        result = scan_apk(metadata, tmp_path)
        
        # Add additional analysis
        result["fraud_keywords"] = detect_fraud_keywords(metadata.get("app_name", ""))[0]
        result["dynamic_analysis"] = simulate_dynamic_analysis(tmp_path, metadata)
        result["apk_dna"] = generate_apk_dna(tmp_path, metadata)
        result["mimic_detection"] = detect_mimic_apps(result["apk_dna"], metadata)
        result["native_analysis_used"] = bool(native_data)
        
        return JSONResponse({
            "success": True,
            "result": result,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }, status_code=500)
    finally:
        # Clean up
        os.unlink(tmp_path)