import rasterio
from windshelter import windshelter_window
# --- Working directory
wd = r'D:\tmp\windshelter'

# --- Input files - see folder example_data
dem = r'D:\GeirangerDTM\dtm10_clip.tif' # 792x800


with rasterio.open(dem) as src:
    array = src.read()
    array = array.astype('float')
    profile = src.profile
    cell_size = profile['transform'][0]

data = windshelter_window(array, profile, radius=8, prob=0.5, cell_size=10.0, wd=wd)

