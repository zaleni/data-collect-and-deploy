import os
from pathlib import Path
from typing import Final, List, Literal, Tuple, Dict, Union
from pydantic import BaseModel
import json
from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    EVENT_TYPE_MOVED,
    EVENT_TYPE_DELETED,
    EVENT_TYPE_CREATED,
    EVENT_TYPE_MODIFIED,
)
from converting_utils import sync_images


TaskDirectory: Final[Path] = Path("data/ano")
AnnotationFileName: Final[str] = "ano.json"


class TaskSpan(BaseModel):
    start_index: int
    end_index: int
    annotation: str
    used_for_vlm: bool


class Task(BaseModel):
    task_name: str
    annotator: str = ''
    # finished: bool
    status: Union[Literal['finished', 'unfinished', 'processing']] = 'unfinished'
    # 同步后的图像帧，每个元素为每步的front rgb, wrist rgb, front depth, wrist depth和平均时间戳
    frames: List[Tuple[str, str, str, str, float]]
    spans: List[TaskSpan] = []

class TaskEntryView(BaseModel):
    task_name: str
    # finished: bool
    status: Union[Literal['finished', 'unfinished', 'processing']]

class TaskManager:
    def __init__(self):
        self._task: Dict[str, Task] = {}
        self.reload()
        self.listener = None

    def reload(self):
        self._task = {}
        for save in TaskDirectory.glob("*"):
            for espi in save.glob("*"):
                anno_file = espi / AnnotationFileName
                if anno_file.exists():
                    # print(anno_file)
                    task = Task(**json.load(open(anno_file, 'r')))
                else:
                    images = sync_images(espi)
                    frames = [(i1, i2, d1, d2, sum(t) / 4.0) for t, (i1, i2, d1, d2) in images]
                    task = Task(
                        task_name=str(espi.relative_to(TaskDirectory)),
                        # finished=False,
                        status='unfinished',
                        frames=frames
                    )
                    with open(anno_file, 'w') as f:
                        f.write(task.model_dump_json(indent=2))
                self._task[task.task_name] = task

    def save_task(self, task: Task) -> Union[str, None]:
        original_task = self.Tasks[task.task_name]
        for f1, f2 in zip(original_task.frames, task.frames):
            if f1 != f2:
                return "frames are not the same"
        self.Tasks[task.task_name] = task
        with open(TaskDirectory / task.task_name / AnnotationFileName, 'w') as f:
            f.write(task.model_dump_json(indent=2))
        return None

    def listen_file_system(self):
        if self.listener is None:
            self.listener = TaskListenHandler(self)
            # 因为种种原因，这里对文件进行监听了，因为单独监听一层目录比较麻烦，所以就放着不懂了
            

    @property
    def TaskNames(self):
        return list(self._task.keys())

    @property
    def Tasks(self) -> Dict[str, Task]:
        return self._task
    
    

class TaskListenHandler(FileSystemEventHandler):
    def __init__(self, task_manager: TaskManager):
        super().__init__()
        self._task_manager = task_manager

    def on_any_event(self, event):
        if event.event_type in [
            EVENT_TYPE_MOVED,
            EVENT_TYPE_DELETED,
            EVENT_TYPE_CREATED,
            EVENT_TYPE_MODIFIED,
        ]:
            self._task_manager.reload()
