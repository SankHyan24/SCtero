import os
import json
from flask import Flask, request, jsonify, session, redirect, url_for, render_template, send_from_directory
from functools import wraps
from database import init_db, get_papers, get_paper, add_paper, update_paper, delete_paper, search_papers

config_path = 'config.json'
config_data = {}
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config_data = json.load(f)

BASE_DIR = os.environ.get('BASE_DIR') or config_data.get('base_dir', 'data')
DB_PATH = os.path.join(BASE_DIR, 'metadata.db')
PAPERS_DIR = os.path.join(BASE_DIR, 'papers')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or config_data.get('admin_password', 'admin')
SECRET_KEY = os.environ.get('SECRET_KEY') or config_data.get('secret_key', os.urandom(24).hex())
PORT = int(os.environ.get('PORT') or config_data.get('port', 5001))

app = Flask(__name__)
app.secret_key = SECRET_KEY

os.makedirs(PAPERS_DIR, exist_ok=True)
init_db(DB_PATH)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized'}), 401
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid password")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/api/papers', methods=['GET'])
@login_required
def api_get_papers():
    query = request.args.get('q', '')
    if query:
        papers = search_papers(DB_PATH, query)
    else:
        papers = get_papers(DB_PATH)
    return jsonify(papers)

@app.route('/api/papers', methods=['POST'])
@login_required
def api_add_paper():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400
        
    from downloader import download_paper
    success, result = download_paper(url, PAPERS_DIR)
    if not success:
        return jsonify({'error': result}), 400
    
    title = data.get('title') or result.get('title', 'Unknown Title')
    authors = data.get('authors') or result.get('authors', 'Unknown Authors')
    
    p_id = add_paper(DB_PATH, title, authors, url,
                     data.get('category', 'Uncategorized'), 
                     data.get('tags', ''), 
                     data.get('notes', ''), 
                     result['filename'],
                     result.get('published_date', ''))
    return jsonify({'id': p_id, 'message': 'Paper added successfully'})

@app.route('/api/papers/<int:paper_id>', methods=['PUT'])
@login_required
def api_update_paper(paper_id):
    data = request.json
    update_paper(DB_PATH, paper_id, 
                 title=data.get('title'),
                 authors=data.get('authors'),
                 category=data.get('category'), 
                 tags=data.get('tags'), 
                 notes=data.get('notes'))
    return jsonify({'message': 'Paper updated'})

@app.route('/api/papers/<int:paper_id>', methods=['DELETE'])
@login_required
def api_delete_paper(paper_id):
    paper = get_paper(DB_PATH, paper_id)
    if not paper:
        return jsonify({'error': 'Not found'}), 404
        
    file_path = os.path.join(PAPERS_DIR, paper['local_path'])
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass
            
    delete_paper(DB_PATH, paper_id)
    return jsonify({'message': 'Paper deleted'})

@app.route('/papers/<path:filename>')
@login_required
def serve_paper(filename):
    return send_from_directory(PAPERS_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
