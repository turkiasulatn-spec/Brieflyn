-- USERS
CREATE TABLE users (
    id          INTEGER PRIMARY KEY,
    username    TEXT    NOT NULL,
    email       TEXT    NOT NULL,
    language    TEXT    NOT NULL DEFAULT 'en',
    country     TEXT,
    api         TEXT,
    api_provider TEXT   NOT NULL CHECK (api_provider IN ('openai','google','groq')) DEFAULT 'groq',
    role        TEXT    NOT NULL DEFAULT 'user',
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- (Categories)
CREATE TABLE categories (
    id          INTEGER PRIMARY KEY,
    title       TEXT,
    description TEXT, -- Category Description
    status      TEXT    NOT NULL CHECK (status IN ('active','inactive')) DEFAULT 'active',
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
--  (User‑Categories)
CREATE TABLE user_categories (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_categories_user
        FOREIGN KEY (user_id) REFERENCES users (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_user_categories_category
        FOREIGN KEY (category_id) REFERENCES categories (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);