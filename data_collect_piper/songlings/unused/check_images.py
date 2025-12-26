import os
from pathlib import Path
from rich import print

image_dir = 'data/SimplePickUp/03-05@11:38:11/imgs'
image_dir = Path(image_dir)

i1c = os.listdir(image_dir / 'img_1_color')
i1d = os.listdir(image_dir / 'img_1_depth')
i2c = os.listdir(image_dir / 'img_2_color')
i2d = os.listdir(image_dir / 'img_2_depth')

get_time_stamp = lambda x: float(x[15:-5].replace('_', '.'))
to_time_stamp = lambda x: list(map(get_time_stamp, x))

i1c, i1d, i2c, i2d = list(map(to_time_stamp, [i1c, i1d, i2c, i2d]))
i1c.sort()
i2c.sort()
i1d.sort()
i2d.sort()


print(f'''
i1c: {len(i1c)}
i2c: {len(i2c)}
i1d: {len(i2d)}
i2d: {len(i2d)}
''')
print(f':')
for a, b, c, d in zip(i1c, i2c, i1d, i2d):
    print(f'i1c: {a:.6f}')
    print(f'i2c: {b:.6f}')
    print(f'i1d: {c:.6f}')
    print(f'i1d: {d:.6f}')
    input(":")