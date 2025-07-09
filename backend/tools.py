# # tools.py

# import os
# import numpy as np
# import geopandas as gpd
# import rasterio
# from rasterio import mask as rio_mask
# from shapely.geometry import box
# from whitebox import WhiteboxTools
# from config import DATA_DIR

# def slope_analysis(out_dir: str,
#                    dem_path: str = None,
#                    bounding_box: list | None = None,
#                    out_slope: str = "slope.tif"):
#     """
#     Compute slope from a DEM. If bounding_box is provided, clip the global DEM mosaic
#     before computing slope.

#     Args:
#       out_dir: directory to save outputs
#       dem_path: path to DEM file (ignored if bounding_box is given)
#       bounding_box: [minx, miny, maxx, maxy] to clip global DEM
#       out_slope: filename for slope output
#     """
#     # Clip global DEM if requested
#     if bounding_box is not None:
#         global_dem = os.path.join(DATA_DIR, "input", "dem.tif")
#         with rasterio.open(global_dem) as src:
#             minx, miny, maxx, maxy = bounding_box
#             geom = box(minx, miny, maxx, maxy)
#             clipped, transform = rio_mask.mask(src, [geom], crop=True)
#             meta = src.meta.copy()
#             meta.update({
#                 "height": clipped.shape[1],
#                 "width": clipped.shape[2],
#                 "transform": transform
#             })
#         dem_in = os.path.join(out_dir, "clipped_dem.tif")
#         with rasterio.open(dem_in, "w", **meta) as dst:
#             dst.write(clipped)
#     else:
#         if dem_path is None:
#             raise ValueError("Either dem_path or bounding_box must be provided to slope_analysis")
#         dem_in = dem_path

#     out_path = os.path.join(out_dir, out_slope)
#     WhiteboxTools().slope(dem_in, out_path)


# def mask_forest(raster_path: str,
#                 forest_shp: str,
#                 out_dir: str,
#                 out_masked: str = "masked.tif"):
#     """
#     Mask out forested areas from a raster.

#     Args:
#       raster_path: path to input raster (e.g. DEM or slope)
#       forest_shp: path to forest polygons (shapefile or GeoJSON)
#       out_dir: directory to save outputs
#       out_masked: filename for masked output
#     """
#     with rasterio.open(raster_path) as src:
#         forests = gpd.read_file(forest_shp).to_crs(src.crs)
#         geoms = [feat.geometry for feat in forests.itertuples()]
#         masked, transform = rio_mask.mask(src, geoms, invert=True)
#         meta = src.meta.copy()
#         meta.update({
#             "height": masked.shape[1],
#             "width": masked.shape[2],
#             "transform": transform
#         })
#     out_path = os.path.join(out_dir, out_masked)
#     with rasterio.open(out_path, "w", **meta) as dst:
#         dst.write(masked)


# def buffer_features(shp_path: str,
#                     distance: float,
#                     out_dir: str,
#                     out_buffer: str = "buffer.shp"):
#     """
#     Create buffers around input features.

#     Args:
#       shp_path: path to input vector (shapefile or GeoJSON)
#       distance: buffer distance (same units as layer CRS)
#       out_dir: directory to save outputs
#       out_buffer: filename for buffered output shapefile
#     """
#     gdf = gpd.read_file(shp_path)
#     buf = gdf.geometry.buffer(distance)
#     out_gdf = gpd.GeoDataFrame(geometry=buf, crs=gdf.crs)
#     out_path = os.path.join(out_dir, out_buffer)
#     out_gdf.to_file(out_path)


# def score_sites(sites_shp: str,
#                 weights: dict,
#                 out_dir: str,
#                 out_scores: str = "scores.shp"):
#     """
#     Score point or polygon sites based on provided attribute weights.

#     Args:
#       sites_shp: path to input sites (shapefile or GeoJSON)
#       weights: dict mapping attribute names to weight (float)
#       out_dir: directory to save outputs
#       out_scores: filename for scored output shapefile
#     """
#     gdf = gpd.read_file(sites_shp)
#     scores = np.zeros(len(gdf), dtype=float)

#     for attr, w in weights.items():
#         if attr not in gdf.columns:
#             raise ValueError(f"Attribute '{attr}' not found in {sites_shp}")
#         vals = gdf[attr].astype(float).values
#         norm = (vals - vals.min()) / (vals.ptp() + 1e-6)
#         scores += w * norm

#     gdf["score"] = scores
#     out_path = os.path.join(out_dir, out_scores)
#     gdf.to_file(out_path)
#     return out_path


# def score_regions_by_energy(regions_shp: str,
#                             energy_type: str,
#                             criteria_weights: dict,
#                             out_dir: str,
#                             out_shp: str = "scored_regions.shp"):
#     """
#     Score polygon regions by suitability for a selected energy type.

#     Args:
#       regions_shp: path to input regions (shapefile or GeoJSON)
#       energy_type: 'solar' or 'wind'
#       criteria_weights: additional attribute weights (dict)
#       out_dir: directory to save outputs
#       out_shp: filename for scored regions shapefile
#     """
#     gdf = gpd.read_file(regions_shp)
#     # Base weight for energy-specific field
#     base_weights = {}
#     if energy_type.lower() == "solar":
#         base_weights["solar_potential"] = 1.0
#     elif energy_type.lower() == "wind":
#         base_weights["wind_potential"] = 1.0
#     else:
#         raise ValueError(f"Unsupported energy_type: {energy_type}")

#     # Merge with user-specified criteria weights
#     weights = {**base_weights, **(criteria_weights or {})}
#     scores = np.zeros(len(gdf), dtype=float)

#     for attr, w in weights.items():
#         if attr not in gdf.columns:
#             raise ValueError(f"Field '{attr}' not found in regions data")
#         vals = gdf[attr].astype(float).values
#         norm = (vals - vals.min()) / (vals.ptp() + 1e-6)
#         scores += w * norm

#     gdf["score"] = scores
#     out_path = os.path.join(out_dir, out_shp)
#     gdf.to_file(out_path)
#     return out_path


# def return_top_n_overlay(scored_shp: str,
#                          out_dir: str,
#                          top_n: int,
#                          out_shp: str | None = None,
#                          out_png: str | None = None):
#     """
#     Select the top N scored regions and generate an overlay map.

#     Args:
#       scored_shp: path to scored regions shapefile (must have 'score' column)
#       out_dir: directory to save outputs
#       top_n: number of top regions to select
#       out_shp: optional filename for top-N shapefile
#       out_png: optional filename for overlay PNG
#     """
#     gdf = gpd.read_file(scored_shp)
#     if "score" not in gdf.columns:
#         raise ValueError("Input shapefile missing 'score' column")

#     top = gdf.nlargest(top_n, "score")
#     shp_name = out_shp or f"top_{top_n}_sites.shp"
#     png_name = out_png or f"top_{top_n}_overlay.png"
#     shp_path = os.path.join(out_dir, shp_name)
#     top.to_file(shp_path)

#     # Create overlay map
#     import matplotlib.pyplot as plt
#     import contextily as cx

#     fig, ax = plt.subplots(figsize=(10, 10))
#     top.to_crs(epsg=3857).plot(ax=ax, column="score", legend=True)
#     cx.add_basemap(ax, source=cx.providers.Stamen.TerrainBackground)
#     ax.set_axis_off()

#     png_path = os.path.join(out_dir, png_name)
#     plt.savefig(png_path, bbox_inches="tight", dpi=150)
#     plt.close(fig)

#     return shp_path, png_path


# tools.py

import os
import numpy as np
import geopandas as gpd
import rasterio
from rasterio import mask as rio_mask
from shapely.geometry import box
from whitebox import WhiteboxTools
from config import DATA_DIR

def slope_analysis(out_dir: str,
                   dem_path: str = None,
                   bounding_box: list | None = None,
                   out_slope: str = "slope.tif"):
    """
    Compute slope from a DEM. Optionally clip by bounding_box.
    """
    # 1) Clip global DEM if requested
    if bounding_box is not None:
        global_dem = os.path.join(DATA_DIR, "input", "dem.tif")
        with rasterio.open(global_dem) as src:
            minx, miny, maxx, maxy = bounding_box
            geom = box(minx, miny, maxx, maxy)
            clipped, transform = rio_mask.mask(src, [geom], crop=True)
            meta = src.meta.copy()
            meta.update({
                "height": clipped.shape[1],
                "width": clipped.shape[2],
                "transform": transform
            })
        dem_in = os.path.join(out_dir, "clipped_dem.tif")
        with rasterio.open(dem_in, "w", **meta) as dst:
            dst.write(clipped)
    else:
        if dem_path is None:
            raise ValueError("Either dem_path or bounding_box must be provided")
        dem_in = dem_path

    # 2) Run WhiteboxTools slope
    out_path = os.path.join(out_dir, out_slope)
    WhiteboxTools().slope(dem_in, out_path)


def mask_forest(raster_path: str,
                forest_shp: str,
                out_dir: str,
                out_masked: str = "masked.tif"):
    """
    Mask out forested areas from a raster.
    """
    with rasterio.open(raster_path) as src:
        forests = gpd.read_file(forest_shp).to_crs(src.crs)
        geoms = [feat.geometry for feat in forests.itertuples()]
        masked, transform = rio_mask.mask(src, geoms, invert=True)
        meta = src.meta.copy()
        meta.update({
            "height": masked.shape[1],
            "width": masked.shape[2],
            "transform": transform
        })
    out_path = os.path.join(out_dir, out_masked)
    with rasterio.open(out_path, "w", **meta) as dst:
        dst.write(masked)


def buffer_features(shp_path: str,
                    distance: float,
                    out_dir: str,
                    out_buffer: str = "buffer.shp"):
    """
    Create buffers around input features.
    """
    gdf = gpd.read_file(shp_path)
    buf = gdf.geometry.buffer(distance)
    gpd.GeoDataFrame(geometry=buf, crs=gdf.crs)\
       .to_file(os.path.join(out_dir, out_buffer))


def score_sites(sites_shp: str,
                weights: dict,
                out_dir: str,
                out_scores: str = "scores.shp") -> str:
    """
    Score sites by weighted, normalized attributes.
    """
    gdf = gpd.read_file(sites_shp)
    scores = np.zeros(len(gdf), dtype=float)

    for attr, w in weights.items():
        if attr not in gdf.columns:
            raise ValueError(f"Attribute '{attr}' not found in {sites_shp}")
        vals = gdf[attr].astype(float).values
        norm = (vals - vals.min()) / (vals.ptp() + 1e-6)
        scores += w * norm

    gdf["score"] = scores
    out_path = os.path.join(out_dir, out_scores)
    gdf.to_file(out_path)
    return out_path


def score_regions_by_energy(regions_shp: str,
                            energy_type: str,
                            criteria_weights: dict,
                            out_dir: str,
                            out_shp: str = "scored_regions.shp") -> str:
    """
    Score polygon regions by solar or wind suitability.
    """
    gdf = gpd.read_file(regions_shp)
    base_weights = {}
    et = energy_type.lower()
    if et == "solar":
        base_weights["solar_potential"] = 1.0
    elif et == "wind":
        base_weights["wind_potential"] = 1.0
    else:
        raise ValueError(f"Unsupported energy_type: {energy_type}")

    weights = {**base_weights, **(criteria_weights or {})}
    scores = np.zeros(len(gdf), dtype=float)

    for attr, w in weights.items():
        if attr not in gdf.columns:
            raise ValueError(f"Field '{attr}' not found in {regions_shp}")
        vals = gdf[attr].astype(float).values
        norm = (vals - vals.min()) / (vals.ptp() + 1e-6)
        scores += w * norm

    gdf["score"] = scores
    out_path = os.path.join(out_dir, out_shp)
    gdf.to_file(out_path)
    return out_path


def return_top_n_overlay(scored_shp: str,
                         out_dir: str,
                         top_n: int,
                         out_shp: str | None = None,
                         out_png: str | None = None) -> tuple[str, str]:
    """
    Select top-N regions and generate a PNG overlay.
    """
    gdf = gpd.read_file(scored_shp)
    if "score" not in gdf.columns:
        raise ValueError("Missing 'score' column")

    top = gdf.nlargest(top_n, "score")
    shp_name = out_shp or f"top_{top_n}_sites.shp"
    png_name = out_png or f"top_{top_n}_overlay.png"

    shp_path = os.path.join(out_dir, shp_name)
    top.to_file(shp_path)

    # Build overlay
    import matplotlib.pyplot as plt
    import contextily as cx

    fig, ax = plt.subplots(figsize=(10, 10))
    top.to_crs(epsg=3857).plot(ax=ax, column="score", legend=True)
    cx.add_basemap(ax, source=cx.providers.Stamen.TerrainBackground)
    ax.set_axis_off()

    png_path = os.path.join(out_dir, png_name)
    plt.savefig(png_path, bbox_inches="tight", dpi=150)
    plt.close(fig)

    return shp_path, png_path
