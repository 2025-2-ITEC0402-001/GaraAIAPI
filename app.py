# main.py

import uvicorn
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# routers 폴더에서 각 API 라우터를 가져옵니다.
from routers import generate, inpaint, video

app = FastAPI(title="Master Mock API Server")

# --- 비디오 라우터의 설정(정적 파일)을 메인 앱에 적용 ---
# video.py에 정의된 JOBS_DIR 변수를 가져옵니다.
JOBS_DIR = video.JOBS_DIR 
os.makedirs(JOBS_DIR, exist_ok=True)

# /results 경로로 'api_jobs' 폴더를 서빙합니다.
# 원본 /video/results/... 경로를 보존하기 위해 video.router를 먼저 포함합니다.
# 하지만 /results는 /video/results가 아니었으므로 여기서 마운트하는게 맞습니다.
app.mount(f"/{JOBS_DIR}", StaticFiles(directory=JOBS_DIR), name="results")


# --- 각 라우터 포함 ---
# 이제 모든 API가 단일 앱/포트에서 제공됩니다.
app.include_router(generate.router)
app.include_router(inpaint.router)
app.include_router(video.router)

@app.get("/")
def read_root():
    return {
        "message": "All mock APIs are running.",
        "docs_url": "/docs",
        "api_jobs_dir": f"/{JOBS_DIR}"
    }

if __name__ == "__main__":
    # 로컬 테스트 시: python app.py 실행
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)