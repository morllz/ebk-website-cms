import sqlite3

import click
from flask import current_app, g

from git import Repo

import os

import yaml


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    
def populate_db():
    db = get_db()
    if not os.path.exists(current_app.config['EBK_WEBSITE_REPO']):
        # Clone the repository if it does not exist
        Repo.clone_from(current_app.config['EBK_WEBSITE_REPO_URL'], 
                        current_app.config['EBK_WEBSITE_REPO'], 
                        depth=1)
    Repo(current_app.config['EBK_WEBSITE_REPO']).remotes.origin.pull()

    directory = os.path.join(current_app.config['EBK_WEBSITE_REPO'], 'content', 'post')

    for filename in os.listdir(directory):
        if filename.endswith('.markdown'):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                content = file.read()
                # Split the content into metadata and body
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        metadata_raw = parts[1]
                        body = parts[2].strip()
                        metadata = yaml.safe_load(metadata_raw)
                    else:
                        metadata = {}
                        body = content
                else:
                    metadata = {}
                    body = content

                # Check if post already exists (by url)
                url = metadata.get('url')
                existing_post = db.execute(
                    "SELECT id FROM posts WHERE url = ?", (url,)
                ).fetchone()
                if existing_post:
                    continue  # Skip if post already exists
                
                print(metadata)
                cursor = db.execute(
                    "INSERT INTO posts (author, title, draft, url, created_at, commited, content) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        metadata.get('author', 'EBK'),
                        metadata.get('title', 'Untitled'),
                        metadata.get('draft', 'False'),
                        url,
                        metadata.get('date', '1970-01-01'),
                        1,
                        body
                    )
                )
                post_id = cursor.lastrowid

                # Handle categories
                categories = metadata.get('categories', [])
                if not isinstance(categories, list):
                    categories = [categories] if categories else []
                for category in categories:
                    # Insert category if not exists
                    db.execute(
                        "INSERT OR IGNORE INTO categories (id) VALUES (?)",
                        (category,)
                    )
                    # Link post to category
                    db.execute(
                        "INSERT OR IGNORE INTO post_categories (post_id, category_id) VALUES (?, ?)",
                        (post_id, category)
                    )

                # Handle tags
                tags = metadata.get('tags', [])
                if not isinstance(tags, list):
                    tags = [tags] if tags else []
                for tag in tags:
                    # Insert tag if not exists
                    db.execute(
                        "INSERT OR IGNORE INTO tags (id) VALUES (?)",
                        (tag,)
                    )
                    # Link post to tag
                    db.execute(
                        "INSERT OR IGNORE INTO post_tags (post_id, tag_id) VALUES (?, ?)",
                        (post_id, tag)
                    )

                db.commit()
    

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

@click.command('populate-db')
def populate_db_command():
    """Populate the database with posts from the EBK website repository."""
    populate_db()
    click.echo('Populated the database with posts from the EBK website repository.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(populate_db_command)

