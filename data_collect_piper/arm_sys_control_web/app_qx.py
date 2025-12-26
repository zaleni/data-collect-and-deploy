from fastapi import FastAPI, Body 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from ros_backend import ROSBackend
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ros_backend = ROSBackend()

@app.get('/api/vla')
async def use_vla():
    ros_backend.use_vla()
    return {"message": "VLA activated"}

@app.get('/api/return_to_init_pos')
async def return_to_init_pos():
    ros_backend.return_to_init_pos()
    return {"message": "Returned to initial position"}



# @app.post('/api/obj')
# async def notify_franka_control():
#     ros_backend.notify_franka_control()
#     return {"message": "Notified franka control"}

@app.post('/api/obj')
async def notify_franka_control(post_string: str = Body(...)):
    # 处理接收到的字符串
    processed_string = post_string.lower()  # 示例处理：将字符串转换为大写
    print("post_string: ", post_string)
    ros_backend.notify_franka_control(processed_string)
    return {"message": "Notified franka control", "processed_string": processed_string}


    
    # curl -X POST "http://127.0.0.1:44931/api/obj" -H  "accept: application/json" -H  "Content-Type: application/json" -d '"water coffee water"'

@app.get('/api/sweep')
async def sweep():
    ros_backend.sweep()
    return {"message": "Sweeped"}


@app.get('/api/pick_up')
async def pick_up():
    ros_backend.pick_up()
    return {"message": "pick_uped"}


@app.get('/api/vllm')
async def vllm():
    ros_backend.vllm()
    return {"message": "vllm mode"}





@app.get('/api/put_bottle_on_table')
async def put_bottle_on_table():
    ros_backend.put_bottle_on_table()
    return {"message": "put_bottle_on_table"}


@app.get('/api/move_left')
async def move_left():
    ros_backend.move_left()
    return {"message": "move_left"}

# @app.get('/api/move_right')
# async def move_right():
#     ros_backend.move_right()
#     return {"message": "move_right"}






@app.get('/api/return_initial_position')
async def return_initial_position():
    ros_backend.return_initial_position()
    return {"message": "return_initial_position"}




@app.get("/")
async def index():
    return FileResponse("static/index.html")

import logging 

class APILogFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        
    def filter(self, record: logging.LogRecord) -> bool:
        if len(record.args) >= 3:
            path = record.args[2]
            if path.startswith('/api'):
                return False
        return True
    
# logging.getLogger('uvicorn.access').addFilter(APILogFilter())