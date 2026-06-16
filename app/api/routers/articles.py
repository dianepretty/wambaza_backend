from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import ArticleBase, ArticleOut
from app.db.session import get_db
from app import models
from app.api.deps import require_publisher, require_admin, get_current_user

router = APIRouter(prefix="/articles", tags=["articles"])


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
def list_my_articles(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    articles = db.query(models.Article).filter(models.Article.publisher_id == current_user.id).all()
    return articles


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


@router.delete("/{id}", dependencies=[Depends(require_publisher)])
def delete_article(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    article = db.query(models.Article).filter(models.Article.id == id, models.Article.publisher_id == current_user.id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found or not owned")
    db.delete(article)
    db.commit()
    return {"detail": "deleted"}
