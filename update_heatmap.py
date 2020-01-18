from PIL import Image
import numpy as np
import requests
from io import BytesIO
from hashlib import sha256
import datetime
import json
import os

colours = [
    (255, 255, 255),
    (255, 255, 255),
    (199, 0, 254),
    (206, 0, 133),
    (176, 0, 1),
    (224, 0, 2),
    (253, 58, 5),
    (255, 160, 4),
    (255, 226, 1),
    (129, 204, 1),
    (0, 177, 3),
    (1, 228, 3),
    (0, 128, 129),
    (0, 79, 255),
    (4, 206, 250),
    (0, 0, 0)
]

palette_image = Image.new('P', (16, 16))
palette_image.putpalette(sum([list(i) for i in colours], []))
background_array = np.array(Image.open('west_java.png').convert('RGB'))
image_url = 'https://dataweb.bmkg.go.id/MEWS/Radar/TANG_SingleLayerCRefQC.png'
image_array = np.array(Image.open(BytesIO(requests.get(image_url).content)).convert('RGB'))
# image_array = np.array(Image.open('TANG_SingleLayerCRefQC_1.png').convert('RGB'))
heatmap_array = np.zeros(image_array.shape)
output_array = np.zeros(image_array.shape[:2], dtype=np.uint8)
heatmap_array[image_array != background_array] = image_array[image_array != background_array]
timestamp_hash = sha256(image_array[:50, ...].tostring()).hexdigest()
print(timestamp_hash)
heatmap_array[:50, ...] = 0
heatmap_array = np.array(Image.fromarray(heatmap_array.astype(np.uint8)).quantize(palette=palette_image).convert('RGB'))
for i, colour_tuple in enumerate(reversed(colours)):
    output_array[(heatmap_array == colour_tuple).all(axis = -1)] = i*255/(len(colours)-1)
timestamp = datetime.datetime.now() - datetime.timedelta(minutes=15)
print(timestamp)

def add_heatmap(timestamp_hash, timestamp, heatmap_array):
    with open('radar_heatmap.json') as f:
        radar_heatmap_list = json.load(f)
    if any([timestamp_hash == heatmap_dict['timestamp_hash'] for heatmap_dict in radar_heatmap_list]):
        return False
    if len(radar_heatmap_list) == 5:
        os.remove(radar_heatmap_list[0]['filename'])
        radar_heatmap_list = radar_heatmap_list[1:]
    radar_heatmap_list = radar_heatmap_list + [{
        'timestamp_hash': timestamp_hash,
        'timestamp': timestamp,
        'filename': timestamp_hash + '.png'
    }]
    with open('radar_heatmap.json', 'w') as f:
        f.write(json.dumps(radar_heatmap_list, default=str))

add_heatmap(timestamp_hash, timestamp, output_array)
Image.fromarray((output_array).astype(np.uint8)).convert('RGB').save(timestamp_hash + '.png')