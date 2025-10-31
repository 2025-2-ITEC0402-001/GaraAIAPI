# routers/inpaint.py

import uvicorn
import asyncio
import io
import os
import logging
# [수정] FastAPI -> APIRouter
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# [수정] app -> router
router = APIRouter()

DUMMY_REVISED_FILE = "dummy_revised.png"

# [수정] @app.on_event -> @router.on_event
@router.on_event("startup")
async def startup_event():
    logger.info("="*50)
    logger.info("MOCK 이미지 수정 API 로드됨")
    if not os.path.exists(DUMMY_REVISED_FILE):
        logger.error(f"!!! {DUMMY_REVISED_FILE} 파일을 찾을 수 없습니다!")
    else:
        logger.info(f"    가짜 응답 파일: {DUMMY_REVISED_FILE}")
    logger.info("="*50)

# [수정] @app.post -> @router.post
# URL 경로는 ('/revise-storyboard') 그대로 유지됩니다.
@router.post("/revise-storyboard", response_class=FileResponse, tags=["Image Inpainting"])
async def revise_storyboard(
    image: UploadFile = File(...), 
    revised_prompt: str = Form(...), 
    strength: float = Form(0.9), 
    guidance_scale: float = Form(3.5), 
    num_inference_steps: int = Form(25), 
    seed: int = Form(0)
):
    logger.info(f"MOCK /revise-storyboard 요청 받음: {revised_prompt[:50]}...")
    await asyncio.sleep(3) # 3초 대기

    try:
        original_image = Image.open(io.BytesIO(await image.read()))
        width, height = original_image.size
        logger.info(f"원본 이미지 로드 성공 (로그용): {width}x{height}")
    except Exception as e:
        logger.error(f"원본 이미지 로드 실패: {e}")

    logger.info("MOCK 이미지 수정 완료. PNG 반환 중...")
    
    if not os.path.exists(DUMMY_REVISED_FILE):
        return JSONResponse(status_code=500, content={"error": f"서버 오류: {DUMMY_REVISED_FILE} 파일을 찾을 수 없습니다."})

    return FileResponse(DUMMY_REVISED_FILE, media_type="image/png")
