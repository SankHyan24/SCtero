import os
import requests
import re
import uuid

def handle_arxiv(url):
    match = re.search(r'arxiv\.org/(?:abs|pdf)/(\d+\.\d+(?:v\d+)?)', url)
    if match:
        arxiv_id = match.group(1)
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        title = f"arXiv Paper {arxiv_id}"
        authors = "Unknown Authors"
        published_date = ""
        
        # HTML meta scraping approach
        try:
            html_url = f"https://arxiv.org/abs/{arxiv_id}"
            r_html = requests.get(html_url, timeout=10)
            if r_html.status_code == 200:
                html_text = r_html.text
                
                t_match = re.search(r'<meta name="citation_title"\s+content="([^"]+)"', html_text, re.IGNORECASE)
                if not t_match:
                    t_match = re.search(r'content="([^"]+)"\s+name="citation_title"', html_text, re.IGNORECASE)
                if t_match:
                    title = t_match.group(1).replace('\n', ' ').strip()
                
                a_matches = re.findall(r'<meta name="citation_author"\s+content="([^"]+)"', html_text, re.IGNORECASE)
                if not a_matches:
                    a_matches = re.findall(r'content="([^"]+)"\s+name="citation_author"', html_text, re.IGNORECASE)
                if a_matches:
                    authors = ", ".join(a_matches)
                    
                d_match = re.search(r'<meta name="citation_date"\s+content="([^"]+)"', html_text, re.IGNORECASE)
                if not d_match:
                    d_match = re.search(r'content="([^"]+)"\s+name="citation_date"', html_text, re.IGNORECASE)
                if d_match:
                    published_date = d_match.group(1).replace('\n', ' ').strip()
                    
                if title != f"arXiv Paper {arxiv_id}":
                    return pdf_url, title, authors, published_date
        except Exception:
            pass
            
        # Fallback to API if HTML didn't yield
        try:
            base_id = arxiv_id.split('v')[0] # Remove version for API querying
            api_url = f"http://export.arxiv.org/api/query?id_list={base_id}"
            r = requests.get(api_url, timeout=5)
            if r.status_code == 200:
                entry_match = re.search(r'<entry>.*?<title>(.+?)</title>', r.text, re.DOTALL)
                if entry_match:
                    title = entry_match.group(1).replace('\n', ' ').strip()
                author_matches = re.findall(r'<author>\s*<name>(.+?)</name>', r.text)
                if author_matches:
                    authors = ", ".join(author_matches)
                    
                pub_match = re.search(r'<published>(.+?)</published>', r.text)
                if pub_match:
                    published_date = pub_match.group(1).split('T')[0]
        except Exception:
            pass
            
        return pdf_url, title, authors, published_date
    return None, None, None, None

def download_paper(url, save_dir):
    try:
        title = "Unknown Paper"
        authors = "Unknown Authors"
        published_date = ""
        pdf_url = url
        
        if 'arxiv.org' in url:
            arxiv_pdf, arxiv_t, arxiv_a, arxiv_d = handle_arxiv(url)
            if arxiv_pdf:
                pdf_url = arxiv_pdf
                title = arxiv_t
                authors = arxiv_a
                published_date = arxiv_d
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(pdf_url, headers=headers, stream=True, timeout=15)
        r.raise_for_status()
        
        content_type = r.headers.get('content-type', '')
        ext = '.pdf' if 'pdf' in content_type.lower() else ''
        
        if not ext and 'arxiv.org' in pdf_url:
            ext = '.pdf'
            
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                
        if title == "Unknown Paper":
            title = url.split('/')[-1] or title

        return True, {
            'filename': filename,
            'title': title,
            'authors': authors,
            'published_date': published_date
        }
    except Exception as e:
        return False, str(e)
