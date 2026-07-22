"""End-to-end tests for the /book endpoints."""

from httpx import AsyncClient

BOOK_PAYLOAD = {
    "title": "The Go Programming Language",
    "description": "A comprehensive introduction to Go.",
    "authors": ["Alan Donovan", "Brian Kernighan"],
    "isbn-10": "0134190440",
    "isbn-13": "9780134190440",
    "publisher": "Addison-Wesley",
    "publishingDate": "2015-10-26",
    "pageCount": 380,
    "location": {
        "address1": "789 Yonge St",
        "city": "Toronto",
        "province": "ON",
        "country": "Canada",
        "postalCode": "M4W 2G8",
    },
    "availability": True,
}


async def test_create_and_get_book(client: AsyncClient) -> None:
    resp = await client.post("/book", json=BOOK_PAYLOAD)
    assert resp.status_code == 201, resp.text
    body = resp.json()

    book_id = body["id"]
    assert sorted(body["authors"]) == ["Alan Donovan", "Brian Kernighan"]
    assert body["isbn-10"] == "0134190440"
    assert body["pageCount"] == 380
    assert body["publishingDate"] == "2015-10-26"
    assert body["location"]["postalCode"] == "M4W 2G8"
    assert body["availability"] is True

    get_resp = await client.get(f"/book/{book_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == BOOK_PAYLOAD["title"]


async def test_update_availability(client: AsyncClient) -> None:
    book_id = (await client.post("/book", json=BOOK_PAYLOAD)).json()["id"]

    resp = await client.put(f"/book/{book_id}", json={"availability": False})
    assert resp.status_code == 200
    assert resp.json()["availability"] is False


async def test_update_location_requires_valid_uuid(client: AsyncClient) -> None:
    book_id = (await client.post("/book", json=BOOK_PAYLOAD)).json()["id"]

    resp = await client.put(f"/book/{book_id}", json={"location": "not-a-uuid"})
    assert resp.status_code == 422


async def test_delete_book(client: AsyncClient) -> None:
    book_id = (await client.post("/book", json=BOOK_PAYLOAD)).json()["id"]

    del_resp = await client.delete(f"/book/{book_id}")
    assert del_resp.status_code == 204

    assert (await client.get(f"/book/{book_id}")).status_code == 404


async def test_create_rejects_duplicate_authors(client: AsyncClient) -> None:
    payload = {**BOOK_PAYLOAD, "authors": ["Same", "Same"]}
    resp = await client.post("/book", json=payload)
    assert resp.status_code == 422


async def test_get_missing_book_returns_404(client: AsyncClient) -> None:
    resp = await client.get("/book/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
