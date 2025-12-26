from pathlib import Path
import json
from rich import print

base_dir = Path('data/ano')
for target in base_dir.iterdir():
    for espi in target.iterdir():
        anno = espi / 'ano.json'
        if anno.exists():
            print(anno)
            doc = json.load(open(anno))
            new_span = [item for item in doc['spans'] if item['annotation'] != 'push the plate closer to the customer']
            if len(new_span) != len(doc['spans']):
                doc['spans'] = new_span
                print(f'Update file {anno}')
                with open(anno, 'w') as f:
                    json.dump(doc, f)