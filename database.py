import sqlite3

def get_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            authors TEXT,
            url TEXT,
            category TEXT,
            tags TEXT,
            notes TEXT,
            local_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    try:
        c.execute("ALTER TABLE papers ADD COLUMN published_date TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def add_paper(db_path, title, authors, url, category, tags, notes, local_path, published_date=None):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT INTO papers (title, authors, url, category, tags, notes, local_path, published_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, authors, url, category, tags, notes, local_path, published_date))
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_papers(db_path):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM papers ORDER BY created_at DESC')
    papers = [dict(row) for row in c.fetchall()]
    conn.close()
    return papers

def update_paper(db_path, paper_id, category=None, tags=None, notes=None, title=None, authors=None):
    conn = get_db(db_path)
    c = conn.cursor()
    
    updates = []
    params = []
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if authors is not None:
        updates.append("authors = ?")
        params.append(authors)
    if category is not None:
        updates.append("category = ?")
        params.append(category)
    if tags is not None:
        updates.append("tags = ?")
        params.append(tags)
    if notes is not None:
        updates.append("notes = ?")
        params.append(notes)
        
    if not updates:
        return
        
    params.append(paper_id)
    query = f"UPDATE papers SET {', '.join(updates)} WHERE id = ?"
    c.execute(query, params)
    conn.commit()
    conn.close()

def search_papers(db_path, query):
    conn = get_db(db_path)
    c = conn.cursor()
    search_term = f"%{query}%"
    c.execute('''
        SELECT * FROM papers 
        WHERE title LIKE ? OR authors LIKE ? OR tags LIKE ? OR notes LIKE ? OR category LIKE ?
        ORDER BY created_at DESC
    ''', (search_term, search_term, search_term, search_term, search_term))
    papers = [dict(row) for row in c.fetchall()]
    conn.close()
    return papers

def get_paper(db_path, paper_id):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM papers WHERE id = ?', (paper_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_paper(db_path, paper_id):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute('DELETE FROM papers WHERE id = ?', (paper_id,))
    conn.commit()
    conn.close()

