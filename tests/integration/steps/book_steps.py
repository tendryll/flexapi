"""Step definitions for the /book REST endpoints (tests/integration/books.feature)."""

import json
import os

from behave import given, then, when

# tests/resources holds the JSON book payloads referenced by the feature file.
_RESOURCES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "resources",
)


def _run(context, coro):
    """Drive an async httpx call on the scenario's shared event loop."""
    return context.loop.run_until_complete(coro)


def _to_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def _load_resource(filename: str) -> dict:
    with open(os.path.join(_RESOURCES, filename), encoding="utf-8") as handle:
        return json.load(handle)


@given("book {number:d}")
def step_load_book(context, number):
    context.book_payload = _load_resource(f"book-{number}.content.json")


@given('a book with an id = "{book_id}"')
def step_book_with_id(context, book_id):
    context.book_id = book_id


@given('the book details to update are in "{filename}"')
def step_update_details(context, filename):
    context.update_payload = _load_resource(filename)


@when("the book is created")
def step_create(context):
    context.response = _run(context, context.client.post("/book", json=context.book_payload))
    if context.response.status_code == 201:
        context.book_id = context.response.json()["id"]


@when("the book is retrieved")
def step_retrieve(context):
    context.response = _run(context, context.client.get(f"/book/{context.book_id}"))


@when("the book is not found")
def step_not_found(context):
    context.response = _run(context, context.client.get(f"/book/{context.book_id}"))


@when("the book is updated")
def step_update(context):
    payload = context.update_payload
    # PUT accepts a BookUpdate body (availability + a location *UUID string*),
    # not the full create payload — so forward only the fields it understands.
    # The create-shaped location address object is not a valid update value.
    body = {"availability": payload["availability"]}
    if isinstance(payload.get("location"), str):
        body["location"] = payload["location"]
    context.response = _run(context, context.client.put(f"/book/{context.book_id}", json=body))


@when("the book is deleted")
def step_delete(context):
    context.response = _run(context, context.client.delete(f"/book/{context.book_id}"))


@then("the response status is {code:d}")
def step_status(context, code):
    assert context.response.status_code == code, context.response.text


@then('the response has authors "{authors}"')
def step_authors(context, authors):
    expected = sorted(name.strip() for name in authors.split(","))
    assert sorted(context.response.json()["authors"]) == expected


@then("the response availability is {value}")
def step_availability(context, value):
    assert context.response.json()["availability"] is _to_bool(value)


@then('the response title is "{title}"')
def step_title(context, title):
    assert context.response.json()["title"] == title


@then("book returns 404")
def step_book_returns_404(context):
    resp = _run(context, context.client.get(f"/book/{context.book_id}"))
    assert resp.status_code == 404, resp.text
