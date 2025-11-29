-- Drop tables if they already exist, so we can re-run this file
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS stores;

-- Table for the physical stores
CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255)
);

-- Table for all the products we might sell
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255)
);

-- This is the "linking" table. It connects stores and products.
CREATE TABLE inventory (
    inventory_id SERIAL PRIMARY KEY,
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    price DECIMAL(10, 2) NOT NULL,

    -- These are the "links"
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),

    -- Ensure a store can't list the same product twice
    UNIQUE(store_id, product_id)
);