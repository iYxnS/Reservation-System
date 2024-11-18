CREATE DATABASE FinalProject;
USE FinalProject;

CREATE TABLE inn_rooms (
    id INT IDENTITY(1,1) PRIMARY KEY,
    room_type VARCHAR(1),
    room_price DECIMAL(5, 2),
    availability SMALLINT
);

CREATE TABLE inn_customer (
    id INT IDENTITY(1,1) PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(30),
    phone_number BIGINT
);


CREATE TABLE inn_reservation (
    id INT IDENTITY(1,1) PRIMARY KEY,
    room_type INT,
    customer_id INT,
    accommodation_days SMALLINT,
    cost DECIMAL(5, 2),
    checkout TINYINT, 
    FOREIGN KEY (room_type) REFERENCES inn_rooms(id),
    FOREIGN KEY (customer_id) REFERENCES inn_customer(id)
);

SELECT * FROM inn_rooms

INSERT INTO inn_rooms (room_type, room_price, availability)
VALUES 
('S', 100.00, 10),
('P', 150.00, 5),
('O', 200.00, 5),
('E', 50.00, 9);
