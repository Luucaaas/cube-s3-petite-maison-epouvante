ARTICLE = {"titre": "Figurine Orc", "categorie": "figurines", "type": "echange"}


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_articles(client):
    assert client.get("/articles").json() == []
    client.post("/articles", json=ARTICLE)
    response = client.get("/articles")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_article(client):
    response = client.post("/articles", json=ARTICLE)
    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["titre"] == "Figurine Orc"


def test_create_article_invalid_type(client):
    response = client.post("/articles", json={**ARTICLE, "type": "vente"})
    assert response.status_code == 422


def test_get_article(client):
    article_id = client.post("/articles", json=ARTICLE).json()["id"]
    response = client.get(f"/articles/{article_id}")
    assert response.status_code == 200
    assert response.json()["id"] == article_id


def test_get_article_not_found(client):
    assert client.get("/articles/inconnu").status_code == 404
