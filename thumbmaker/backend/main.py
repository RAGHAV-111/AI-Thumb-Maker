import uuid
from urllib.parse import quote

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from imagekitio import ImageKit
from sqlalchemy.orm import Session

import config
import models
import schemas
from database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ThumbMaker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

imagekit = ImageKit(private_key=config.IMAGEKIT_PRIVATE_KEY) if config.IMAGEKIT_PRIVATE_KEY else None


@app.get("/")
def root():
    return {"status": "ThumbMaker API is running"}


@app.get("/thumbnails", response_model=list[schemas.ThumbnailOut])
def list_thumbnails(db: Session = Depends(get_db)):
    return db.query(models.Thumbnail).order_by(models.Thumbnail.created_at.desc()).all()


@app.get("/thumbnails/{thumbnail_id}", response_model=schemas.ThumbnailOut)
def get_thumbnail(thumbnail_id: int, db: Session = Depends(get_db)):
    thumbnail = db.query(models.Thumbnail).filter(models.Thumbnail.id == thumbnail_id).first()
    if not thumbnail:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return thumbnail


@app.post("/thumbnails/generate", response_model=schemas.ThumbnailOut)
def generate_thumbnail(payload: schemas.ThumbnailCreate, db: Session = Depends(get_db)):
    if not imagekit:
        raise HTTPException(status_code=500, detail="IMAGEKIT_PRIVATE_KEY is not configured")

    try:
        pollinations_url = f"https://image.pollinations.ai/prompt/{quote(payload.prompt)}"
        resp = httpx.get(
            pollinations_url,
            params={"width": 1024, "height": 1024, "nologo": "true"},
            timeout=60,
            follow_redirects=True,
        )
        resp.raise_for_status()
        image_bytes = resp.content
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Image generation failed: {exc}")

    try:
        upload = imagekit.files.upload(
            file=image_bytes,
            file_name=f"{uuid.uuid4().hex}.jpg",
            folder="/thumbmaker",
            use_unique_file_name=True,
        )
        image_url = upload.url
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"ImageKit upload failed: {exc}")

    if not image_url:
        raise HTTPException(status_code=502, detail="ImageKit upload did not return a URL")

    thumbnail = models.Thumbnail(title=payload.title, prompt=payload.prompt, image_url=image_url)
    db.add(thumbnail)
    db.commit()
    db.refresh(thumbnail)
    return thumbnail


@app.delete("/thumbnails/{thumbnail_id}")
def delete_thumbnail(thumbnail_id: int, db: Session = Depends(get_db)):
    thumbnail = db.query(models.Thumbnail).filter(models.Thumbnail.id == thumbnail_id).first()
    if not thumbnail:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    db.delete(thumbnail)
    db.commit()
    return {"status": "deleted"}
