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


@app.get("/tasks/{file_path:path}")
async def compressed_static(file_path: str):
    original_path = f"{TaskDirectory}/{file_path}"
    
    # 仅处理 PNG 图片
    if not file_path.lower().endswith(".png"):
        return FileResponse(original_path)

    with Image.open(original_path) as img:
        # 尺寸压缩（长宽各减半）
        new_size = (img.width // 2, img.height // 2)
        resized_img = img.resize(new_size, Image.Resampling.LANCZOS)

        # 内存中直接处理
        byte_io = BytesIO()
        resized_img.save(byte_io, "WEBP", quality=85)
        byte_io.seek(0)  # 重置指针
            
    # 直接返回流式响应（无磁盘缓存）
    return StreamingResponse(
        content=byte_io,
        media_type="image/webp",
        headers={"Content-Length": str(byte_io.getbuffer().nbytes)}
    )

# 挂载静态文件目录
# app.mount("/tasks", StaticFiles(directory=TaskDirectory), name="tasks")
app.mount('/', StaticFiles(directory='static'), name='static')

import logging 
logging.getLogger('uvicorn.access').addFilter(PngFilePathFilter())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=11455)