-- Mock library data (fixed UUIDs so the relationships can be wired by hand).

INSERT INTO author (id, author)
VALUES ('0190a000-0000-7000-8000-0000000000a1', 'J.R.R. Tolkien'),
       ('0190a000-0000-7000-8000-0000000000a2', 'George R.R. Martin'),
       ('0190a000-0000-7000-8000-0000000000a3', 'Brandon Sanderson'),
       ('0190a000-0000-7000-8000-0000000000a4', 'Ursula K. Le Guin'),
       ('0190a000-0000-7000-8000-0000000000a5', 'Neil Gaiman'),
       ('0190a000-0000-7000-8000-0000000000a6', 'Terry Pratchett');

INSERT INTO location (id, address1, address2, city, province, country, postalCode)
VALUES ('0190a000-0000-7000-8000-0000000000c1', '789 Yonge St', NULL, 'Toronto', 'ON', 'Canada', 'M4W 2G8'),
       ('0190a000-0000-7000-8000-0000000000c2', '1200 Riverside Dr', 'Unit 3', 'Vancouver', 'BC', 'Canada', 'V5K 0A1'),
       ('0190a000-0000-7000-8000-0000000000c3', '500 Rue Sainte-Catherine', NULL, 'Montreal', 'QC', 'Canada',
        'H2X 1L2');

INSERT INTO book
(id, title, description, isbn_10, isbn_13, publisher, publishingDate, page_count, location_id, availability)
VALUES ('0190a000-0000-7000-8000-0000000000b1', 'The Hobbit',
        'Bilbo Baggins is swept into a quest to reclaim the Lonely Mountain from the dragon Smaug.',
        '054792822X', '9780547928227', 'Houghton Mifflin',
        '1937-09-21', 310, '0190a000-0000-7000-8000-0000000000c1', true),

       ('0190a000-0000-7000-8000-0000000000b2', 'A Game of Thrones',
        'Noble families vie for control of the Iron Throne in the land of Westeros.',
        '0553103547', '9780553103540', 'Bantam Books',
        '1996-08-06', 694, '0190a000-0000-7000-8000-0000000000c2', true),

       ('0190a000-0000-7000-8000-0000000000b3', 'The Way of Kings',
        'On the storm-scoured world of Roshar, war rages as ancient powers stir once more.',
        '0765326353', '9780765326355', 'Tor Books',
        '2010-08-31', 1007, '0190a000-0000-7000-8000-0000000000c1', false),

       ('0190a000-0000-7000-8000-0000000000b4', 'A Wizard of Earthsea',
        'A gifted young wizard comes of age and confronts the shadow he himself unleashed.',
        '0553383043', '9780553383041', 'Parnassus Press',
        '1968-11-01', 205, '0190a000-0000-7000-8000-0000000000c3', true),

       ('0190a000-0000-7000-8000-0000000000b5', 'Good Omens',
        'An angel and a demon team up to avert the apocalypse, having grown rather fond of Earth.',
        '0060853980', '9780060853983', 'Gollancz',
        '1990-05-10', 288, '0190a000-0000-7000-8000-0000000000c2', true);

-- book_author junction (Good Omens has two authors).
INSERT INTO book_author (id, author_id, book_id)
VALUES ('0190a000-0000-7000-8000-0000000000e1', '0190a000-0000-7000-8000-0000000000a1',
        '0190a000-0000-7000-8000-0000000000b1'),
       ('0190a000-0000-7000-8000-0000000000e2', '0190a000-0000-7000-8000-0000000000a2',
        '0190a000-0000-7000-8000-0000000000b2'),
       ('0190a000-0000-7000-8000-0000000000e3', '0190a000-0000-7000-8000-0000000000a3',
        '0190a000-0000-7000-8000-0000000000b3'),
       ('0190a000-0000-7000-8000-0000000000e4', '0190a000-0000-7000-8000-0000000000a4',
        '0190a000-0000-7000-8000-0000000000b4'),
       ('0190a000-0000-7000-8000-0000000000e5', '0190a000-0000-7000-8000-0000000000a5',
        '0190a000-0000-7000-8000-0000000000b5'),
       ('0190a000-0000-7000-8000-0000000000e6', '0190a000-0000-7000-8000-0000000000a6',
        '0190a000-0000-7000-8000-0000000000b5');
