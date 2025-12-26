from pathlib import Path
from shutil import copyfile
import time

base_dir = Path('data/stage2')
back_dir = Path('backup')

for ds in base_dir.iterdir():
    for espi in ds.iterdir():
        anno_file = espi / 'ano.json'
        if anno_file.exists():
            copyfile(anno_file, back_dir / f'{ds.name}_{espi.name}@{str(time.time()).replace(".", "")}.json')
            print(f'backed up {ds.name}_{espi.name}.json')