from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from datetime import date, datetime
import shutil

ROOT = Path(".")
DAY_MEDIA_DIR = ROOT / "day_media"
STATIC_DIR = ROOT / "static"

DAY_MEDIA_ROOT = Path("day_media")
DAY_MEDIA_ROOT.mkdir(parents=True, exist_ok=True)


DAY_MEDIA_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(ROOT)), name="static")

IMAGE_EXTS = {".jpg", ".jpeg", ".png"}
VIDEO_EXTS = {".mp4", ".mov"}


def build_static_url(path: Path) -> str:
    rel = path.relative_to(ROOT)
    return f"/static/{rel.as_posix()}"


def get_day_folder(day: str) -> Path:
    f = DAY_MEDIA_DIR / day
    f.mkdir(exist_ok=True)
    return f


@app.post("/upload_media")
async def upload_media(file: UploadFile = File(...)):
    today = date.today().isoformat()
    folder = get_day_folder(today)

    dest = folder / file.filename
    with dest.open("wb") as f:
        f.write(await file.read())

    return {"status": "ok", "path": str(dest)}


@app.get("/today_stats")
def today_stats():
    today = date.today().isoformat()
    folder = get_day_folder(today)

    photos = sum(1 for f in folder.iterdir() if f.suffix.lower() in IMAGE_EXTS)
    videos = sum(1 for f in folder.iterdir() if f.suffix.lower() in VIDEO_EXTS)

    return {"date": today, "photos": photos, "videos": videos}


@app.get("/today_media")
def today_media():
    today = date.today().isoformat()
    folder = get_day_folder(today)

    items = []
    for f in folder.iterdir():
        ext = f.suffix.lower()
        if ext in IMAGE_EXTS:
            t = "photo"
        elif ext in VIDEO_EXTS:
            t = "video"
        else:
            continue

        items.append({
            "id": str(f.relative_to(ROOT)),
            "type": t,
            "url": build_static_url(f),
        })

    return {"items": items}


class DeleteBody(BaseModel):
    id: str


@app.post("/delete_media")
def delete_media(body: DeleteBody):
    p = ROOT / body.id
    if p.exists():
        p.unlink()
        return {"status": "deleted"}
    return {"status": "not_found"}


@app.post("/generate_wrapup")
def generate_wrapup(force: bool = Query(False), day: str | None = None):
    from main import run_daily_wrapup, get_wrapup_output_path

    target_day = day or date.today().isoformat()
    out_path = get_wrapup_output_path(target_day)

    result = run_daily_wrapup(output_path=out_path, day=target_day)
    if not result:
        return {"status": "no_media"}

    return {"status": "ok", "video_url": build_static_url(out_path)}

@app.delete("/wrapup_today")
def delete_wrapup(day: str | None = None):
    from main import get_wrapup_output_path
    target = day or date.today().isoformat()
    p = get_wrapup_output_path(target)
    if p.exists():
        p.unlink()
        return {"status": "deleted"}
    return {"status": "not_found"}

@app.get("/wrapup_status")
def wrapup_status(day: str | None = None):
    from main import get_wrapup_output_path
    target = day or date.today().isoformat()
    out = get_wrapup_output_path(target)

    exists = out.exists()

    return {
        "date": target,
        "video_exists": exists,
        "after_schedule": True,  # SIMPLE MODE
        "scheduled_time": "23:30",
        "video_url": build_static_url(out) if exists else None
    }
@app.get("/past_days")
def past_days():
    days = []
    for f in STATIC_DIR.glob("timecapsule_*.mp4"):
        name = f.stem.split("_")
        if len(name) == 2:
            days.append(name[1])

    days.sort(reverse=True)

    return {"days": [{"date": d} for d in days]}

@app.post("/register_imported_media")
async def register_imported_media(file: UploadFile = File(...)):
    """
    Called by: ApiService.registerImportedMedia(path: file.path)

    Expects a multipart/form-data upload with a single field named "file".
    Saves it under: day_media/<today>/HHMMSS_micro.ext
    """
    today_str = date.today().isoformat()
    day_dir = DAY_MEDIA_ROOT / today_str
    day_dir.mkdir(parents=True, exist_ok=True)

    original_name = file.filename or "capture"
    ext = Path(original_name).suffix.lower()
    if not ext:
        ct = (file.content_type or "").lower()
        if ct.startswith("image/"):
            ext = ".jpg"
        elif ct.startswith("video/"):
            ext = ".mp4"
        else:
            ext = ".bin"
    ts = datetime.now().strftime("%H%M%S_%f")
    dest = day_dir / f"{ts}{ext}"
    data = await file.read()
    dest.write_bytes(data)

    return {
      "status": "ok",
      "saved_path": str(dest),
      "date": today_str,
    }
