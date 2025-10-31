# routers/video.py

import uvicorn
import shutil
import os
import uuid
import time
import traceback
# [수정] FastAPI -> APIRouter
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import JSONResponse
# [삭제] StaticFiles는 main.py에서 처리하므로 삭제

# [수정] app -> router
router = APIRouter()

# [수정] 이 변수들은 main.py에서 참조할 수 있도록 바깥에 둡니다.
JOBS_DIR = "api_jobs" 
DUMMY_VIDEO_FILE = "dummy_video.mp4"
job_db = {} # 모든 작업 상태를 저장 (단일 프로세스이므로 문제 없음)

# [삭제] app.mount(...) 코드는 main.py로 이동했으므로 삭제

# [수정] @app.on_event -> @router.on_event
@router.on_event("startup")
async def startup_event():
    print("="*50)
    print("MOCK 영상 생성 API 로드됨")
    if not os.path.exists(DUMMY_VIDEO_FILE):
        print(f"!!! 치명적 오류: {DUMMY_VIDEO_FILE} 파일을 찾을 수 없습니다!")
    else:
        print(f"    가짜 응답 파일: {DUMMY_VIDEO_FILE}")
    print(f"작업 폴더: {os.path.abspath(JOBS_DIR)}")
    print("="*50)

# (run_mock_generation_task 함수는 변경 없음)
def run_mock_generation_task(job_id: str, job_dir: str, frame_number: int):
    global job_db
    try:
        print(f"[Job {job_id}] MOCK 백그라운드 작업 시작... (10초 대기)")
        time.sleep(10) 
        print(f"[Job {job_id}] MOCK 작업 완료. 가짜 비디오 파일 복사 중...")
        
        output_video_dir = os.path.join(job_dir, "output")
        os.makedirs(output_video_dir, exist_ok=True)
        output_video_path = os.path.join(output_video_dir, "generated_video.mp4")
        
        if not os.path.exists(DUMMY_VIDEO_FILE):
            raise FileNotFoundError(f"{DUMMY_VIDEO_FILE} not found")

        shutil.copyfile(DUMMY_VIDEO_FILE, output_video_path)

        relative_video_url = os.path.relpath(output_video_path, JOBS_DIR)
        
        job_db[job_id] = {
            "status": "complete",
            # [수정] main.py에서 마운트한 경로를 사용합니다.
            "video_url": f"/{JOBS_DIR}/{relative_video_url.replace(os.path.sep, '/')}"
        }
        print(f"[Job {job_id}] 작업 완료. 비디오: {output_video_path}")
    except Exception as e:
        error_message = traceback.format_exc()
        print(f"[Job {job_id}] MOCK 작업 실패: {error_message}")
        job_db[job_id] = {"status": "error", "message": str(e)}

# --- API 엔드포인트 ---
# [수정] @app -> @router
# URL 경로는 ('/generate', '/status/{job_id}' 등) 그대로 유지됩니다.

@router.post("/generate", summary="비디오 생성 요청 (비동기)", tags=["Video Generation"])
async def start_generation(
    background_tasks: BackgroundTasks,
    origin_image: UploadFile = File(...),
    sam_mask: UploadFile = File(...),
    trajectory_data: UploadFile = File(...),
    frame_number: int = Form(14, description="생성할 총 프레임 수 (Mock에서는 무시됨)") 
):
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(JOBS_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    print(f"[Job {job_id}] 요청 수신. 파일 저장 위치: {job_dir}")

    image_path = os.path.join(job_dir, "origin_image.jpg") 
    mask_path = os.path.join(job_dir, "mask.png")
    traj_path = os.path.join(job_dir, "trajectory.json")
    try:
        with open(image_path, "wb") as f: shutil.copyfileobj(origin_image.file, f)
        with open(mask_path, "wb") as f: shutil.copyfileobj(sam_mask.file, f)
        with open(traj_path, "wb") as f: shutil.copyfileobj(trajectory_data.file, f)
        print(f"[Job {job_id}] 입력 파일 3개 저장 완료.")
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": f"파일 저장 실패: {e}"})
    finally:
        origin_image.file.close()
        sam_mask.file.close()
        trajectory_data.file.close()

    job_db[job_id] = {"status": "processing"}
    background_tasks.add_task(run_mock_generation_task, job_id, job_dir, frame_number)

    return {
        "status": "processing",
        "job_id": job_id,
        "status_url": f"/status/{job_id}" # 경로는 그대로 유지됨
    }


@router.get("/status/{job_id}", summary="작업 상태 확인", tags=["Video Generation"])
async def get_job_status(job_id: str):
    print(f"상태 확인 요청: {job_id}")
    status = job_db.get(job_id)
    if not status:
        return JSONResponse(status_code=404, content={"status": "error", "message": "Job ID를 찾을 수 없습니다."})
    return status

@router.get("/api-health", summary="API 상태 확인", tags=["Video Generation"])
async def root():
    return {"message": "MOCK Motion Generation API가 로드되었습니다.", "model_loaded": "mock"}
