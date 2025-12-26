from pathlib import Path
import json
from rich import print

backups_dir = Path('backup')
backups = list(backups_dir.glob('*.json'))

base_dir = Path('data/ano')
for target in base_dir.iterdir():
    for espi in target.iterdir():
        anno = espi / 'ano.json'
        if anno.exists():
            find_name = f'{target.name}_{espi.name}'
            find_items = [item for item in backups if item.name.startswith(find_name)]
            find_items.sort(key=lambda x: int(str.ljust(x.name[len(find_name) + 1:-5], 18, '0')))
            back_up_file = find_items[-1]
            
            without_push = json.load(open(anno))
            with_push = json.load(open(back_up_file))
            
            if len(without_push['spans']) != len(with_push['spans']):
                # wops = [str(item) for item in without_push['spans']]
                # wps = [str(item) for item in with_push['spans']]
                
                # print(set(wps) - set(wops))
                without_push = with_push
                print(anno)
                with open(anno, 'w') as f:
                    json.dump(without_push, f)