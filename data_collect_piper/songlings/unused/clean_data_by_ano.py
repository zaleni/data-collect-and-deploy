import json
from pathlib import Path
from rich import print

base_dir = 'data/stage2'
base_dir = Path(base_dir)

for ds in base_dir.iterdir():
    for espi in ds.iterdir():
        anno_file = espi / 'ano.json'
        with open(anno_file) as f:
            anno = json.load(f)
        
        frames = anno['frames']
        front_color, wrist_color, front_depth, wrist_depth, _ = \
            zip(*frames)
            
        front_color = set(front_color)
        wrist_color = set(wrist_color)
        front_depth = set(front_depth)
        wrist_depth = set(wrist_depth)
        
        # real_front_color = [item. for item in (espi / 'img' / 'front_color').glob('*')]
        # check which files are not in the list
        real_front_color = [item for item in (espi / 'img' / 'front_color').glob('*') if item.name not in front_color]
        real_wrist_color = [item for item in (espi / 'img' / 'wrist_color').glob('*') if item.name not in wrist_color]
        real_front_depth = [item for item in (espi / 'img' / 'front_depth').glob('*') if item.name not in front_depth]
        real_wrist_depth = [item for item in (espi / 'img' / 'wrist_depth').glob('*') if item.name not in wrist_depth]
        
        print(f'Trying to delete {real_front_color}')
        print(f'Trying to delete {real_wrist_color}')
        print(f'Trying to delete {real_front_depth}')
        print(f'Trying to delete {real_wrist_depth}')
        print(espi)
        
        # remove files
        for item in real_front_color:
            item.unlink()
        for item in real_wrist_color:
            item.unlink()
        for item in real_front_depth:
            item.unlink()
        for item in real_wrist_depth:
            item.unlink()
        print(str(espi))
        print(f'delete {len(real_front_color) + len(real_wrist_color) + len(real_front_depth) + len(real_wrist_depth)} files')
        print('---')
        # exit(-1)