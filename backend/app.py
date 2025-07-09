# # app.py

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import os, json
# from config import DATA_DIR
# from orchestrator import run_task, summarize_task, OrchestratorError

# app = FastAPI(title="GeoSolarX CoT GIS Agent")

# class Query(BaseModel):
#     query: str
#     bbox: list  # [minx, miny, maxx, maxy]

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# @app.post("/api/v1/query")
# def submit_query(q: Query):
#     task_id = run_task(q.query, q.bbox)
#     return {"task_id": task_id}

# @app.get("/api/v1/status/{task_id}")
# def get_status(task_id: str):
#     task_dir = os.path.join(DATA_DIR, "output", task_id)
#     cot_file = os.path.join(task_dir, "cot.json")
#     if not os.path.isfile(cot_file):
#         raise HTTPException(status_code=404, detail="Task not found")
#     with open(cot_file, "r") as f:
#         cot = json.load(f)
#     return {"chain_of_thought": cot, "completed": True}

# @app.get("/api/v1/results/{task_id}/layers")
# def list_layers(task_id: str):
#     task_dir = os.path.join(DATA_DIR, "output", task_id)
#     if not os.path.isdir(task_dir):
#         raise HTTPException(status_code=404, detail="Task not found")
#     return {"files": os.listdir(task_dir)}

# @app.get("/api/v1/results/{task_id}/download/{filename}")
# def download_file(task_id: str, filename: str):
#     from fastapi.responses import FileResponse
#     task_dir = os.path.join(DATA_DIR, "output", task_id)
#     path = os.path.join(task_dir, filename)
#     if not os.path.isfile(path):
#         raise HTTPException(status_code=404, detail="File not found")
#     return FileResponse(path, media_type="application/octet-stream", filename=filename)

# @app.get("/api/v1/summary/{task_id}")
# def get_summary(task_id: str):
#     try:
#         summary = summarize_task(task_id)
#     except FileNotFoundError:
#         raise HTTPException(status_code=404, detail="Task not found")
#     except OrchestratorError as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     return {"summary": summary}


# app.py

# backend/app.py

# from fastapi import FastAPI, HTTPException, BackgroundTasks
# import json                
# from fastapi.middleware.cors import CORSMiddleware

# from pydantic import BaseModel
# import os

# from config import DATA_DIR
# from orchestrator import prepare_task, process_task, get_cot, summarize_task

# app = FastAPI(title="GeoSolarX CoT GIS Agent")

# # ─── Enable CORS for React dev server ───────────────────────────────────────
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:8080"],
#     allow_methods=["GET", "POST", "OPTIONS"],
#     allow_headers=["*"],
# )
# # ─────────────────────────────────────────────────────────────────────────────

# class Query(BaseModel):
#     query: str
#     bbox: list  # [minx, miny, maxx, maxy]

# class QueryPayload(BaseModel):
#     query: str
#     bbox: List[float]  # [minx, miny, maxx, maxy]

# @app.on_event("startup")
# def ensure_output_dir():
#     os.makedirs(os.path.join(DATA_DIR, "output"), exist_ok=True)

# @app.get("/health")
# def health():
#     return {"status": "ok"}

# @app.post("/api/v1/query")
# def submit_query(q: Query, background_tasks: BackgroundTasks):
#     """
#     Prepare the task (writes out cot.json) then fire off full
#     processing in background.
#     """
#     try:
#         task_id = prepare_task(q.query, q.bbox)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

#     background_tasks.add_task(process_task, task_id)
#     return {"task_id": task_id}

# @app.get("/api/v1/status/{task_id}")
# def get_status(task_id: str):
#     """
#     Returns the Chain-of-Thought JSON immediately, plus a completed flag.
#     """
#     try:
#         cot = get_cot(task_id)
#     except FileNotFoundError:
#         raise HTTPException(status_code=404, detail="Task not found")
#     return {"chain_of_thought": cot, "completed": True}

# @app.get("/api/v1/summary/{task_id}")
# def get_summary(task_id: str):
#     """
#     When ready, returns:
#       {
#         "summary": "...",
#         "results": [ {lat, lon, area_m2}, … ],
#         "overlay_map": "top_3_overlay.png"  // or null
#       }
#     """
#     try:
#         res = summarize_task(task_id)
#     except FileNotFoundError:
#         raise HTTPException(status_code=404, detail="Task not found")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     return res

# @app.get("/api/v1/results/{task_id}/download/{filename}")
# def download_file(task_id: str, filename: str):
#     from fastapi.responses import FileResponse
#     task_dir = os.path.join(DATA_DIR, "output", task_id)
#     path = os.path.join(task_dir, filename)
#     if not os.path.isfile(path):
#         raise HTTPException(status_code=404, detail="File not found")
#     return FileResponse(path, media_type="application/octet-stream", filename=filename)

# @app.get("/api/v1/reports")
# def list_all_reports():
#     """
#     Returns all tasks under OUTPUT, each with download URLs for each file.
#     """
#     root = os.path.join(DATA_DIR, "output")
#     if not os.path.isdir(root):
#         return {"reports": []}

#     reports = []
#     for task_id in sorted(os.listdir(root)):
#         task_dir = os.path.join(root, task_id)
#         if not os.path.isdir(task_dir):
#             continue
#         files = sorted(os.listdir(task_dir))
#         entries = []
#         for fname in files:
#             entries.append({
#                 "name": fname,
#                 # this uses your existing download endpoint
#                 "url": f"/api/v1/results/{task_id}/download/{fname}"
#             })
#         reports.append({"task_id": task_id, "files": entries})

#     return {"reports": reports}

# @app.get("/api/v1/candidates/{task_id}")
# def get_candidate_sites(
#     task_id: str,
#     limit: int = Query(100, ge=1, le=10000, description="Max number of points to return")
# ):
#     """
#     Fetch up to `limit` lat/lng points from candidate_sites.geojson under that task.
#     """
#     task_dir = os.path.join(DATA_DIR, "output", task_id)
#     geojson_path = os.path.join(task_dir, "candidate_sites.geojson")
#     if not os.path.isfile(geojson_path):
#         raise HTTPException(
#             status_code=404,
#             detail="candidate_sites.geojson not found for this task"
#         )

#     try:
#         with open(geojson_path) as f:
#             gj = json.load(f)
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to read GeoJSON: {e}"
#         )

#     points = []
#     for feat in gj.get("features", [])[:limit]:
#         geom = feat.get("geometry", {})
#         if geom.get("type") == "Point":
#             lon, lat = geom.get("coordinates", [None, None])
#             if lat is not None and lon is not None:
#                 points.append({"lat": lat, "lng": lon})

#     return {"points": points}

# @app.post("/api/v1/query")
# def submit_query(q: QueryPayload, background_tasks: BackgroundTasks):
#     try:
#         task_id = prepare_task(q.query, q.bbox)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     background_tasks.add_task(process_task, task_id)
#     return {"task_id": task_id}

# @app.get("/api/v1/candidates/{task_id}")
# def get_candidate_sites(
#     task_id: str,
#     limit: int = Query(
#         100,
#         ge=1,
#         le=10000,
#         description="Max number of points to return"
#     ),
# ):
#     """
#     Fetch up to `limit` points from candidate_sites.geojson under that task.
#     """
#     task_dir = os.path.join(DATA_DIR, "output", task_id)
#     geojson_path = os.path.join(task_dir, "candidate_sites.geojson")
#     if not os.path.isfile(geojson_path):
#         raise HTTPException(
#             status_code=404,
#             detail="candidate_sites.geojson not found for this task"
#         )

#     try:
#         with open(geojson_path) as f:
#             gj = json.load(f)
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to read GeoJSON: {e}"
#         )

#     points = []
#     for feat in gj.get("features", [])[:limit]:
#         geom = feat.get("geometry", {})
#         if geom.get("type") == "Point":
#             lon, lat = geom.get("coordinates", [None, None])
#             if lat is not None and lon is not None:
#                 points.append({"lat": lat, "lng": lon})

#     return {"points": points}

# backend/app.py


import os
import json
import random
import smtplib
from email.message import EmailMessage
from typing import List

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from fastapi.responses import FileResponse
from datetime import datetime

from config import DATA_DIR
from orchestrator import prepare_task, process_task, get_cot, summarize_task

# ─── SMTP & BASE_URL CONFIG ───────────────────────────────────────────────────

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))          # 587 for TLS
SMTP_USER = os.getenv("SMTP_USER", "llmgisx@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "qcrk imif vfxm rjtg")
SMTP_FROM = os.getenv("SMTP_FROM", "llmgisx@gmail.com")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
# ───────────────────────────────────────────────────────────────────────────────

app = FastAPI(title="GeoSolarX CoT GIS Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryPayload(BaseModel):
    query: str
    bbox: List[float]

class EmailRequest(BaseModel):
    task_id: str
    email: EmailStr

@app.on_event("startup")
def ensure_output_dir():
    os.makedirs(os.path.join(DATA_DIR, "output"), exist_ok=True)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/query")
def submit_query(q: QueryPayload, background_tasks: BackgroundTasks):
    try:
        task_id = prepare_task(q.query, q.bbox)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    background_tasks.add_task(process_task, task_id)
    return {"task_id": task_id}

@app.get("/api/v1/status/{task_id}")
def get_status(task_id: str):
    try:
        cot = get_cot(task_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"chain_of_thought": cot, "completed": True}

@app.get("/api/v1/summary/{task_id}")
def get_summary(task_id: str):
    try:
        return summarize_task(task_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/results/{task_id}/download/{filename}")
def download_file(task_id: str, filename: str):
    task_dir = os.path.join(DATA_DIR, "output", task_id)
    path = os.path.join(task_dir, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="application/octet-stream", filename=filename)

@app.get("/api/v1/reports")
def list_all_reports():
    root = os.path.join(DATA_DIR, "output")
    if not os.path.isdir(root):
        return {"reports": []}
    reports = []
    for task_id in sorted(os.listdir(root)):
        task_dir = os.path.join(root, task_id)
        if not os.path.isdir(task_dir):
            continue
        files = sorted(os.listdir(task_dir))
        entries = [
            {"name": fn, "url": f"/api/v1/results/{task_id}/download/{fn}"}
            for fn in files
        ]
        reports.append({"task_id": task_id, "files": entries})
    return {"reports": reports}

@app.get("/api/v1/candidates/{task_id}")
def get_candidate_sites(
    task_id: str,
    limit: int = Query(10, ge=1, le=10000, description="Number of random points")
):
    task_dir = os.path.join(DATA_DIR, "output", task_id)
    geojson_path = os.path.join(task_dir, "candidate_sites.geojson")
    if not os.path.isfile(geojson_path):
        raise HTTPException(status_code=404,
            detail="candidate_sites.geojson not found for this task")
    try:
        with open(geojson_path) as f:
            gj = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read GeoJSON: {e}")
    feats = gj.get("features", [])
    sample = random.sample(feats, min(limit, len(feats)))
    points = []
    for feat in sample:
        geom = feat.get("geometry", {})
        if geom.get("type") == "Point":
            lon, lat = geom.get("coordinates", [None, None])
            if lat is not None and lon is not None:
                points.append({"lat": lat, "lng": lon})
    return {"points": points}

@app.post("/api/v1/email_reports")
def email_reports(req: EmailRequest):
    task_dir = os.path.join(DATA_DIR, "output", req.task_id)
    if not os.path.isdir(task_dir):
        raise HTTPException(status_code=404, detail="Task not found")
    files = sorted(os.listdir(task_dir))
    if not files:
        raise HTTPException(status_code=404, detail="No files to email")

    # Build HTML list items
    links_html = "".join(
        f'''
        <li style="
            margin: 8px 0;
            list-style-type: none;
            padding-left: 16px;
            position: relative;
        ">
          <span style="
              display: inline-block;
              width: 8px;
              height: 8px;
              background-color: #2E7D32;
              border-radius: 50%;
              position: absolute;
              left: 0;
              top: 6px;
          "></span>
          <a href="{BASE_URL}/api/v1/results/{req.task_id}/download/{fn}"
             style="
               color: #2E7D32;
               text-decoration: none;
               font-weight: 500;
             ">
            {fn}
          </a>
        </li>'''
        for fn in files
    )

    # Compose styled HTML
    html = f"""
    <html>
      <body style="
        margin:0;
        padding:0;
        background-color: #E8F5E9;
        font-family: Arial, sans-serif;
        color: #333;
      ">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td align="center">
              <table width="600" cellpadding="0" cellspacing="0" style="
                background-color: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
              ">
                <!-- Header -->
                <tr>
                  <td style="
                    background-color: #2E7D32;
                    padding: 20px;
                    text-align: center;
                  ">
                    <h1 style="
                      margin: 0;
                      color: #ffffff;
                      font-size: 24px;
                      font-weight: normal;
                    ">
                      GeoSolarX Reports
                    </h1>
                  </td>
                </tr>

                <!-- Body -->
                <tr>
                  <td style="padding: 24px;">
                    <p style="font-size: 16px; margin-top: 0;">
                      Hello,
                    </p>
                    <p style="font-size:16px;">
                      Here are your reports for <strong>{req.task_id}</strong>:
                    </p>
                    <ul style="padding: 0; margin: 16px 0 24px 0;">
                      {links_html}
                    </ul>
                    <p style="font-size:14px; color: #555;">
                      You can click each link to download the file directly.
                    </p>
                  </td>
                </tr>

                <!-- Footer -->
                <tr>
                  <td style="
                    background-color: #F1F8E9;
                    padding: 16px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                  ">
                    &copy; {datetime.utcnow().year} GeoSolarX — All rights reserved.
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    msg = EmailMessage()
    msg["Subject"] = f"Your GeoSolarX Reports for {req.task_id}"
    msg["From"] = SMTP_FROM
    msg["To"] = req.email
    msg.set_content("Please view this email in an HTML-capable client.")
    msg.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")

    return {"message": f"Email sent to {req.email}"}