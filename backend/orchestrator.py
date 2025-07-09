# # orchestrator.py

# import re
# import json
# import uuid
# import os
# import logging
# import tempfile
# import requests

# import numpy as np
# import geopandas as gpd
# import rasterio
# from rasterio.transform import from_bounds
# from shapely.geometry import box as shapely_box, Point

# from groq import Groq
# from config import GROQ_API_KEY, DATA_DIR
# from tools import (
#     slope_analysis,
#     mask_forest,
#     buffer_features,
#     score_sites,
#     score_regions_by_energy,
#     return_top_n_overlay,
# )
# import stats_tools

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# client = Groq(api_key=GROQ_API_KEY)

# # persists the user's BBOX so we can generate points later
# CURRENT_BBOX = None


# class OrchestratorError(Exception):
#     """Raised when something goes wrong in the orchestration pipeline."""


# def sanitize_raw_json(raw: str) -> str:
#     """Strip code fences, comments, trailing commas → valid JSON."""
#     m = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
#     if m:
#         raw = m.group(1)
#     raw = re.sub(r"//.*", "", raw)
#     raw = re.sub(r"/\*[\s\S]*?\*/", "", raw)
#     raw = re.sub(r",\s*(?=[}\]])", "", raw)
#     return raw.strip()


# def fetch_raster_via_wcs(layer: str, bbox=None, crs="EPSG:4326") -> str:
#     """Attempt a WCS GetCoverage; write to temp GeoTIFF."""
#     url = "http://localhost:8080/geoserver/wcs"
#     params = {
#         "service": "WCS", "version": "1.0.0", "request": "GetCoverage",
#         "coverage": layer, "crs": crs, "format": "GeoTIFF",
#         "width": 512, "height": 512
#     }
#     if bbox:
#         params["bbox"] = ",".join(map(str, bbox))
#     resp = requests.get(url, params=params, timeout=30)
#     resp.raise_for_status()
#     tmp = tempfile.NamedTemporaryFile(suffix=".tif", delete=False)
#     tmp.write(resp.content)
#     tmp.flush()
#     return tmp.name


# def create_dummy_raster(bbox=None, width=256, height=256) -> str:
#     """Make a constant (1) raster over bbox (or world)."""
#     if bbox:
#         minx, miny, maxx, maxy = bbox
#     else:
#         minx, miny, maxx, maxy = -180, -90, 180, 90

#     data = np.ones((height, width), dtype=np.float32)
#     transform = from_bounds(minx, miny, maxx, maxy, width, height)
#     meta = {
#         "driver": "GTiff", "dtype": "float32", "count": 1,
#         "crs": "EPSG:4326", "transform": transform,
#         "width": width, "height": height
#     }
#     tmp = tempfile.NamedTemporaryFile(suffix=".tif", delete=False)
#     with rasterio.open(tmp.name, "w", **meta) as dst:
#         dst.write(data, 1)
#     logger.info(f"Dummy raster → {tmp.name}")
#     return tmp.name


# def get_raster(layer: str, bbox=None) -> str:
#     """
#     Try WCS → local DATA_DIR/input/{layer}.tif → dummy raster.
#     """
#     # 1) WCS
#     try:
#         path = fetch_raster_via_wcs(layer, bbox)
#         with rasterio.open(path):
#             pass
#         return path
#     except Exception as e:
#         logger.warning(f"WCS fetch failed for '{layer}': {e}")

#     # 2) local
#     local = os.path.join(DATA_DIR, "input", f"{layer}.tif")
#     if os.path.isfile(local):
#         logger.info(f"Using local raster {local}")
#         return local

#     # 3) dummy
#     logger.info(f"No raster '{layer}', generating dummy")
#     return create_dummy_raster(bbox)


# def fetch_vector_via_wfs(layer: str) -> str:
#     """Attempt a WFS GetFeature; write to temp GeoJSON."""
#     url = "http://localhost:8080/geoserver/wfs"
#     params = {
#         "service": "WFS", "version": "1.0.0", "request": "GetFeature",
#         "typeName": layer, "outputFormat": "application/json"
#     }
#     resp = requests.get(url, params=params, timeout=30)
#     resp.raise_for_status()
#     tmp = tempfile.NamedTemporaryFile(suffix=".geojson", delete=False)
#     tmp.write(resp.content)
#     tmp.flush()
#     return tmp.name


# def create_dummy_vector(bbox=None) -> str:
#     """Make one polygon = bbox (or world) as GeoJSON."""
#     geom = shapely_box(*bbox) if bbox else shapely_box(-180, -90, 180, 90)
#     gdf = gpd.GeoDataFrame({"geometry": [geom]}, crs="EPSG:4326")
#     tmp = tempfile.NamedTemporaryFile(suffix=".geojson", delete=False)
#     gdf.to_file(tmp.name, driver="GeoJSON")
#     logger.info(f"Dummy vector → {tmp.name}")
#     return tmp.name


# def get_vector(layer: str, bbox=None) -> str:
#     """
#     Try WFS → local input/{layer}.shp/.geojson → dummy GeoJSON.
#     """
#     try:
#         path = fetch_vector_via_wfs(layer)
#         _ = gpd.read_file(path)
#         return path
#     except Exception as e:
#         logger.warning(f"WFS fetch failed for '{layer}': {e}")

#     for ext in (".shp", ".geojson"):
#         local = os.path.join(DATA_DIR, "input", f"{layer}{ext}")
#         if os.path.isfile(local):
#             logger.info(f"Using local vector {local}")
#             return local

#     logger.info(f"No vector '{layer}', generating dummy")
#     return create_dummy_vector(bbox)


# def generate_candidate_sites(bbox: list, out_dir: str, spacing=0.01) -> str:
#     """Fishnet of points across bbox, saved as GeoJSON."""
#     minx, miny, maxx, maxy = bbox
#     xs = np.arange(minx, maxx, spacing)
#     ys = np.arange(miny, maxy, spacing)
#     pts = [Point(x, y) for x in xs for y in ys]
#     gdf = gpd.GeoDataFrame(geometry=pts, crs="EPSG:4326")
#     path = os.path.join(out_dir, "candidate_sites.geojson")
#     gdf.to_file(path, driver="GeoJSON")
#     logger.info(f"Generated {len(pts)} candidates → {path}")
#     return path


# # ─── Wrappers ────────────────────────────────────────────────────────────────

# def wrapper_slope(params, out_dir):
#     layer = params.get("dem_data") or params.get("dem_source") or "dem"
#     bbox = params.get("bounding_box") or params.get("bbox")
#     dem = get_raster(layer, bbox)
#     slope_analysis(out_dir=out_dir, dem_path=dem, bounding_box=None)


# def wrapper_mask(params, out_dir):
#     layer = params.get("forest_data") or params.get("forest_data_source")
#     if not layer:
#         logger.info("No 'forest_data' → skipping mask_forest")
#         return
#     bbox = params.get("bounding_box") or params.get("bbox")
#     shp = get_vector(layer, bbox)
#     slope_fp = os.path.join(out_dir, "slope.tif")
#     raster_to_mask = slope_fp if os.path.isfile(slope_fp) else get_raster(params.get("dem_data", "dem"), bbox)
#     mask_forest(raster_path=raster_to_mask, forest_shp=shp, out_dir=out_dir)


# def wrapper_buffer(params, out_dir):
#     layer = params.get("features")
#     dist = params.get("buffer_distance") or params.get("distance")
#     if not layer or dist is None:
#         logger.info("Incomplete 'buffer_features' params → skipping")
#         return
#     shp = get_vector(layer, CURRENT_BBOX)
#     buffer_features(shp_path=shp, distance=dist, out_dir=out_dir)


# def wrapper_score(params, out_dir):
#     # 1) find or generate candidate sites GeoJSON
#     files = os.listdir(out_dir)
#     geo = next((f for f in files if f.endswith(".geojson")), None)
#     if geo:
#         sites_fp = os.path.join(out_dir, geo)
#     else:
#         if not CURRENT_BBOX:
#             raise OrchestratorError("No BBOX to generate candidate sites")
#         sites_fp = generate_candidate_sites(CURRENT_BBOX, out_dir)

#     gdf = gpd.read_file(sites_fp)

#     # 2) sample solar potential
#     if "solar_potential_data" in params:
#         rast = get_raster(params["solar_potential_data"], CURRENT_BBOX)
#         with rasterio.open(rast) as src:
#             vals = [list(src.sample([(pt.x, pt.y)]))[0][0] or 0 for pt in gdf.geometry]
#         gdf["solar_potential"] = vals

#     # 3) forest damage flag
#     mask_fp = os.path.join(out_dir, "masked.tif")
#     if os.path.isfile(mask_fp):
#         with rasterio.open(mask_fp) as src:
#             dmg = []
#             for pt in gdf.geometry:
#                 v = list(src.sample([(pt.x, pt.y)]))[0][0]
#                 dmg.append(1 if v is None or np.isnan(v) else 0)
#         gdf["forest_damage"] = dmg
#     else:
#         gdf["forest_damage"] = 0

#     # 4) save back to GeoJSON (retain full names!)
#     gdf.to_file(sites_fp, driver="GeoJSON")

#     # 5) weights & score
#     weights = {}
#     if "solar_potential_data" in params:
#         weights["solar_potential"] = 1.0
#     if "max_forest_damage" in params:
#         weights["forest_damage"] = -float(params["max_forest_damage"])
#     score_sites(sites_shp=sites_fp, weights=weights, out_dir=out_dir)


# def wrapper_pixel_entropy(params, out_dir):
#     layer = params.get("raster_data") or params.get("raster_source")
#     if not layer:
#         logger.info("No 'raster_data' → skipping pixel_entropy")
#         return
#     tif = get_raster(layer)
#     ent = stats_tools.pixel_entropy(tif)
#     with open(os.path.join(out_dir, "pixel_entropy.json"), "w") as f:
#         json.dump({"pixel_entropy": ent}, f)


# def wrapper_region_probability(params, out_dir):
#     layer = params.get("raster_data") or params.get("raster_source")
#     thresh = params.get("threshold")
#     if not layer or thresh is None:
#         logger.info("Incomplete 'region_probability' params → skipping")
#         return
#     tif = get_raster(layer)
#     prob = stats_tools.region_probability(tif, float(thresh))
#     with open(os.path.join(out_dir, "region_probability.json"), "w") as f:
#         json.dump({"region_probability": prob}, f)


# def wrapper_gaussian_fit(params, out_dir):
#     samples = params.get("samples")
#     if not isinstance(samples, list):
#         logger.info("No valid 'samples' → skipping gaussian_fit")
#         return
#     fit = stats_tools.gaussian_fit(samples)
#     with open(os.path.join(out_dir, "gaussian_fit.json"), "w") as f:
#         json.dump(fit, f)


# def wrapper_score_regions(params, out_dir):
#     layer = params.get("regions")
#     energy = params.get("energy_type")
#     wts = params.get("criteria_weights", {})
#     if not layer or not energy:
#         logger.info("Incomplete 'score_regions' params → skipping")
#         return
#     shp = get_vector(layer, CURRENT_BBOX)
#     score_regions_by_energy(regions_shp=shp,
#                             energy_type=energy,
#                             criteria_weights=wts,
#                             out_dir=out_dir)


# def wrapper_return_top_n(params, out_dir):
#     top_n = params.get("top_n")
#     if top_n is None:
#         logger.info("No 'top_n' → skipping return_top_n_overlay")
#         return
#     shp = os.path.join(out_dir, "scored_regions.shp")
#     if not os.path.isfile(shp):
#         logger.info("No scored_regions.shp → skipping overlay")
#         return
#     return_top_n_overlay(scored_shp=shp, out_dir=out_dir, top_n=int(top_n))


# TOOL_WRAPPERS = {
#     "slope_analysis":       wrapper_slope,
#     "mask_forest":          wrapper_mask,
#     "buffer_features":      wrapper_buffer,
#     "score_sites":          wrapper_score,
#     "pixel_entropy":        wrapper_pixel_entropy,
#     "region_probability":   wrapper_region_probability,
#     "gaussian_fit":         wrapper_gaussian_fit,
#     "score_regions":        wrapper_score_regions,
#     "return_top_n_overlay": wrapper_return_top_n,
# }


# def run_task(query: str, bbox: list) -> str:
#     global CURRENT_BBOX
#     if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
#         raise ValueError("bbox must be [minx, miny, maxx, maxy]")
#     CURRENT_BBOX = bbox

#     task_id = uuid.uuid4().hex
#     task_dir = os.path.join(DATA_DIR, "output", task_id)
#     os.makedirs(task_dir, exist_ok=True)

#     prompt = (
#         "You are GeoSolarX. Tools:\n"
#         "• slope_analysis(dem_data, optional bounding_box)\n"
#         "• mask_forest(forest_data, optional bounding_box)\n"
#         "• buffer_features(features, buffer_distance)\n"
#         "• score_sites(solar_potential_data, max_forest_damage, top_n_sites)\n"
#         "• pixel_entropy(raster_data)\n"
#         "• region_probability(raster_data, threshold)\n"
#         "• gaussian_fit(samples)\n"
#         "• score_regions(regions, energy_type, optional criteria_weights)\n"
#         "• return_top_n_overlay(top_n)\n\n"
#         f"Chain-of-Thought:\nQuery: {query}\nBBOX: {bbox}\n"
#         "Return JSON array of steps."
#     )
#     resp = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[{"role":"user","content":prompt}]
#     )
#     raw = resp.choices[0].message.content or ""
#     clean = sanitize_raw_json(raw)
#     try:
#         steps = json.loads(clean)
#     except Exception as e:
#         logger.error("Bad CoT JSON: %s\n%s", e, clean)
#         raise OrchestratorError(f"Bad CoT JSON: {e}")

#     with open(os.path.join(task_dir, "cot.json"), "w") as f:
#         json.dump(steps, f, indent=2)

#     for i, step in enumerate(steps, start=1):
#         tool = step.get("tool")
#         params = step.get("params", {}) or {}
#         wrapper = TOOL_WRAPPERS.get(tool)
#         if not wrapper:
#             logger.warning(f"Unknown tool '{tool}' (step {i}) → skipping")
#             continue
#         try:
#             wrapper(params, task_dir)
#         except Exception as e:
#             logger.error(f"Tool '{tool}' failed at step {i}: {e}")
#             raise OrchestratorError(f"{tool} failed at step {i}: {e}")

#     return task_id


# def extract_properties(task_dir: str) -> list[dict]:
#     results = []
#     for fn in os.listdir(task_dir):
#         if fn.lower().endswith((".shp", ".geojson")):
#             path = os.path.join(task_dir, fn)
#             gdf = gpd.read_file(path)
#             geo = gdf.to_crs(epsg=4326)
#             metr = gdf.to_crs(epsg=3857)
#             for pt, poly in zip(geo.geometry.centroid, metr.geometry):
#                 results.append({
#                     "lat": float(pt.y),
#                     "lon": float(pt.x),
#                     "area_m2": float(poly.area)
#                 })
#     return results


# def summarize_task(task_id: str) -> dict:
#     task_dir = os.path.join(DATA_DIR, "output", task_id)
#     cot_file = os.path.join(task_dir, "cot.json")
#     if not os.path.isfile(cot_file):
#         raise OrchestratorError(f"No CoT for task {task_id}")

#     steps = json.load(open(cot_file))
#     results = extract_properties(task_dir)

#     stats_out = {}
#     for fn in ("pixel_entropy.json", "region_probability.json", "gaussian_fit.json"):
#         p = os.path.join(task_dir, fn)
#         if os.path.isfile(p):
#             stats_out.update(json.load(open(p)))

#     overlays = [f for f in os.listdir(task_dir) if f.endswith("_overlay.png")]
#     overlay = overlays[0] if overlays else None

#     summary_prompt = (
#         "You are GeoSolarX Assistant.\n\n"
#         "Chain-of-Thought:\n" f"{json.dumps(steps,indent=2)}\n\n"
#         "Site properties:\n" f"{json.dumps(results,indent=2)}\n\n"
#         "Statistics:\n" f"{json.dumps(stats_out,indent=2)}\n\n"
#         f"Overlay map: {overlay}\n\n"
#         "Provide a concise summary."
#     )
#     resp = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[{"role":"user","content":summary_prompt}]
#     )
#     summary = resp.choices[0].message.content.strip()
#     with open(os.path.join(task_dir,"summary.txt"),"w") as f:
#         f.write(summary)

#     return {"summary": summary, "results": results, "overlay_map": overlay}


# orchestrator.py

# orchestrator.py

# orchestrator.py



# import re
# import json
# import uuid
# import os
# import math
# import logging
# import tempfile
# import requests

# import numpy as np
# import geopandas as gpd
# import rasterio
# from rasterio.transform import from_bounds
# from shapely.geometry import box as shapely_box, Point

# from groq import Groq
# from config import GROQ_API_KEY, DATA_DIR
# from tools import (
#     slope_analysis,
#     mask_forest,
#     buffer_features,
#     score_sites,
#     score_regions_by_energy,
#     return_top_n_overlay,
# )
# import stats_tools

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# client = Groq(api_key=GROQ_API_KEY)

# # Persist the user's BBOX for downstream steps
# CURRENT_BBOX = None

# class OrchestratorError(Exception):
#     pass


# # ── JSON Sanitation & LLM call ─────────────────────────────────────────────

# def sanitize_raw_json(raw: str) -> str:
#     m = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
#     if m:
#         raw = m.group(1)
#     raw = re.sub(r"//.*", "", raw)
#     raw = re.sub(r"/\*[\s\S]*?\*/", "", raw)
#     raw = re.sub(r",\s*(?=[}\]])", "", raw)
#     return raw.strip()


# def prepare_task(query: str, bbox: list) -> str:
#     """
#     1) Validate bbox
#     2) Create task folder
#     3) Prompt LLM for CoT (including new policy & cost tools)
#     4) Sanitize & parse JSON
#     5) Write cot.json
#     """
#     global CURRENT_BBOX
#     if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
#         raise ValueError("bbox must be [minx, miny, maxx, maxy]")
#     CURRENT_BBOX = bbox

#     task_id = uuid.uuid4().hex
#     task_dir = os.path.join(DATA_DIR, "output", task_id)
#     os.makedirs(task_dir, exist_ok=True)

#     prompt = (
#         "You are GeoSolarX. Tools available:\n"
#         " - slope_analysis(dem_data, bounding_box)\n"
#         " - mask_forest(forest_data, bounding_box)\n"
#         " - buffer_features(features, buffer_distance)\n"
#         " - score_sites(solar_potential_data, max_forest_damage, top_n_sites)\n"
#         " - pixel_entropy(raster_data)\n"
#         " - region_probability(raster_data, threshold)\n"
#         " - gaussian_fit(samples)\n"
#         " - score_regions(regions, energy_type, criteria_weights)\n"
#         " - return_top_n_overlay(top_n)\n"
#         " - score_by_policy(state_policy_layer, preferred_states, state_policy_weight)\n"
#         " - score_by_cost(cost_raster, max_cost_threshold, cost_weight)\n\n"
#         f"Chain-of-Thought for:\n  Query: {query}\n  BBOX: {bbox}\n"
#         "Return a JSON array of steps: [{\"tool\":...,\"params\":{...}}, ...]."
#     )
#     resp = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[{"role":"user","content":prompt}]
#     )
#     raw = resp.choices[0].message.content or ""
#     clean = sanitize_raw_json(raw)
#     try:
#         steps = json.loads(clean)
#     except Exception as e:
#         logger.error("CoT JSON parse error: %s\n%s", e, clean)
#         raise OrchestratorError(f"Bad CoT JSON: {e}")

#     # Write cot.json immediately so status endpoints can read it
#     with open(os.path.join(task_dir, "cot.json"), "w") as f:
#         json.dump(steps, f, indent=2)

#     return task_id


# def get_cot(task_id: str) -> list:
#     """Return the parsed cot.json for status checks."""
#     path = os.path.join(DATA_DIR, "output", task_id, "cot.json")
#     if not os.path.isfile(path):
#         raise FileNotFoundError
#     return json.load(open(path))


# # ── WCS/WFS + Dummy fallbacks ──────────────────────────────────────────────

# def fetch_raster_via_wcs(layer: str, bbox=None, crs="EPSG:4326") -> str:
#     url = "http://localhost:8080/geoserver/wcs"
#     params = {
#         "service": "WCS", "version": "1.0.0", "request": "GetCoverage",
#         "coverage": layer, "crs": crs, "format": "GeoTIFF",
#         "width": 512, "height": 512
#     }
#     if bbox:
#         params["bbox"] = ",".join(map(str, bbox))
#     resp = requests.get(url, params=params, timeout=30)
#     resp.raise_for_status()
#     tmp = tempfile.NamedTemporaryFile(suffix=".tif", delete=False)
#     tmp.write(resp.content); tmp.flush()
#     return tmp.name

# def create_dummy_raster(bbox=None, width=256, height=256) -> str:
#     if bbox:
#         minx, miny, maxx, maxy = bbox
#     else:
#         minx, miny, maxx, maxy = -180, -90, 180, 90

#     data = np.ones((height, width), dtype=np.float32)
#     transform = from_bounds(minx, miny, maxx, maxy, width, height)
#     meta = {
#         "driver": "GTiff", "dtype": "float32", "count": 1,
#         "crs": "EPSG:4326", "transform": transform,
#         "width": width, "height": height
#     }
#     tmp = tempfile.NamedTemporaryFile(suffix=".tif", delete=False)
#     with rasterio.open(tmp.name, "w", **meta) as dst:
#         dst.write(data, 1)
#     logger.info(f"Dummy raster → {tmp.name}")
#     return tmp.name

# def get_raster(layer: str, bbox=None) -> str:
#     try:
#         path = fetch_raster_via_wcs(layer, bbox)
#         with rasterio.open(path): pass
#         return path
#     except Exception as e:
#         logger.warning(f"WCS fetch failed for '{layer}': {e}")
#     local = os.path.join(DATA_DIR, "input", f"{layer}.tif")
#     if os.path.isfile(local):
#         return local
#     return create_dummy_raster(bbox)

# def fetch_vector_via_wfs(layer: str) -> str:
#     url = "http://localhost:8080/geoserver/wfs"
#     params = {
#         "service": "WFS", "version": "1.0.0", "request": "GetFeature",
#         "typeName": layer, "outputFormat": "application/json"
#     }
#     resp = requests.get(url, params=params, timeout=30)
#     resp.raise_for_status()
#     tmp = tempfile.NamedTemporaryFile(suffix=".geojson", delete=False)
#     tmp.write(resp.content); tmp.flush()
#     return tmp.name

# def create_dummy_vector(bbox=None) -> str:
#     geom = shapely_box(*bbox) if bbox else shapely_box(-180, -90, 180, 90)
#     gdf = gpd.GeoDataFrame({"geometry": [geom]}, crs="EPSG:4326")
#     tmp = tempfile.NamedTemporaryFile(suffix=".geojson", delete=False)
#     gdf.to_file(tmp.name, driver="GeoJSON")
#     return tmp.name

# def get_vector(layer: str, bbox=None) -> str:
#     try:
#         path = fetch_vector_via_wfs(layer)
#         _ = gpd.read_file(path)
#         return path
#     except Exception:
#         pass
#     for ext in (".shp", ".geojson"):
#         local = os.path.join(DATA_DIR, "input", f"{layer}{ext}")
#         if os.path.isfile(local):
#             return local
#     return create_dummy_vector(bbox)

# def generate_candidate_sites(bbox: list, out_dir: str, spacing=0.01) -> str:
#     minx, miny, maxx, maxy = bbox
#     xs = np.arange(minx, maxx, spacing)
#     ys = np.arange(miny, maxy, spacing)
#     pts = [Point(x, y) for x in xs for y in ys]
#     gdf = gpd.GeoDataFrame(geometry=pts, crs="EPSG:4326")
#     path = os.path.join(out_dir, "candidate_sites.geojson")
#     gdf.to_file(path, driver="GeoJSON")
#     return path


# # ── Wrapper dispatch ───────────────────────────────────────────────────────

# def wrapper_slope(params, out_dir):
#     layer = params.get("dem_data") or params.get("dem_source") or "dem"
#     dem = get_raster(layer, CURRENT_BBOX)
#     slope_analysis(out_dir=out_dir, dem_path=dem, bounding_box=None)

# def wrapper_mask(params, out_dir):
#     layer = params.get("forest_data") or params.get("forest_data_source")
#     if not layer:
#         return
#     shp = get_vector(layer, CURRENT_BBOX)
#     slope_fp = os.path.join(out_dir, "slope.tif")
#     raster_to_mask = slope_fp if os.path.isfile(slope_fp) else get_raster("dem", CURRENT_BBOX)
#     mask_forest(raster_path=raster_to_mask, forest_shp=shp, out_dir=out_dir)

# def wrapper_buffer(params, out_dir):
#     layer = params.get("features")
#     dist  = params.get("buffer_distance") or params.get("distance")
#     if not layer or dist is None:
#         return
#     shp = get_vector(layer, CURRENT_BBOX)
#     buffer_features(shp_path=shp, distance=dist, out_dir=out_dir)

# def wrapper_score(params, out_dir):
#     geo = next((f for f in os.listdir(out_dir) if f.endswith(".geojson")), None)
#     sites_fp = os.path.join(out_dir, geo) if geo else generate_candidate_sites(CURRENT_BBOX, out_dir)
#     gdf = gpd.read_file(sites_fp)

#     if "solar_potential_data" in params:
#         rast = get_raster(params["solar_potential_data"], CURRENT_BBOX)
#         with rasterio.open(rast) as src:
#             gdf["solar_potential"] = [
#                 list(src.sample([(pt.x, pt.y)]))[0][0] or 0
#                 for pt in gdf.geometry
#             ]

#     mask_fp = os.path.join(out_dir, "masked.tif")
#     if os.path.isfile(mask_fp):
#         with rasterio.open(mask_fp) as src:
#             gdf["forest_damage"] = [
#                 1 if (list(src.sample([(pt.x, pt.y)]))[0][0] is None) else 0
#                 for pt in gdf.geometry
#             ]
#     else:
#         gdf["forest_damage"] = 0

#     gdf.to_file(sites_fp, driver="GeoJSON")

#     weights = {}
#     if "solar_potential_data" in params:
#         weights["solar_potential"] = 1.0
#     if "max_forest_damage" in params:
#         weights["forest_damage"] = -float(params["max_forest_damage"])
#     score_sites(sites_shp=sites_fp, weights=weights, out_dir=out_dir)

# def wrapper_pixel_entropy(params, out_dir):
#     layer = params.get("raster_data") or params.get("raster_source")
#     if not layer:
#         return
#     ent = stats_tools.pixel_entropy(get_raster(layer))
#     with open(os.path.join(out_dir, "pixel_entropy.json"), "w") as f:
#         json.dump({"pixel_entropy": ent}, f)

# def wrapper_region_probability(params, out_dir):
#     layer = params.get("raster_data") or params.get("raster_source")
#     thr   = params.get("threshold")
#     if not layer or thr is None:
#         return
#     prob = stats_tools.region_probability(get_raster(layer), float(thr))
#     with open(os.path.join(out_dir, "region_probability.json"), "w") as f:
#         json.dump({"region_probability": prob}, f)

# def wrapper_gaussian_fit(params, out_dir):
#     samples = params.get("samples")
#     if not isinstance(samples, list):
#         return
#     fit = stats_tools.gaussian_fit(samples)
#     with open(os.path.join(out_dir, "gaussian_fit.json"), "w") as f:
#         json.dump(fit, f)

# def wrapper_score_regions(params, out_dir):
#     layer = params.get("regions")
#     energy= params.get("energy_type")
#     wts   = params.get("criteria_weights", {})
#     if not layer or not energy:
#         return
#     shp = get_vector(layer, CURRENT_BBOX)
#     score_regions_by_energy(
#         regions_shp=shp,
#         energy_type=energy,
#         criteria_weights=wts,
#         out_dir=out_dir
#     )

# def wrapper_return_top_n(params, out_dir):
#     top_n = params.get("top_n")
#     if top_n is None:
#         return
#     scored = os.path.join(out_dir, "scored_regions.shp")
#     if os.path.isfile(scored):
#         return_top_n_overlay(
#             scored_shp=scored,
#             out_dir=out_dir,
#             top_n=int(top_n)
#         )

# def wrapper_score_by_policy(params, out_dir):
#     layer            = params.get("state_policy_layer")
#     preferred_states = params.get("preferred_states", [])
#     weight           = float(params.get("state_policy_weight", 0))
#     if not layer or not preferred_states or weight == 0:
#         return

#     shp = get_vector(layer, CURRENT_BBOX)
#     geo = next((f for f in os.listdir(out_dir) if f.endswith(".geojson")), None)
#     if not geo:
#         return
#     sites_fp = os.path.join(out_dir, geo)
#     gdf = gpd.read_file(sites_fp)
#     policy_gdf = gpd.read_file(shp)

#     # Spatially join sites to state polygons
#     joined = gpd.sjoin(
#         gdf.set_geometry("geometry"),
#         policy_gdf.set_geometry("geometry"),
#         how="left",
#         predicate="within"
#     )

#     # If policy layer has numeric 'policy_score', use it; else binary by state name
#     if "policy_score" in joined.columns:
#         scores = joined["policy_score"].fillna(0) * weight
#     else:
#         joined["state_name"] = joined.get("state_name", "")
#         scores = joined["state_name"].isin(preferred_states).astype(int) * weight

#     gdf["state_policy_score"] = scores
#     gdf.to_file(sites_fp, driver="GeoJSON")

#     # Incorporate into site scoring
#     score_sites(
#         sites_shp=sites_fp,
#         weights={"state_policy_score": weight},
#         out_dir=out_dir
#     )

# def wrapper_score_by_cost(params, out_dir):
#     raster_layer    = params.get("cost_raster")
#     max_threshold   = params.get("max_cost_threshold")
#     weight          = float(params.get("cost_weight", 0))
#     if not raster_layer or max_threshold is None or weight == 0:
#         return

#     cost_rast = get_raster(raster_layer, CURRENT_BBOX)
#     geo = next((f for f in os.listdir(out_dir) if f.endswith(".geojson")), None)
#     if not geo:
#         return
#     sites_fp = os.path.join(out_dir, geo)
#     gdf = gpd.read_file(sites_fp)

#     with rasterio.open(cost_rast) as src:
#         cost_vals = [
#             list(src.sample([(pt.x, pt.y)]))[0][0] or 0
#             for pt in gdf.geometry
#         ]

#     gdf["site_cost"] = cost_vals
#     # Optionally flag exceedance:
#     gdf["cost_ok"] = (gdf["site_cost"] <= float(max_threshold)).astype(int)
#     gdf.to_file(sites_fp, driver="GeoJSON")

#     # Penalize by cost if above threshold
#     gdf["cost_score"] = gdf["site_cost"] * weight
#     gdf.to_file(sites_fp, driver="GeoJSON")

#     score_sites(
#         sites_shp=sites_fp,
#         weights={"cost_score": weight},
#         out_dir=out_dir
#     )


# TOOL_WRAPPERS = {
#     "slope_analysis":       wrapper_slope,
#     "mask_forest":          wrapper_mask,
#     "buffer_features":      wrapper_buffer,
#     "score_sites":          wrapper_score,
#     "pixel_entropy":        wrapper_pixel_entropy,
#     "region_probability":   wrapper_region_probability,
#     "gaussian_fit":         wrapper_gaussian_fit,
#     "score_regions":        wrapper_score_regions,
#     "return_top_n_overlay": wrapper_return_top_n,
#     "score_by_policy":      wrapper_score_by_policy,
#     "score_by_cost":        wrapper_score_by_cost,
# }


# def process_task(task_id: str):
#     """
#     Load cot.json + dispatch each step. Errors are logged but do NOT halt.
#     """
#     task_dir = os.path.join(DATA_DIR, "output", task_id)
#     cot_f = os.path.join(task_dir, "cot.json")
#     steps = json.load(open(cot_f))

#     for i, step in enumerate(steps, start=1):
#         tool    = step.get("tool")
#         params  = step.get("params", {}) or {}
#         wrapper = TOOL_WRAPPERS.get(tool)
#         if not wrapper:
#             logger.warning(f"[{task_id}] Skipping unknown tool '{tool}'")
#             continue
#         try:
#             wrapper(params, task_dir)
#             logger.info(f"[{task_id}] Completed step {i} → {tool}")
#         except Exception as e:
#             logger.error(f"[{task_id}] Step {i} ({tool}) error: {e}")
#             with open(os.path.join(task_dir, f"error_step_{i}_{tool}.txt"), "w") as ef:
#                 ef.write(str(e))


# # ── Summary Utilities ──────────────────────────────────────────────────────

# def extract_properties(task_dir: str) -> list[dict]:
#     """
#     Read any .shp/.geojson in task_dir, compute centroid & area,
#     filter out any non-finite values.
#     """
#     results = []
#     for fn in os.listdir(task_dir):
#         if fn.lower().endswith((".shp", ".geojson")):
#             path = os.path.join(task_dir, fn)
#             gdf = gpd.read_file(path)
#             geo = gdf.to_crs(epsg=4326)
#             metr= gdf.to_crs(epsg=3857)
#             for pt, poly in zip(geo.geometry.centroid, metr.geometry):
#                 lat = float(pt.y)
#                 lon = float(pt.x)
#                 area = float(poly.area)
#                 if not (math.isfinite(lat) and math.isfinite(lon) and math.isfinite(area)):
#                     continue
#                 results.append({"lat": lat, "lon": lon, "area_m2": area})
#     return results


# def summarize_task(task_id: str) -> dict:
#     """
#     1) Parse cot.json → describe each tool run
#     2) Extract site properties
#     3) Load any stats
#     4) Identify overlay
#     5) Build a cohesive paragraph summary
#     """
#     task_dir = os.path.join(DATA_DIR, "output", task_id)
#     cot_f    = os.path.join(task_dir, "cot.json")
#     if not os.path.isfile(cot_f):
#         raise FileNotFoundError(f"No such task {task_id}")

#     # 1) Parse the CoT steps
#     try:
#         steps = json.load(open(cot_f))
#     except json.JSONDecodeError:
#         steps = []

#     descriptions = []
#     last_params  = {}
#     for step in steps:
#         tool = step.get("tool")
#         p    = step.get("params", {}) or {}
#         last_params = p

#         if tool == "slope_analysis":
#             dem  = p.get("dem_data") or p.get("dem_source") or "DEM"
#             bbox = p.get("bounding_box")
#             desc = f"computed terrain slope from '{dem}'" + (f" within bbox {bbox}" if bbox else "")
#         elif tool == "mask_forest":
#             forest = p.get("forest_data") or "forest layer"
#             desc = f"masked out forested areas using '{forest}'"
#         elif tool == "buffer_features":
#             feat = p.get("features") or "features layer"
#             dist = p.get("buffer_distance") or p.get("distance")
#             desc = f"buffered '{feat}' by {dist} units"
#         elif tool == "score_sites":
#             sp = p.get("solar_potential_data", "solar data")
#             mf = p.get("max_forest_damage")
#             tn = p.get("top_n_sites") or p.get("top_n")
#             desc = f"scored candidate sites using '{sp}' (max forest damage {mf}), selected top {tn}"
#         elif tool == "pixel_entropy":
#             rd = p.get("raster_data") or p.get("raster_source")
#             desc = f"calculated pixel entropy of '{rd}'"
#         elif tool == "region_probability":
#             rd  = p.get("raster_data") or p.get("raster_source")
#             thr = p.get("threshold")
#             desc = f"computed probability of pixels in '{rd}' exceeding {thr}"
#         elif tool == "gaussian_fit":
#             samples = p.get("samples", [])
#             desc = f"fitted a Gaussian to {len(samples)} samples"
#         elif tool == "score_regions":
#             regs = p.get("regions") or "regions layer"
#             en   = p.get("energy_type")
#             wts  = p.get("criteria_weights", {})
#             desc = f"scored '{regs}' for {en} energy with weights {wts}"
#         elif tool == "return_top_n_overlay":
#             top_n = p.get("top_n")
#             desc  = f"generated an overlay of the top {top_n} regions"
#         elif tool == "score_by_policy":
#             desc = (
#                 f"scored sites by state policy from '{p.get('state_policy_layer')}', "
#                 f"preferencing {p.get('preferred_states')} with weight {p.get('state_policy_weight')}"
#             )
#         elif tool == "score_by_cost":
#             desc = (
#                 f"scored sites by cost from '{p.get('cost_raster')}', "
#                 f"threshold {p.get('max_cost_threshold')} with weight {p.get('cost_weight')}"
#             )
#         else:
#             desc = f"ran '{tool}' with params {p}"

#         descriptions.append(desc)

#     # 2) Extract site properties
#     results = extract_properties(task_dir)
#     count   = len(results)

#     # 3) Load stats
#     stats_out = {}
#     for fn in ("pixel_entropy.json", "region_probability.json", "gaussian_fit.json"):
#         path = os.path.join(task_dir, fn)
#         if os.path.isfile(path):
#             stats_out.update(json.load(open(path)))

#     # 4) Overlay map
#     overlays = [f for f in os.listdir(task_dir) if f.endswith("_overlay.png")]
#     overlay  = overlays[0] if overlays else None

#     # 5) Build the summary paragraph
#     paragraph = []
#     if descriptions:
#         paragraph.append(
#             "We performed the following steps: " +
#             "; then ".join(descriptions) + "."
#         )
#     if count:
#         paragraph.append(f"In total, {count} candidate site(s) were identified.")
#     if stats_out:
#         stats_str = "; ".join(f"{k.replace('_',' ')} = {v}" for k, v in stats_out.items())
#         paragraph.append(f"Key statistics: {stats_str}.")
#     if overlay:
#         top_n = last_params.get("top_n")
#         paragraph.append(f"The overlay map '{overlay}' highlights the top {top_n} regions.")

#     summary = " ".join(paragraph)

#     # Save summary.txt
#     with open(os.path.join(task_dir, "summary.txt"), "w") as sf:
#         sf.write(summary)

#     return {
#         "summary":    summary,
#         "results":    results,
#         "overlay_map": overlay,
#     }



import re
import json
import uuid
import os
import math
import logging
import tempfile
import requests

import numpy as np
import geopandas as gpd
import rasterio
from rasterio.transform import from_bounds
from shapely.geometry import box as shapely_box, Point

from groq import Groq
from config import GROQ_API_KEY, DATA_DIR
from tools import (
    slope_analysis,
    mask_forest,
    buffer_features,
    score_sites,
    score_regions_by_energy,
    return_top_n_overlay,
)
import stats_tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
client = Groq(api_key=GROQ_API_KEY)

# Persist the user's BBOX for downstream steps
CURRENT_BBOX = None

class OrchestratorError(Exception):
    pass


# ── JSON Sanitation & LLM call ─────────────────────────────────────────────

def sanitize_raw_json(raw: str) -> str:
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
    if m:
        raw = m.group(1)
    raw = re.sub(r"//.*", "", raw)
    raw = re.sub(r"/\*[\s\S]*?\*/", "", raw)
    raw = re.sub(r",\s*(?=[}\]])", "", raw)
    return raw.strip()


def prepare_task(query: str, bbox: list) -> str:
    """
    1) Validate bbox
    2) Create task folder
    3) Prompt LLM for CoT
    4) Sanitize & parse JSON
    5) Write cot.json
    """
    global CURRENT_BBOX
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
        raise ValueError("bbox must be [minx, miny, maxx, maxy]")
    CURRENT_BBOX = bbox

    task_id = uuid.uuid4().hex
    task_dir = os.path.join(DATA_DIR, "output", task_id)
    os.makedirs(task_dir, exist_ok=True)

    prompt = (
        "You are GeoSolarX. Tools available:\n"
        " - slope_analysis(dem_data, bounding_box)\n"
        " - mask_forest(forest_data, bounding_box)\n"
        " - buffer_features(features, buffer_distance)\n"
        " - score_sites(solar_potential_data, max_forest_damage, top_n_sites)\n"
        " - pixel_entropy(raster_data)\n"
        " - region_probability(raster_data, threshold)\n"
        " - gaussian_fit(samples)\n"
        " - score_regions(regions, energy_type, criteria_weights)\n"
        " - return_top_n_overlay(top_n)\n\n"
        f"Chain-of-Thought for:\n  Query: {query}\n  BBOX: {bbox}\n"
        "Return a JSON array of steps: [{\"tool\":...,\"params\":{...}}, ...]."
    )
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}]
    )
    raw = resp.choices[0].message.content or ""
    clean = sanitize_raw_json(raw)
    try:
        steps = json.loads(clean)
    except Exception as e:
        logger.error("CoT JSON parse error: %s\n%s", e, clean)
        raise OrchestratorError(f"Bad CoT JSON: {e}")

    # Write cot.json immediately so /layers shows it at once
    with open(os.path.join(task_dir, "cot.json"), "w") as f:
        json.dump(steps, f, indent=2)

    return task_id


def get_cot(task_id: str) -> list:
    """Return the parsed cot.json for status."""
    path = os.path.join(DATA_DIR, "output", task_id, "cot.json")
    if not os.path.isfile(path):
        raise FileNotFoundError
    return json.load(open(path))


# ── WCS/WFS + Dummy fallbacks ──────────────────────────────────────────────

def fetch_raster_via_wcs(layer: str, bbox=None, crs="EPSG:4326") -> str:
    url = "http://localhost:8080/geoserver/wcs"
    params = {
        "service": "WCS", "version": "1.0.0", "request": "GetCoverage",
        "coverage": layer, "crs": crs, "format": "GeoTIFF",
        "width": 512, "height": 512
    }
    if bbox:
        params["bbox"] = ",".join(map(str, bbox))
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(suffix=".tif", delete=False)
    tmp.write(resp.content); tmp.flush()
    return tmp.name

def create_dummy_raster(bbox=None, width=256, height=256) -> str:
    if bbox:
        minx, miny, maxx, maxy = bbox
    else:
        minx, miny, maxx, maxy = -180, -90, 180, 90

    data = np.ones((height, width), dtype=np.float32)
    transform = from_bounds(minx, miny, maxx, maxy, width, height)
    meta = {
        "driver": "GTiff", "dtype": "float32", "count": 1,
        "crs": "EPSG:4326", "transform": transform,
        "width": width, "height": height
    }
    tmp = tempfile.NamedTemporaryFile(suffix=".tif", delete=False)
    with rasterio.open(tmp.name, "w", **meta) as dst:
        dst.write(data, 1)
    logger.info(f"Dummy raster → {tmp.name}")
    return tmp.name

def get_raster(layer: str, bbox=None) -> str:
    try:
        path = fetch_raster_via_wcs(layer, bbox)
        with rasterio.open(path): pass
        return path
    except Exception as e:
        logger.warning(f"WCS fetch failed for '{layer}': {e}")

    local = os.path.join(DATA_DIR, "input", f"{layer}.tif")
    if os.path.isfile(local):
        return local

    return create_dummy_raster(bbox)

def fetch_vector_via_wfs(layer: str) -> str:
    url = "http://localhost:8080/geoserver/wfs"
    params = {
        "service": "WFS", "version": "1.0.0", "request": "GetFeature",
        "typeName": layer, "outputFormat": "application/json"
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(suffix=".geojson", delete=False)
    tmp.write(resp.content); tmp.flush()
    return tmp.name

def create_dummy_vector(bbox=None) -> str:
    geom = shapely_box(*bbox) if bbox else shapely_box(-180, -90, 180, 90)
    gdf = gpd.GeoDataFrame({"geometry": [geom]}, crs="EPSG:4326")
    tmp = tempfile.NamedTemporaryFile(suffix=".geojson", delete=False)
    gdf.to_file(tmp.name, driver="GeoJSON")
    return tmp.name

def get_vector(layer: str, bbox=None) -> str:
    try:
        path = fetch_vector_via_wfs(layer)
        _ = gpd.read_file(path)
        return path
    except Exception:
        pass
    for ext in (".shp", ".geojson"):
        local = os.path.join(DATA_DIR, "input", f"{layer}{ext}")
        if os.path.isfile(local):
            return local
    return create_dummy_vector(bbox)

def generate_candidate_sites(bbox: list, out_dir: str, spacing=0.01) -> str:
    minx, miny, maxx, maxy = bbox
    xs = np.arange(minx, maxx, spacing)
    ys = np.arange(miny, maxy, spacing)
    pts = [Point(x, y) for x in xs for y in ys]
    gdf = gpd.GeoDataFrame(geometry=pts, crs="EPSG:4326")
    path = os.path.join(out_dir, "candidate_sites.geojson")
    gdf.to_file(path, driver="GeoJSON")
    return path


# ── Wrapper dispatch ───────────────────────────────────────────────────────

def wrapper_slope(params, out_dir):
    layer = params.get("dem_data") or params.get("dem_source") or "dem"
    dem = get_raster(layer, CURRENT_BBOX)
    slope_analysis(out_dir=out_dir, dem_path=dem, bounding_box=None)

def wrapper_mask(params, out_dir):
    layer = params.get("forest_data") or params.get("forest_data_source")
    if not layer:
        return
    shp = get_vector(layer, CURRENT_BBOX)
    slope_fp = os.path.join(out_dir, "slope.tif")
    raster_to_mask = slope_fp if os.path.isfile(slope_fp) else get_raster("dem", CURRENT_BBOX)
    mask_forest(raster_path=raster_to_mask, forest_shp=shp, out_dir=out_dir)

def wrapper_buffer(params, out_dir):
    layer = params.get("features")
    dist  = params.get("buffer_distance") or params.get("distance")
    if not layer or dist is None:
        return
    shp = get_vector(layer, CURRENT_BBOX)
    buffer_features(shp_path=shp, distance=dist, out_dir=out_dir)

def wrapper_score(params, out_dir):
    geo = next((f for f in os.listdir(out_dir) if f.endswith(".geojson")), None)
    sites_fp = os.path.join(out_dir, geo) if geo else generate_candidate_sites(CURRENT_BBOX, out_dir)
    gdf = gpd.read_file(sites_fp)

    if "solar_potential_data" in params:
        rast = get_raster(params["solar_potential_data"], CURRENT_BBOX)
        with rasterio.open(rast) as src:
            gdf["solar_potential"] = [
                list(src.sample([(pt.x, pt.y)]))[0][0] or 0 for pt in gdf.geometry
            ]

    mask_fp = os.path.join(out_dir, "masked.tif")
    if os.path.isfile(mask_fp):
        with rasterio.open(mask_fp) as src:
            gdf["forest_damage"] = [
                1 if (list(src.sample([(pt.x, pt.y)]))[0][0] is None) else 0
                for pt in gdf.geometry
            ]
    else:
        gdf["forest_damage"] = 0

    gdf.to_file(sites_fp, driver="GeoJSON")

    weights = {}
    if "solar_potential_data" in params:
        weights["solar_potential"] = 1.0
    if "max_forest_damage" in params:
        weights["forest_damage"] = -float(params["max_forest_damage"])
    score_sites(sites_shp=sites_fp, weights=weights, out_dir=out_dir)

def wrapper_pixel_entropy(params, out_dir):
    layer = params.get("raster_data") or params.get("raster_source")
    if not layer:
        return
    ent = stats_tools.pixel_entropy(get_raster(layer))
    with open(os.path.join(out_dir, "pixel_entropy.json"), "w") as f:
        json.dump({"pixel_entropy": ent}, f)

def wrapper_region_probability(params, out_dir):
    layer = params.get("raster_data") or params.get("raster_source")
    thr   = params.get("threshold")
    if not layer or thr is None:
        return
    prob = stats_tools.region_probability(get_raster(layer), float(thr))
    with open(os.path.join(out_dir, "region_probability.json"), "w") as f:
        json.dump({"region_probability": prob}, f)

def wrapper_gaussian_fit(params, out_dir):
    samples = params.get("samples")
    if not isinstance(samples, list):
        return
    fit = stats_tools.gaussian_fit(samples)
    with open(os.path.join(out_dir, "gaussian_fit.json"), "w") as f:
        json.dump(fit, f)

def wrapper_score_regions(params, out_dir):
    layer = params.get("regions")
    energy= params.get("energy_type")
    wts   = params.get("criteria_weights", {})
    if not layer or not energy:
        return
    shp = get_vector(layer, CURRENT_BBOX)
    score_regions_by_energy(regions_shp=shp,
                            energy_type=energy,
                            criteria_weights=wts,
                            out_dir=out_dir)

def wrapper_return_top_n(params, out_dir):
    top_n = params.get("top_n")
    if top_n is None:
        return
    scored = os.path.join(out_dir, "scored_regions.shp")
    if os.path.isfile(scored):
        return_top_n_overlay(scored_shp=scored,
                             out_dir=out_dir,
                             top_n=int(top_n))

TOOL_WRAPPERS = {
    "slope_analysis":       wrapper_slope,
    "mask_forest":          wrapper_mask,
    "buffer_features":      wrapper_buffer,
    "score_sites":          wrapper_score,
    "pixel_entropy":        wrapper_pixel_entropy,
    "region_probability":   wrapper_region_probability,
    "gaussian_fit":         wrapper_gaussian_fit,
    "score_regions":        wrapper_score_regions,
    "return_top_n_overlay": wrapper_return_top_n,
}


def process_task(task_id: str):
    """
    Load cot.json + dispatch each step. Errors are logged but do NOT halt.
    """
    task_dir = os.path.join(DATA_DIR, "output", task_id)
    cot_f = os.path.join(task_dir, "cot.json")
    steps = json.load(open(cot_f))

    for i, step in enumerate(steps, start=1):
        tool   = step.get("tool")
        params = step.get("params", {}) or {}
        wrapper= TOOL_WRAPPERS.get(tool)
        if not wrapper:
            logger.warning(f"[{task_id}] Skipping unknown tool '{tool}'")
            continue
        try:
            wrapper(params, task_dir)
            logger.info(f"[{task_id}] Completed step {i} → {tool}")
        except Exception as e:
            logger.error(f"[{task_id}] Step {i} ({tool}) error: {e}")
            with open(os.path.join(task_dir, f"error_step_{i}_{tool}.txt"), "w") as ef:
                ef.write(str(e))


# ── Summary ────────────────────────────────────────────────────────────────

def extract_properties(task_dir: str) -> list[dict]:
    """
    Read any .shp/.geojson in task_dir, compute centroid & area,
    and filter out any non-finite values.
    """
    results = []
    for fn in os.listdir(task_dir):
        if fn.lower().endswith((".shp", ".geojson")):
            path = os.path.join(task_dir, fn)
            gdf = gpd.read_file(path)
            geo = gdf.to_crs(epsg=4326)
            metr= gdf.to_crs(epsg=3857)
            for pt, poly in zip(geo.geometry.centroid, metr.geometry):
                lat = float(pt.y)
                lon = float(pt.x)
                area = float(poly.area)
                if not (math.isfinite(lat) and math.isfinite(lon) and math.isfinite(area)):
                    continue
                results.append({"lat": lat, "lon": lon, "area_m2": area})
    return results


# def summarize_task(task_id: str) -> dict:
#     """
#     1) Load cot.json
#     2) Extract valid site properties
#     3) Load any stats JSON
#     4) Identify PNG overlay
#     5) Prompt LLM for a concise human‐readable summary
#     """
#     task_dir = os.path.join(DATA_DIR, "output", task_id)
#     cot_f    = os.path.join(task_dir, "cot.json")
#     if not os.path.isfile(cot_f):
#         raise FileNotFoundError(f"No such task {task_id}")

#     steps   = json.load(open(cot_f))
#     results = extract_properties(task_dir)

#     stats_out = {}
#     for fn in ("pixel_entropy.json", "region_probability.json", "gaussian_fit.json"):
#         p = os.path.join(task_dir, fn)
#         if os.path.isfile(p):
#             stats_out.update(json.load(open(p)))

#     overlays = [f for f in os.listdir(task_dir) if f.endswith("_overlay.png")]
#     overlay  = overlays[0] if overlays else None

#     summary_prompt = (
#         "You are GeoSolarX Assistant.\n\n"
#         "Chain-of-Thought:\n" f"{json.dumps(steps, indent=2)}\n\n"
#         "Site properties:\n" f"{json.dumps(results, indent=2)}\n\n"
#         "Statistics:\n" f"{json.dumps(stats_out, indent=2)}\n\n"
#         f"Overlay map file: {overlay}\n\n"
#         "Provide a concise summary including locations and key metrics."
#     )
#     resp = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[{"role":"user","content":summary_prompt}]
#     )
#     summary = resp.choices[0].message.content.strip()

#     with open(os.path.join(task_dir, "summary.txt"), "w") as sf:
#         sf.write(summary)

#     return {
#         "summary":    summary,
#         "results":    results,
#         "overlay_map": overlay
#     }

def summarize_task(task_id: str) -> dict:
    """
    1) Load cot.json → describe each tool run in NL
    2) Extract site properties
    3) Load stats
    4) Identify overlay
    5) Build a cohesive paragraph summary
    """
    task_dir = os.path.join(DATA_DIR, "output", task_id)
    cot_f    = os.path.join(task_dir, "cot.json")
    if not os.path.isfile(cot_f):
        raise FileNotFoundError(f"No such task {task_id}")

    # 1) Parse the CoT steps
    try:
        steps = json.load(open(cot_f))
    except json.JSONDecodeError:
        steps = []

    descriptions = []
    last_params = {}
    for step in steps:
        tool = step.get("tool")
        p    = step.get("params", {})
        last_params = p

        if tool == "slope_analysis":
            dem  = p.get("dem_data") or p.get("dem_source") or "DEM"
            bbox = p.get("bounding_box")
            desc = f"computed terrain slope from '{dem}'" + (f" within bbox {bbox}" if bbox else "")
        elif tool == "mask_forest":
            forest = p.get("forest_data") or "forest layer"
            desc = f"masked out forested areas using '{forest}'"
        elif tool == "buffer_features":
            feat = p.get("features") or "features layer"
            dist = p.get("buffer_distance") or p.get("distance")
            desc = f"buffered '{feat}' by {dist} units"
        elif tool == "score_sites":
            sp = p.get("solar_potential_data", "solar data")
            mf = p.get("max_forest_damage")
            tn = p.get("top_n_sites") or p.get("top_n")
            desc = f"scored candidate sites using '{sp}' (max forest damage {mf}), selected top {tn}"
        elif tool == "pixel_entropy":
            rd = p.get("raster_data") or p.get("raster_source")
            desc = f"calculated pixel entropy of '{rd}'"
        elif tool == "region_probability":
            rd   = p.get("raster_data") or p.get("raster_source")
            thr  = p.get("threshold")
            desc = f"computed probability of pixels in '{rd}' exceeding {thr}"
        elif tool == "gaussian_fit":
            samples = p.get("samples", [])
            desc = f"fitted a Gaussian to {len(samples)} samples"
        elif tool == "score_regions":
            regs = p.get("regions") or "regions layer"
            en   = p.get("energy_type")
            wts  = p.get("criteria_weights", {})
            desc = f"scored '{regs}' for {en} energy with weights {wts}"
        elif tool == "return_top_n_overlay":
            top_n = p.get("top_n")
            desc  = f"generated an overlay of the top {top_n} regions"
        else:
            desc = f"ran '{tool}' with params {p}"

        descriptions.append(desc)

    # 2) Extract site properties
    results = extract_properties(task_dir)
    count   = len(results)

    # 3) Load stats
    stats_out = {}
    for fn in ("pixel_entropy.json", "region_probability.json", "gaussian_fit.json"):
        path = os.path.join(task_dir, fn)
        if os.path.isfile(path):
            stats_out.update(json.load(open(path)))

    # 4) Overlay map
    overlays = [f for f in os.listdir(task_dir) if f.endswith("_overlay.png")]
    overlay  = overlays[0] if overlays else None

    # 5) Build the summary paragraph
    paragraph = []
    if descriptions:
        paragraph.append(
            "We performed the following steps: " +
            "; then ".join(descriptions) + "."
        )
    if count:
        paragraph.append(f"In total, {count} candidate site(s) were identified.")
    if stats_out:
        stats_str = "; ".join(f"{k.replace('_',' ')} = {v}" for k, v in stats_out.items())
        paragraph.append(f"Key statistics: {stats_str}.")
    if overlay:
        # assume last step was return_top_n_overlay
        top_n = last_params.get("top_n")
        paragraph.append(f"The overlay map '{overlay}' highlights the top {top_n} regions.")

    summary = " ".join(paragraph)

    # Save summary.txt
    with open(os.path.join(task_dir, "summary.txt"), "w") as sf:
        sf.write(summary)

    return {
        "summary":    summary,
        "results":    results,
        "overlay_map": overlay,
    }
