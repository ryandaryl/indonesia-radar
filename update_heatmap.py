from PIL import Image
import numpy as np
import requests
from io import BytesIO

colours = [
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
    (0, 0, 0),
    (0, 0, 0)
]

palette_image = Image.new('P', (16, 16))
palette_image.putpalette(sum([list(i) for i in colours], []))
background_array = np.array(Image.open('west_java.png').convert('RGB'))
image_url = 'https://dataweb.bmkg.go.id/MEWS/Radar/TANG_SingleLayerCRefQC.png'
image_array = np.array(Image.open(BytesIO(requests.get(image_url).content)).convert('RGB'))
# image_array = np.array(Image.open('TANG_SingleLayerCRefQC_1.png').convert('RGB'))
output_array = np.zeros(image_array.shape)
output_array[image_array != background_array] = image_array[image_array != background_array]
output_array[:50, ...] = 0
output_array = np.array(Image.fromarray(output_array.astype(np.uint8)).quantize(palette=palette_image).convert('RGB'))
for i, colour_tuple in enumerate(reversed(colours)):
    output_array[(output_array == colour_tuple).all(axis = -1)] = tuple([i*255/(len(colours)-1)]*3)
Image.fromarray((output_array).astype(np.uint8)).convert('RGB').save('output.png')