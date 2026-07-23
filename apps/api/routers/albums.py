from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.album import Album
from models.place import Place
from schemas.place import AlbumResponse

router = APIRouter(prefix="/places/{place_id}/albums", tags=["albums"])

STORAGE_DIR = Path(__file__).resolve().parents[1] / "storage" / "covers"
if not STORAGE_DIR.parent.exists():
    STORAGE_DIR = Path(__file__).resolve().parents[3] / "storage" / "covers"
MAX_IMAGE_SIZE = 10 * 1024 * 1024
ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


async def _require_place(place_id: UUID, db: AsyncSession) -> None:
    if await db.get(Place, place_id) is None:
        raise HTTPException(status_code=404, detail="Place not found")


@router.post("", response_model=AlbumResponse, status_code=201)
async def upload_album_image(
    place_id: UUID,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> AlbumResponse:
    await _require_place(place_id, db)
    suffix = Path(image.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES or not (image.content_type or "").startswith("image/"):
        raise HTTPException(status_code=422, detail="Upload a JPG, PNG, WEBP, or GIF image")
    contents = await image.read()
    if not contents or len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=422, detail="Image must be between 1 byte and 10 MB")

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{suffix}"
    target = STORAGE_DIR / filename
    target.write_bytes(contents)
    album = Album(place_id=place_id, image_url=f"/storage/covers/{filename}")
    db.add(album)
    try:
        await db.commit()
        await db.refresh(album)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    return AlbumResponse.model_validate(album)


@router.delete("/{album_id}", status_code=204)
async def delete_album_image(place_id: UUID, album_id: UUID, db: AsyncSession = Depends(get_db)) -> None:
    album = (await db.execute(select(Album).where(Album.id == album_id, Album.place_id == place_id))).scalar_one_or_none()
    if album is None:
        raise HTTPException(status_code=404, detail="Album image not found")
    filename = Path(album.image_url).name
    target = (STORAGE_DIR / filename).resolve()
    storage_root = STORAGE_DIR.resolve()
    await db.delete(album)
    await db.commit()
    if target.parent == storage_root:
        target.unlink(missing_ok=True)
