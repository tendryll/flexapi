Feature: Book REST API

  As a user I want to create, read, update, and delete books

  Scenario: Create a new book
    # book contents are located at tests/resources/book-1.content.json
    Given book 1
    When the book is created
    Then the response status is 201
    And the response has authors "Alan Donovan, Brian Kernighan"
    And the response availability is true

  Scenario: Retrieve an existing book
    # book id = 0190a000-0000-7000-8000-0000000000b1
    Given a book with an id = "0190a000-0000-7000-8000-0000000000b1"
    When the book is retrieved
    Then the response status is 200
    And the response title is "The Hobbit"

  Scenario: Retrieve a book that does not exist
    # book id = 00000000-0000-0000-0000-000000000000
    Given a book with an id = "00000000-0000-0000-0000-000000000000"
    When the book is not found
    Then the response status is 404

  Scenario: Update a book's availability
    Given a book with an id = "0190a000-0000-7000-8000-0000000000b1"
    And the book details to update are in "book-2.content.json"
    When the book is updated
    Then the response status is 200
    And the response availability is false

  Scenario: Delete a book
    Given a book with an id = "0190a000-0000-7000-8000-0000000000b1"
    When the book is deleted
    Then the response status is 204
    And book returns 404