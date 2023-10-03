DROP TABLE IF EXISTS users;
CREATE TABLE users
(
    user_id TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    scout_role_id INTEGER,
    FOREIGN KEY (role_id) REFERENCES user_roles(role_id),
    FOREIGN KEY (scout_role_id) REFERENCES scout_roles(scout_role_id)
);

DROP TABLE IF EXISTS user_roles;
CREATE TABLE user_roles
(
    role_id INTEGER PRIMARY KEY,
    role TEXT NOT NULL
);

INSERT INTO user_roles (role_id, role)
VALUES
    (1, 'User'),
    (2, 'Scout'),
    (3, 'Admin');

DROP TABLE IF EXISTS scout_roles;
CREATE TABLE scout_roles
(
    scout_role_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    min_age INTEGER NOT NULL
);

INSERT INTO scout_roles (scout_role_id, name, min_age)
VALUES
    (0, 'Beaver', 6),
    (1, 'Cub', 9),
    (2, 'Scout', 12),
    (3, 'Venture', 16),
    (4, 'Leader', 18);

DROP TABLE IF EXISTS scout_codes;
CREATE TABLE scout_codes
(
    scout_role_id INTEGER NOT NULL,
    code TEXT PRIMARY KEY,
    date DATE NOT NULL,
    FOREIGN KEY (scout_role_id) REFERENCES scout_roles(scout_role_id)
);

INSERT INTO scout_codes (scout_role_id, code, date)
VALUES
    (0, '1111', '2023-02-01'),
    (1, '1112', '2023-02-01'),
    (2, '1113', '2023-02-01'),
    (3, '1114', '2023-02-01'),
    (4, '1115', '2023-02-01');


DROP TABLE IF EXISTS shop;
CREATE TABLE shop 
(
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    colour TEXT NOT NULL,
    description TEXT NOT NULL,
    image_path TEXT NOT NULL,
    stock INTEGER NOT NULL,
    month_sales INTEGER NOT NULL
);


INSERT INTO shop (name, category, price, colour, description, image_path, stock, month_sales)
VALUES
    ('I love Scouts Mug', 'Mug', 9.99, 'White', 'Show your scout love with this lovely cup.', 'love-scouts-mug.jpg', 20, 3),
    ('Swiss Utility Knife', 'Tools', 89.99, 'Red', 'You won''t need many tools with one of this uh?', 'swiss-army-knife.webp', 30, 15),
    ('Trek First Aid Kit', 'First-Aid', 19.99, 'Red', 'Sorted with multiple types of bandages and dressings. Sterile scissors and tweezers included.', 'trek-first-aid.jpg', 30, 5),
    ('Emergency Blanket', 'First-Aid', 7.99, 'Orange', 'Reflects 90% of radiated body heat. Both waterproof & windproof.', 'emergency-blanket.jpg', 30, 3),
    ('Scout Group Mug', 'Mug', 9.99, 'White', 'Take us with you everytime you sip out that tea.', 'mug_logo_white.png', 30, 0),
    ('Scout Group Neckerchief', 'Neckerchief', 12.99, 'Grey', 'A classic.', 'scout-neckerchief.jpg', 30, 0),
    ('Scout Group pen', 'Stationery', 2.99, 'Black', 'Yeah, it''s just a pen. Our pen.', 'pen_logo_black.jpg', 20, 2),
    ('Keep Calm Mug', 'Mug', 9.99, 'White', 'Perfect for when having to chill between scouting expeditions', 'mug_keepcalm_white.png', 30, 8),
    ('Scout Group Thermos', 'Tools', 19.99, 'Green', 'Keeps your coffee hot up to 24hours!', 'scout-group-thermos.jpg', 30, 1),
    ('Lowe Alpine Backpack', 'Backpacks', 69.99, 'Grey', 'Capacity of 30 liters. Inspired by the original design of the Lowe brothers in 1985.', 'backpack.jpg', 30, 0),
    ('Lowe Alpine Edge Backpack', 'Backpacks', 59.99, 'Blue', 'Capacity of 26 liters. Dynamic, versatile daypack that is simply ideal for outdoor enthusiasts.', 'backpack-2.jpg', 30, 2),
    ('Pocket compass', 'Tools', 9.99, 'Golden', 'Keep track of where you are when you aren''t that sure of where you are.', 'pocket-compass.jpg', 20, 8),
    ('Scout Group Diary', 'Stationery', 7.99, 'Black', 'Rule Nº2 of the scout: keep organised.', 'diary_scouts.jpg', 15, 25);


DROP TABLE IF EXISTS product_sales;
CREATE TABLE product_sales
(
    product_id INTEGER NOT NULL,
    sales INTEGER NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES shop(product_id)
);

INSERT INTO product_sales (product_id, sales, date)
VALUES
    (1, 8, '2022-09-01'),
    (2, 6, '2022-09-01'),
    (3, 12, '2022-09-01'),
    (4, 4, '2022-09-01'),
    (5, 9, '2022-09-01'),
    (6, 5, '2022-09-01'),
    (7, 3, '2022-09-01'),
    (8, 10, '2022-09-01'),
    (9, 7, '2022-09-01'),
    (10, 2, '2022-09-01'),
    (11, 6, '2022-09-01'),
    (12, 19, '2022-09-01'),
    (13, 9, '2022-09-01'),
    (1, 10, '2022-10-01'),
    (2, 2, '2022-10-01'),
    (3, 8, '2022-10-01'),
    (4, 3, '2022-10-01'),
    (5, 5, '2022-10-01'),
    (6, 7, '2022-10-01'),
    (7, 4, '2022-10-01'),
    (8, 15, '2022-10-01'),
    (9, 6, '2022-10-01'),
    (10, 8, '2022-10-01'),
    (11, 9, '2022-10-01'),
    (12, 13, '2022-10-01'),
    (13, 4, '2022-10-01'),
    (1, 7, '2022-11-01'),
    (2, 9, '2022-11-01'),
    (3, 6, '2022-11-01'),
    (4, 2, '2022-11-01'),
    (5, 10, '2022-11-01'),
    (6, 3, '2022-11-01'),
    (7, 6, '2022-11-01'),
    (8, 12, '2022-11-01'),
    (9, 5, '2022-11-01'),
    (10, 1, '2022-11-01'),
    (11, 8, '2022-11-01'),
    (12, 9, '2022-11-01'),
    (13, 11, '2022-11-01'),
    (1, 15, '2022-12-01'),
    (2, 8, '2022-12-01'),
    (3, 21, '2022-12-01'),
    (4, 12, '2022-12-01'),
    (5, 4, '2022-12-01'),
    (6, 16, '2022-12-01'),
    (7, 5, '2022-12-01'),
    (8, 20, '2022-12-01'),
    (9, 6, '2022-12-01'),
    (10, 3, '2022-12-01'),
    (11, 9, '2022-12-01'),
    (12, 7, '2022-12-01'),
    (13, 18, '2022-12-01'),
    (1, 4, '2023-01-01'),
    (2, 0, '2023-01-01'),
    (3, 10, '2023-01-01'),
    (4, 2, '2023-01-01'),
    (5, 0, '2023-01-01'),
    (6, 4, '2023-01-01'),
    (7, 7, '2023-01-01'),
    (8, 16, '2023-01-01'),
    (9, 8, '2023-01-01'),
    (10, 1, '2023-01-01'),
    (11, 5, '2023-01-01'),
    (12, 10, '2023-01-01'),
    (13, 11, '2023-01-01'),
    (1, 3, '2023-02-01'),
    (2, 4, '2023-02-01'),
    (3, 20, '2023-02-01'),
    (4, 5, '2023-02-01'),
    (5, 10, '2023-02-01'),
    (6, 6, '2023-02-01'),
    (7, 8, '2023-02-01'),
    (8, 22, '2023-02-01'),
    (9, 2, '2023-02-01'),
    (10, 9, '2023-02-01'),
    (11, 12, '2023-02-01'),
    (12, 4, '2023-02-01'),
    (13, 5, '2023-02-01');

DROP TABLE IF EXISTS deleted_products;
CREATE TABLE deleted_products 
(
    product_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    colour TEXT NOT NULL,
    description TEXT NOT NULL,
    image_path TEXT NOT NULL,
    month_sales INTEGER,
    FOREIGN KEY (product_id) REFERENCES shop(product_id)
);

DROP TABLE IF EXISTS activities;
CREATE TABLE activities
(
    activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    price REAL NOT NULL,
    capacity INTEGER NOT NULL
);

INSERT INTO activities (date, name, category, difficulty, price, capacity)
VALUES
    ('2023-03-25', 'Hike to the Galtees', 'Hike', 'Beginners', 14.99, 19),
    ('2023-04-01', 'Kayak in Lee River', 'Kayaking', 'Medium', 44.99, 11),
    ('2023-04-16', 'Kayak at open see', 'Kayaking', 'Advanced', 59.99, 7),
    ('2023-04-15', '2-day hike (camp gear not provided)', 'Hike', 'Medium', 29.99, 25),
    ('2023-04-22', 'Basic First Aid Course', 'First Aid', 'Beginners', 29.99, 25),
    ('2023-04-23', 'Advanced Aid Course', 'First Aid', 'Advanced', 34.99, 25),
    ('2023-05-13', '2-day Mountain First Aid Course', 'First Aid', 'Medium', 49.99, 25),
    ('2023-05-06', 'Backwoods cooking', 'Outdoor cooking', 'Beginners', 14.99, 17),
    ('2023-05-20', 'Hike to Carauntoohil', 'Hike', 'Medium', 14.99, 25),
    ('2023-06-17', 'End of Season ''Come&Join'' hike', 'Hike', 'Beginners', 0, 75);

DROP TABLE IF EXISTS booked_activities;
CREATE TABLE booked_activities
(
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    booking_fee REAL NOT NULL,
    booking_date DATE NOT NULL,
    FOREIGN KEY (activity_id) REFERENCES activities(activity_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

INSERT INTO booked_activities (activity_id, user_id, quantity, booking_fee, booking_date)
VALUES
    (1, 'michelle', 2, 4.5, '2023-02-15'),
    (2, 'robert76', 4, 10.5, '2023-02-28'),
    (3, 'a_kelly', 2, 36, '2023-03-02'),
    (1, 'drake-22', 4, 4.5, '2023-03-03'),
    (8, 'danielle_o''neill', 8, 4.5, '2023-03-03'),
    (3, 'hythen', 3, 36, '2023-03-06');


DROP TABLE IF EXISTS shop_discount;
CREATE TABLE shop_discount
(
    discount_id TEXT PRIMARY KEY,
    percentage_off INTEGER NOT NULL
);

INSERT INTO shop_discount (discount_id, percentage_off)
VALUES
    ('SCOUT_NEW', 25),
    ('SPRING_23', 10),
    ('1MSC0UTER', 15);


DROP TABLE IF EXISTS orders;
CREATE TABLE orders
(
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    discount TEXT NOT NULL,
    shipping_cost INTEGER NOT NULL,
    total_price REAL NOT NULL,
    shipment_status TEXT NOT NULL,
    shipment_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

INSERT INTO orders (user_id, order_date, discount, shipping_cost, total_price, shipment_status, shipment_date)
VALUES
    ('patrick_88', '2023-02-07', 25, 3.99, 32.46, 'Shipped', '2023-02-13');

INSERT INTO orders (user_id, order_date, discount, shipping_cost, total_price, shipment_status)
VALUES
    ('hythen', '2023-03-11', 10, 0, 129.56, 'Pending shipment'),
    ('rachel_craig', '2023-03-13', 0, 3.99, 33.96, 'Pending shipment');

DROP TABLE IF EXISTS order_details;
CREATE TABLE order_details
(
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_quantity INTEGER NOT NULL,
    product_price_sum REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES shop(product_id)
);

INSERT INTO order_details (order_id, product_id, product_quantity, product_price_sum)
VALUES
    (1, 1, 2, 19.98),
    (1, 3, 1, 17.99),
    (2, 9, 4, 143.96),
    (3, 1, 1, 9.99),
    (3, 4, 2, 19.98);

DROP TABLE IF EXISTS product_reviews;
CREATE TABLE product_reviews
(
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    date DATE NOT NULL,
    review_title TEXT NOT NULL,
    review TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES shop(product_id)
);

INSERT INTO product_reviews(user_id, product_id, rating, date, review_title, review)
VALUES
    ('patrick_88', 1, 5, '2023-02-12', 'Nice product', 'This was a small gift for my wife who was a scout when she was younger and she absolutely loved it. Fast delivery too!'),
    ('patrick_88', 3, 4, '2023-02-12', 'All good', 'Happy with my purchase'),
    ('leafy_willow', 3, 5, '2022-01-16', 'Amazing quality', 'Product arrived in perfect condition. It''s nice to buy from a local shop instead of a big retailer'),
    ('hythen', 5, 5, '2023-02-28', '100% recommended shop', 'What an unreal experience! They don''t have a payment system set-up but they still send your orders! Now I''ll have to find what to do with so many mugs.'),
    ('christine_O''connel', 7, 1, '2022-11-24', 'What kind of generation are we raising', 'I bought this pen for my 7 year old boy in the hope of him stopping playing with his tablet all day. It seems like kids don''t know what a pen is anymore, before I could realize he was doing everything with it but writing. Now the iPad has scratches all over it''s screen!! And the pen... it couldn''t be that good when it exploded in an ink mess staining what was a beautiful sofa. Overall, this little thing has been way too expensive.'),
    ('william-2', 5, 7, '2023-03-01', 'All good', 'Very happy with everything, thanks!'),
    ('patrick_88', 7, 4, '2023-01-08', 'I''m happy with my pen', 'So much that I could say about Christine review. I''ll just say that it is just a pen... nothing to do with what your children do with it.');


DROP TABLE IF EXISTS contact;
CREATE TABLE contact
(
    contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    subject TEXT NOT NULL,
    preference TEXT NOT NULL,
    message TEXT NOT NULL
);

INSERT INTO contact (date, name, email, phone, subject, preference, message)
VALUES
    ('2022-12-14', 'Isabella Murphy', 'isabella123@gmail.com', '+353895384922', 'Joining us', 'Phone call', 'Hello I am messaging regarding my interest for my both boys of 6 and 9 to join the scout group. I would be interested to know a bit more about how much time a week would the scouts take from them. In terms of money how much is it (monthly, yearly...)?? Thank! I''ll wait for your response!'),
    ('2023-01-16', 'Frank O''Sulivan', 'frank_78@gmail.com', '+353830124869', 'Shop', 'Unspecified', 'Hi, my name is Frank and I was thinking of making a big order for a group. I was wondering if you make any special discounts in this type of situations. Thanks, Frank');


DROP TABLE IF EXISTS events;
CREATE TABLE events
(
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    time TIME NOT NULL,
    name TEXT NOT NULL
);


INSERT INTO events (date, time, name)
VALUES
    ('2023-03-25', '08:30:00', 'Finding and building refugee in forest'),
    ('2023-04-16', '10:00:00', 'Kayak in Lee River'),
    ('2023-04-08', '09:00:00', 'Kayak at open see'),
    ('2023-04-15', '08:30:00', 'Weekend hike'),
    ('2023-04-22', '09:00:00', 'Basic First Aid Practice'),
    ('2023-04-23', '09:00:00', 'Camping at Brampton Field'),
    ('2023-05-13', '08:30:00', 'Hike to the Galtees'),
    ('2023-05-14', '09:00:00', 'Kayak at open see'),
    ('2023-05-06', '09:00:00', 'Outdoors camp and cooking'),
    ('2023-05-27', '08:00:00', 'Hike to Carauntoohil'),
    ('2023-06-17', '09:00:00', 'End of Season ''Come&Join'' hike'),
    ('2022-12-10', '08:30:00', 'Hike + Secret Santa Resolution');


DROP TABLE IF EXISTS event_details;
CREATE TABLE event_details
(
    details_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    scout_role_id INTEGER NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(event_id),
    FOREIGN KEY (scout_role_id) REFERENCES scout_roles(scout_role_id)
);

INSERT INTO event_details (event_id, scout_role_id)
VALUES
    (1, 0),
    (1, 1),
    (2, 3),
    (3, 3),
    (4, 2),
    (4, 1),
    (5, 1),
    (6, 1),
    (6, 2),
    (6, 3),
    (7, 2),
    (8, 3),
    (9, 1),
    (9, 2),
    (10, 2),
    (11, 0),
    (11, 1),
    (11, 2),
    (11, 3),
    (11, 4),
    (12, 0),
    (12, 1),
    (12, 2),
    (12, 3),
    (12, 4);