from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from ros_backend import ROSBackend
from pydantic import BaseModel

class switchState(BaseModel):
    switch_state: bool

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

backend = ROSBackend()

@app.get("/api/query_switch")
async def query_switch():
    return backend.query_switch_callback()

@app.post("/api/set_switch")
async def set_switch(switch_state: switchState):
    res =  backend.set_switch_callback(switch_state.switch_state)
    return res

@app.get("/api/query_status")
async def query_status():
    return backend.query_status_callback()

@app.get("/api/query_record_num")
async def query_record_num():
    return backend.query_record_num_callback()

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
    
logging.getLogger('uvicorn.access').addFilter(APILogFilter())