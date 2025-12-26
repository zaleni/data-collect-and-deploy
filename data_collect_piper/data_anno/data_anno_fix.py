from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
import random
import uvicorn
from typing import Final, List
import os
from task import TaskManager, TaskDirectory, Task, TaskEntryView
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO
from fastapi.responses import FileResponse, StreamingResponse
from pathlib import Path
import time
from log_filter import PngFilePathFilter

task_manager = TaskManager()
task_manager.listen_file_system()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法（GET/POST等）
    allow_headers=["*"],  # 允许所有请求头
)

BackUpDirectory: Final[Path] = Path("backup")


@app.get("/api/get_task_list", response_model=List[TaskEntryView])
async def get_task_list():
    return list(task_manager.Tasks.values())

@app.get("/api/get_task")
async def get_task(task_name):
    # task_path : Path = TaskDirectory / task_name
    if task_name in task_manager.Tasks:
        task = task_manager.Tasks[task_name]
        return task 
    else:
        return {"err": "request task does not exist"}
    
@app.post("/api/update_task")
async def update_task(task: Task):
    res = task_manager.save_task(task)
    with open(BackUpDirectory / f'{task.task_name.replace("/", "_")}_{str(time.time()).replace(".", "")}.json', 'w') as f:
        f.write(task.model_dump_json(indent=2))
    if res:
        return {"err": res}
    else:
        return {"msg": "success"}   
    
@app.post("/api/reload")
async def reload():
    task_manager.reload()
    return {"msg": "success"}

from fastapi import HTTPException

@app.get("/api/list_images")
async def list_images(
    task_name: str,
    img_type: str,   # front_color / wrist_color / front_depth / wrist_depth
):
    dir_path = Path(TaskDirectory) / task_name / "img" / img_type

    if not dir_path.exists() or not dir_path.is_dir():
        raise HTTPException(status_code=404, detail="Image directory not found")

    files = sorted(p.name for p in dir_path.glob("*.png"))

    return files

@app.get("/tasks/{file_path:path}")
async def compressed_static(file_path: str):
    # 1. 拦截前端常见的 undefined 请求错误
    if "undefined" in file_path:
        raise HTTPException(status_code=404, detail="Invalid request: undefined path")

    # 构造完整路径
    original_path = TaskDirectory / file_path

    # 2. 严格检查文件是否存在
    if not original_path.exists() or not original_path.is_file():
        # 这里返回 404，防止 FileResponse 抛出 500 错误
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    # 3. 非 PNG 文件直接返回
    if original_path.suffix.lower() != ".png":
        return FileResponse(original_path)

    # 4. PNG 图片压缩逻辑
    try:
        # 建议：这里如果并发高，应该放入线程池，否则会阻塞
        with Image.open(original_path) as img:
            new_size = (img.width // 2, img.height // 2)
            resized_img = img.resize(new_size, Image.Resampling.LANCZOS)

            byte_io = BytesIO()
            resized_img.save(byte_io, "WEBP", quality=85)
            byte_io.seek(0)

        return StreamingResponse(
            content=byte_io,
            media_type="image/webp",
            headers={"Content-Length": str(byte_io.getbuffer().nbytes)}
        )
    except Exception as e:
        print(f"Error processing image {file_path}: {e}")
        # 如果压缩失败，降级返回原图
        return FileResponse(original_path)

# 挂载静态文件目录
# app.mount("/tasks", StaticFiles(directory=TaskDirectory), name="tasks")
app.mount('/', StaticFiles(directory='static'), name='static')

import logging 
logging.getLogger('uvicorn.access').addFilter(PngFilePathFilter())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=11453)