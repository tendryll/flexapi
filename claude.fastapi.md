# Create a FastAPI application, with Pydantic, and SQLAlchemy using PostgreSQL, for a library application with the following endpoints:

/book POST

body (request):
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aleksandr.io/library.schema.json",
  "title": "Book",
  "description": "A request body to create a book in a library",
  "type": "object",
  "$defs": {
    "address": {
      "$anchor": "AddressSchema",
      "type": "object",
      "properties": {
        "address1": {
          "type": "string"
        },
        "address2": {
          "type": "string"
        },
        "city": {
          "type": "string"
        },
        "province": {
          "type": "string"
        },
        "country": {
          "type": "string"
        },
        "postalCode": {
          "type": "string"
        }
      },
      "required": ["address1", "city", "province", "country", "postalCode"]
    }
  },
  "properties": {
    "title": {
      "description": "The book title",
      "type": "string"
    },
    "description": {
      "description": "The book description",
      "type": "string"
    },
    "authors": {
      "description": "A list of the book's authors",
      "type": "array",
      "items": {
        "type": "string"
      },
      "minItems": 1,
      "uniqueItems": true
    },
    "isbn-10": {
      "description": "The book's ISBN-10",
      "type": "string"
    },
    "isbn-13": {
      "description": "The book's ISBN-13",
      "type": "string"
    },
    "publisher": {
      "description": "The book's publisher",
      "type": "string"
    },
    "publishingDate": {
      "description": "The publishing date",
      "type": "string",
      "format": "date"
    },
    "pageCount": {
      "description": "The book's page count",
      "type": "number"
    },
    "location": {
      "description": "The library location where the book is associated with",
      "$ref": "#/$defs/address"
    },
    "availability": {
      "description": "The book's availability",
      "type": "boolean"
    }
  },
  "required": ["title", "description", "authors", "publisher", "publishingDate", "pageCount"]
}
```

/book/{id} PUT

body (request):
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aleksandr.io/library.schema.json",
  "title": "Book",
  "description": "A request body to create a book in a library",
  "type": "object",
  "properties": {
    "location": {
      "description": "The library location where the book is associated with",
      "type": "string"
    },
    "availability": {
      "description": "The book's availability",
      "type": "boolean"
    }
  }
}
```

/book/{id} DELETE

/book/{id} GET

body (response):
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aleksandr.io/library.schema.json",
  "title": "Book",
  "description": "A request body to create a book in a library",
  "type": "object",
  "$defs": {
    "address": {
      "$anchor": "AddressSchema",
      "type": "object",
      "properties": {
        "address1": {
          "type": "string"
        },
        "address2": {
          "type": "string"
        },
        "city": {
          "type": "string"
        },
        "province": {
          "type": "string"
        },
        "country": {
          "type": "string"
        },
        "postalCode": {
          "type": "string"
        }
      },
      "required": ["address1", "city", "province", "country", "postalCode"]
    }
  },  
  "properties": {
    "title": {
      "description": "The book title",
      "type": "string"
    },
    "description": {
      "description": "The book description",
      "type": "string"
    },
    "authors": {
      "description": "A list of the book's authors",
      "type": "array",
      "items": {
        "type": "string"
      },
      "minItems": 1,
      "uniqueItems": true
    },
    "isbn-10": {
      "description": "The book's ISBN-10",
      "type": "string"
    },
    "isbn-13": {
      "description": "The book's ISBN-13",
      "type": "string"
    },
    "publisher": {
      "description": "The book's publisher",
      "type": "string"
    },
    "publishingDate": {
      "description": "The publishing date",
      "type": "string",
      "format": "date"
    },
    "pageCount": {
      "description": "The book's page count",
      "type": "number"
    },
    "location": {
      "description": "The library location where the book is associated with",
      "$ref": "#/$defs/address"
    },
    "availability": {
      "description": "The book's availability",
      "type": "boolean"
    }
  }
}
```

The following is the DDL for the PostgreSQL tables:

```sql
CREATE TABLE author (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    author text NOT NULL
);

CREATE TABLE location (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    address1 text NOT NULL,
    address2 text,
    city text NOT NULL,
    province text NOT NULL,
    country text NOT NULL,
    postalCode text
);

CREATE TABLE book (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    title text NOT NULL,
    description text NOT NULL,
    author_id UUID NOT NULL,
    isbn_10 text,
    isbn_13 text,
    publisher text NOT NULL,
    publishingDate date NOT NULL,
    page_count int NOT NULL,
    location_id UUID,
    availability boolean DEFAULT false,

    CONSTRAINT fk_book_location FOREIGN KEY (location_id) REFERENCES location (id)
);

CREATE TABLE book_author (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    author_id UUID NOT NULL,
    book_id UUID NOT NULL,

    CONSTRAINT fk_book_author_author FOREIGN KEY (author_id) references author (id),
    CONSTRAINT fk_book_author_book FOREIGN KEY (book_id) references book (id)
);
```

Use the tool uv for managing the project's dependencies. Add support for Ruff and ty.

---

Execute the following:

1. Create a Flyway script to create tables as per the following DDL:

```sql
CREATE TABLE author (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    author text NOT NULL
);

CREATE TABLE location (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    address1 text NOT NULL,
    address2 text,
    city text NOT NULL,
    province text NOT NULL,
    country text NOT NULL,
    postalCode text
);

CREATE TABLE book (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    title text NOT NULL,
    description text NOT NULL,
    author_id UUID NOT NULL,
    isbn_10 text,
    isbn_13 text,
    publisher text NOT NULL,
    publishingDate date NOT NULL,
    page_count int NOT NULL,
    location_id UUID,
    availability boolean DEFAULT false,

    CONSTRAINT fk_book_location FOREIGN KEY (location_id) REFERENCES location (id)
);

CREATE TABLE book_author (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    author_id UUID NOT NULL,
    book_id UUID NOT NULL,

    CONSTRAINT fk_book_author_author FOREIGN KEY (author_id) references author (id),
    CONSTRAINT fk_book_author_book FOREIGN KEY (book_id) references book (id)
);
```

2. Put the Flyway scripts in a directory named 'flyway' under the project root directory.
3. Create a Flyway script to insert mock data generated by Claude (you).
4. Update the docker-compose.yml file to add a Flyway container and that will execute the Flyway scripts.


### Additional Notes

When using FastAPI:

Using request-scoped resources provides several advantages:

Isolation: Each request operates in its own context, preventing shared state issues.
Resource Management: Resources are created and destroyed with each request, reducing the risk of memory leaks.
Testing: Easier to test individual components without interference from shared state.