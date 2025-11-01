# GaraAIAPI

이미지/영상 AI API **프론트엔드/백엔드 연동 개발 및 통합 테스트**를 위해 구축된 **모의(Mock) API 서버**. 
실제 고성능 AI 모델의 실행 없이, 고정된 더미 응답을 빠르게 반환하여 개발 속도를 높이는 것을 목표로 함.   

---
##  API 엔드포인트 개요

이 Mock 서버는 영상 생성 파이프라인의 3단계(이미지 생성, 이미지 수정, 영상 생성) 모방

### 1. 이미지 생성 (Storyboard Generation)

| 역할 | 엔드포인트 | 메소드 | 입력 유형 | 출력 유형 | 특징 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Generate** | `/generate-storyboard` | POST | **JSON** (Prompt, Size) | **PNG File** | Prompt에 관계없이 고정된 `dummy_generated.png` 파일을 반환하며, 응답 전에 **10초 지연**이 있음. |

### 2. 이미지 수정 (Inpainting/Revision)

| 역할 | 엔드포인트 | 메소드 | 입력 유형 | 출력 유형 | 특징 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Revise** | `/revise-storyboard` | POST | **Multipart** (Image File + Form Data) | **PNG File** | 업로드된 이미지를 받아, 고정된 `dummy_revised.png` 파일을 반환하며, 응답 전에 **3초 지연**이 있음. |  

### 3. 영상 생성 (Video Generation)

| 역할 | 엔드포인트 | 메소드 | 입력 유형 | 출력 유형 | 특징 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Request** | `/generate` | POST | **Multipart** (3 Files + Form Data) | **JSON** (Job ID) | 비동기 작업을 시작하고, 작업이 완료되는 데 **10초**가 소요됩니다. |
| **Status** | `/status/{job_id}` | GET | **Path Param** (Job ID) | **JSON** (Status) | 작업 완료 시 `api_jobs/{job_id}/output/generated_video.mp4` 경로를 가리키는 URL을 반환. | 
| **Download** | `/api_jobs/{path_to_file}` | GET | **URL Path** | **Video File** | 반환된 URL 경로를 통해 최종 영상을 다운로드. |

---
## 4. 테스트 예시 (Curl)   
어떤 값을 입력하든(프롬프트 등) 동일한 값 반환. 확장자 형식만 갖춘 쓰레기 값 넘겨주면 됨.

### 1. 이미지 생성 테스트  

```bash
# 10초 후 더미 PNG 파일이 output.png로 저장됨.
curl -X POST 'http://localhost:8000/generate-storyboard' \
-H "Content-Type: application/json" \
-d '{"prompt": "A cute cat programmer..."}' \
--output output.png
```

<img width="1057" height="580" alt="image" src="https://github.com/user-attachments/assets/0f215837-c3cb-4614-9404-691a0775a33e" />  


### 2. 이미지 수정 테스트
```bash
curl -X POST 'http://localhost:8000/revise-storyboard' \
-F 'image=@output.png' \
-F 'revised_prompt=cat is wearing a wizard hat' \
-F 'strength=0.9' \
-F 'guidance_scale=3.5' \
-F 'num_inference_steps=25' \
-F 'seed=0' \
--output revised_output.png
```  
<img width="932" height="662" alt="image" src="https://github.com/user-attachments/assets/cae10953-bac9-4233-bb3a-2c5fc2d781e0" />  

### 3. 영상 생성 테스트 (비동기)
(테스트를 위해 `origin.jpg`, `mask.png`, `traj.json`이라는 더미 파일이 필요.
그냥 쓰레기 값 들어도 됨. 그냥 저 확장자 가지고 있음 됨)   

- 작업 요청 (Job ID 반환):
```Bash
curl -X POST 'http://localhost:8000/generate' \
-F 'origin_image=@origin.jpg' \
-F 'sam_mask=@mask.png' \
-F 'trajectory_data=@traj.json' \
-F 'frame_number=14'
(응답 예시: {"status": "processing", "job_id": "UUID-HERE", "status_url": "/status/UUID-HERE"})
```  
<img width="727" height="181" alt="image" src="https://github.com/user-attachments/assets/154cbad4-a064-42b5-a106-e81cb608810b" />  

  
응답 예시: `{"status": "processing", "job_id": "UUID-HERE", "status_url": "/status/UUID-HERE"}`  


- 작업 상태 확인 (10초 후 재시도):  
  
```Bash
curl 'http://localhost:8000/status/UUID-HERE'
(완료 응답 예시: {"status": "complete", "video_url": "/api_jobs/UUID-HERE/output/generated_video.mp4"})
```
<img width="727" height="125" alt="image" src="https://github.com/user-attachments/assets/20a88a85-0c0d-4191-9fdb-2a211a03cf22" />  


- 최종 영상 다운로드:
```bash
# {UUID-HERE} 자리에 Job ID를 넣어 전체 경로로 GET 요청 보냄
# 다운로드 시 반드시 --output 옵션을 사용하여 파일로 저장해야 함.
curl -X GET "http://localhost:8000/api_jobs/{UUID-HERE}/output/generated_video.mp4" --output final_video.mp4
```
```bash
curl -X GET "http://localhost:8000/api_jobs/{UUID-HERE}/output/generated_video.mp4" --output final_video.mp4
```
<img width="590" height="742" alt="image" src="https://github.com/user-attachments/assets/2a98643b-02d9-425c-a239-4e7ed8eb73e7" />  


