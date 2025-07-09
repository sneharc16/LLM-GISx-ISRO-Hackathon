import numpy as np, rasterio
from scipy.stats import entropy, norm

def pixel_entropy(raster_path):
    with rasterio.open(raster_path) as src:
        arr = src.read(1).flatten()
    counts,_ = np.histogram(arr[arr>0], bins=256)
    return float(entropy(counts))

def region_probability(raster_path, threshold):
    with rasterio.open(raster_path) as src:
        arr = src.read(1).flatten()
    return float(np.mean(arr > threshold))

def gaussian_fit(samples):
    mu, std = norm.fit(np.array(samples))
    return {"mean":float(mu), "std":float(std)}
