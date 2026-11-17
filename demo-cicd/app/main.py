"""Swap space micro-service (demo): articles are kept in memory."""

from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Troc - La Petite Maison de l'Epouvante")


class ArticleIn(BaseModel):
    titre: str
    categorie: str
    type: Literal["echange", "don"]


class Article(ArticleIn):
    id: str


articles: dict[str, Article] = {}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/articles")
def list_articles() -> list[Article]:
    return list(articles.values())


@app.post("/articles", status_code=201)
def create_article(article: ArticleIn) -> Article:
    new_article = Article(id=str(uuid4()), **article.model_dump())
    articles[new_article.id] = new_article
    return new_article


@app.get("/articles/{article_id}")
def get_article(article_id: str) -> Article:
    if article_id not in articles:
        raise HTTPException(status_code=404, detail="Article not found")
    return articles[article_id]
