DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS post_tags;
DROP TABLE IF EXISTS post_categories;

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT NOT NULL,
    title TEXT NOT NULL,
    draft BOOLEAN NOT NULL DEFAULT 0,
    url TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    commited BOOLEAN NOT NULL DEFAULT 0,
    content TEXT NOT NULL
);

CREATE TABLE tags (
    id TEXT PRIMARY KEY
);

CREATE TABLE categories (
    id TEXT PRIMARY KEY
);

CREATE TABLE post_tags (
    post_id INTEGER NOT NULL,
    tag_id TEXT NOT NULL,
    FOREIGN KEY (post_id) REFERENCES post (id),
    FOREIGN KEY (tag_id) REFERENCES tag (id),
    PRIMARY KEY (post_id, tag_id)
);

CREATE TABLE post_categories (
    post_id INTEGER NOT NULL,
    category_id TEXT NOT NULL,
    FOREIGN KEY (post_id) REFERENCES post (id),
    FOREIGN KEY (category_id) REFERENCES category (id),
    PRIMARY KEY (post_id, category_id)
);