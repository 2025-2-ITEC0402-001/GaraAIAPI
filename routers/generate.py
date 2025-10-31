# routers/generate.py

import uvicorn
import asyncio
import os
import logging
# [수정] FastAPI 대신 APIRouter를 가져옵니다.
from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# [수정] app = FastAPI() 대신 router = APIRouter()
router = APIRouter()

DUMMY_IMAGE_FILE = "dummy_generated.png"

# (StoryboardRequest 모델은 변경 없음)
class StoryboardRequest(BaseModel):
    prompt: str
    height: int = 1536
    width: int = 1024
    guidance_scale: float = 3.5
    num_inference_steps: int = 20
    seed: int = 0

# [수정] @app.on_event -> @router.on_event
@router.on_event("startup")
async def startup_event():
    logger.info("="*50)
    logger.info("MOCK 이미지 생성 API 로드됨")
    if not os.path.exists(DUMMY_IMAGE_FILE):
        logger.error(f"!!! {DUMMY_IMAGE_FILE} 파일을 찾을 수 없습니다!")
    else:
        logger.info(f"    가짜 응답 파일: {DUMMY_IMAGE_FILE}")
    logger.info("="*50)

# [수정] @app.post -> @router.post
# URL 경로는 ('/generate-storyboard') 그대로 유지됩니다.
@router.post("/generate-storyboard", response_class=FileResponse, tags=["Image Generation"])
async def generate_storyboard(request: StoryboardRequest):
    logger.info(f"MOCK /generate-storyboard 요청 받음: {request.prompt[:50]}...")
    await asyncio.sleep(20) # 20초 대기
    logger.info("MOCK 이미지 생성 완료. PNG 반환 중...")
    
    if not os.path.exists(DUMMY_IMAGE_FILE):
        return JSONResponse(status_code=500, content={"error": f"서버 오류: {DUMMY_IMAGE_FILE} 파일을 찾을 수 없습니다."})
        
    return FileResponse(DUMMY_IMAGE_FILE, media_type="image/png")
