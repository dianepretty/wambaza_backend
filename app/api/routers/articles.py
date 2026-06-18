import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from sqlalchemy.orm import Session
from app.schemas import ArticleBase, ArticleOut, ArticleAdminOut
from app.db.session import get_db
from app import models
from app.api.deps import require_publisher, require_admin, get_current_user

router = APIRouter(prefix="/articles", tags=["articles"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "static", "uploads")
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@router.post("/upload-image", dependencies=[Depends(require_publisher)])
async def upload_image(request: Request, file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WEBP, or GIF images are allowed")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    url = f"{str(request.base_url).rstrip('/')}/static/uploads/{filename}"
    return {"url": url}


@router.post("", response_model=ArticleOut, dependencies=[Depends(require_publisher)])
def create_article(payload: ArticleBase, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    article = models.Article(**payload.dict(), publisher_id=current_user.id)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@router.get("", response_model=list[ArticleOut])
def list_published(db: Session = Depends(get_db)):
    articles = db.query(models.Article).filter(models.Article.status == "published").all()
    return articles


@router.get("/my", response_model=list[ArticleOut], dependencies=[Depends(require_publisher)])
def list_my_articles(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Article).filter(models.Article.publisher_id == current_user.id)
    if status_filter:
        query = query.filter(models.Article.status == status_filter)
    return query.order_by(models.Article.updated_at.desc()).all()


@router.get("/all", response_model=list[ArticleAdminOut], dependencies=[Depends(require_admin)])
def list_all_articles(
    status_filter: Optional[str] = None,
    publisher_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Article, models.User).join(models.User, models.Article.publisher_id == models.User.id)
    if status_filter:
        query = query.filter(models.Article.status == status_filter)
    if publisher_id:
        query = query.filter(models.Article.publisher_id == publisher_id)
    rows = query.order_by(models.Article.updated_at.desc()).all()
    return [
        {
            "id": article.id,
            "title_en": article.title_en,
            "title_kin": article.title_kin,
            "title_lug": article.title_lug,
            "content_en": article.content_en,
            "content_kin": article.content_kin,
            "content_lug": article.content_lug,
            "cover_image_url": article.cover_image_url,
            "status": article.status,
            "publisher_id": article.publisher_id,
            "created_at": article.created_at,
            "updated_at": article.updated_at,
            "publisher_name": publisher.name,
            "publisher_email": publisher.email,
        }
        for article, publisher in rows
    ]


@router.get("/{id}", response_model=ArticleOut)
def get_article(id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.put("/{id}", response_model=ArticleOut, dependencies=[Depends(require_publisher)])
def edit_article(id: int, payload: ArticleBase, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    article = db.query(models.Article).filter(models.Article.id == id, models.Article.publisher_id == current_user.id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found or not owned")
    for k, v in payload.dict().items():
        setattr(article, k, v)
    db.commit()
    db.refresh(article)
    return article


@router.patch("/{id}/publish", dependencies=[Depends(require_publisher)])
def publish_article(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    article = db.query(models.Article).filter(models.Article.id == id, models.Article.publisher_id == current_user.id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found or not owned")
    article.status = "published"
    db.commit()
    return {"detail": "published"}


@router.patch("/{id}/unpublish")
def unpublish_article(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    article = db.query(models.Article).filter(models.Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    # allow publisher (owner) or admin
    if current_user.role != "admin" and article.publisher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    article.status = "draft"
    db.commit()
    return {"detail": "unpublished"}


@router.patch("/{id}/archive", dependencies=[Depends(require_publisher)])
def archive_article(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    article = db.query(models.Article).filter(models.Article.id == id, models.Article.publisher_id == current_user.id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found or not owned")
    article.status = "archived"
    db.commit()
    return {"detail": "archived"}


@router.delete("/{id}", dependencies=[Depends(require_publisher)])
def delete_article(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    article = db.query(models.Article).filter(models.Article.id == id, models.Article.publisher_id == current_user.id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found or not owned")
    db.delete(article)
    db.commit()
    return {"detail": "deleted"}
