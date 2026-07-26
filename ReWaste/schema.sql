-- TABLE 1: users
-- Stores every registered business on the platform
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    business_name VARCHAR(120) NOT NULL,
    email         VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    sector        VARCHAR(80),
    city          VARCHAR(80),
    created_at    TIMESTAMP DEFAULT NOW()
);


-- TABLE 2: listings
-- Stores every waste material posted for exchange
CREATE TABLE listings (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title         VARCHAR(120) NOT NULL,
    material_type VARCHAR(80) NOT NULL,
    quantity      FLOAT NOT NULL,
    unit          VARCHAR(20) NOT NULL,
    price         FLOAT NOT NULL,
    description   TEXT,
    photo         VARCHAR(200),
    city          VARCHAR(80),
    status        VARCHAR(20) DEFAULT 'available',
    created_at    TIMESTAMP DEFAULT NOW()
);


-- TABLE 3: requests
-- Stores every buy request a buyer sends on a listing
CREATE TABLE requests (
    id         SERIAL PRIMARY KEY,
    listing_id INTEGER NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    buyer_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    seller_id  INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message    TEXT,
    status     VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);


-- TABLE 4: scores
-- Stores the sustainability score for each business
-- One row per business, updated whenever activity changes
CREATE TABLE scores (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score_value  FLOAT DEFAULT 0.0,
    badge_level  VARCHAR(20) DEFAULT 'Bronze',
    last_updated TIMESTAMP DEFAULT NOW()
);
