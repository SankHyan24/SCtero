document.addEventListener('DOMContentLoaded', () => {
    // Only run scripts on index
    const papersTableBody = document.getElementById('papersBody');
    if (!papersTableBody) return;

    const addModal = document.getElementById('addModal');
    const addPaperBtn = document.getElementById('addPaperBtn');
    const closeAddModal = document.getElementById('closeAddModal');
    const cancelAdd = document.getElementById('cancelAdd');
    const submitAdd = document.getElementById('submitAdd');
    const searchInput = document.getElementById('searchInput');

    const loadPapers = async (query = '') => {
        try {
            const res = await fetch(`/api/papers?q=${encodeURIComponent(query)}`);
            const papers = await res.json();
            renderPapers(papers);
        } catch (e) {
            console.error('Failed to load papers', e);
        }
    };

    const renderPapers = (papers) => {
        papersTableBody.innerHTML = '';
        if (papers.length === 0) {
            papersTableBody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--text-muted);padding:32px;">No papers found.</td></tr>`;
            return;
        }

        papers.forEach(p => {
            const tr = document.createElement('tr');
            const dateStr = new Date(p.created_at).toLocaleDateString();
            const tagsHtml = p.tags ? p.tags.split(',').map(t => `<span class="tag">${t.trim()}</span>`).join('') : '-';
            
            const escap = (str) => (str || '').replace(/'/g, "\\'");
            tr.innerHTML = `
                <td><strong style="color:var(--text-main);font-size:0.9rem;">${p.title}</strong><div style="color:var(--text-muted);font-size:0.8rem;margin-top:4px;">${p.notes || ''}</div></td>
                <td><span style="color:var(--text-muted);font-size:0.85rem;">${p.authors}</span>
                ${p.published_date ? `<br><span style="font-size:0.75rem; color:#4f46e5; margin-top:4px; display:inline-block;">🗓 ArXiv: ${p.published_date}</span>` : ''}
                </td>
                <td>${p.category || '-'}</td>
                <td>${tagsHtml}</td>
                <td style="color:var(--text-muted);font-size:0.85rem;">${dateStr}</td>
                <td>
                    <div style="display: flex; gap: 8px;">
                        <a href="/papers/${p.local_path}" target="_blank" class="pdf-btn">PDF</a>
                        <button class="btn secondary-btn" style="padding: 4px 8px; font-size: 0.75rem;" onclick="openEditModal(${p.id}, '${escap(p.title)}', '${escap(p.authors)}', '${escap(p.category)}', '${escap(p.tags)}', '${escap(p.notes)}')">Edit</button>
                        <button class="btn primary-btn" style="padding: 4px 8px; font-size: 0.75rem; background: var(--danger-color);" onclick="deletePaper(${p.id})">Del</button>
                    </div>
                </td>
            `;
            papersTableBody.appendChild(tr);
        });
    };

    // Modal Interaction
    const openModal = () => addModal.classList.add('visible');
    const closeModal = () => {
        addModal.classList.remove('visible');
        document.getElementById('paperUrl').value = '';
        document.getElementById('paperCategory').value = '';
        document.getElementById('paperTags').value = '';
    };

    addPaperBtn.addEventListener('click', openModal);
    closeAddModal.addEventListener('click', closeModal);
    cancelAdd.addEventListener('click', closeModal);
    
    // Upload logic
    submitAdd.addEventListener('click', async () => {
        const url = document.getElementById('paperUrl').value;
        const category = document.getElementById('paperCategory').value;
        const tags = document.getElementById('paperTags').value;
        
        if (!url) {
            alert('URL is required');
            return;
        }

        document.getElementById('submitText').style.display = 'none';
        document.getElementById('submitSpinner').style.display = 'block';
        submitAdd.disabled = true;

        try {
            const res = await fetch('/api/papers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url, category, tags })
            });
            const data = await res.json();
            
            if (res.ok) {
                closeModal();
                loadPapers();
            } else {
                alert('Error: ' + data.error);
            }
        } catch (e) {
            alert('Failed to connect to server');
        } finally {
            document.getElementById('submitText').style.display = 'block';
            document.getElementById('submitSpinner').style.display = 'none';
            submitAdd.disabled = false;
        }
    });

    // Edit Modal Logic
    const editModal = document.getElementById('editModal');
    if (editModal) {
        document.getElementById('closeEditModal').addEventListener('click', () => editModal.classList.remove('visible'));
        document.getElementById('cancelEdit').addEventListener('click', () => editModal.classList.remove('visible'));

        document.getElementById('submitEdit').addEventListener('click', async () => {
            const id = document.getElementById('editPaperId').value;
            const title = document.getElementById('editTitle').value;
            const authors = document.getElementById('editAuthors').value;
            const category = document.getElementById('editCategory').value;
            const tags = document.getElementById('editTags').value;
            const notes = document.getElementById('editNotes').value;
            
            try {
                const res = await fetch(`/api/papers/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, authors, category, tags, notes })
                });
                if (res.ok) {
                    editModal.classList.remove('visible');
                    loadPapers();
                } else {
                    alert('Error updating paper');
                }
            } catch (e) {
                alert('Failed to connect to server');
            }
        });
    }

    window.openEditModal = (id, title, authors, cat, tags, notes) => {
        document.getElementById('editPaperId').value = id;
        document.getElementById('editTitle').value = title || '';
        document.getElementById('editAuthors').value = authors || '';
        document.getElementById('editCategory').value = cat || '';
        document.getElementById('editTags').value = tags || '';
        document.getElementById('editNotes').value = notes || '';
        document.getElementById('editModal').classList.add('visible');
    };

    window.deletePaper = async (id) => {
        if (!confirm('Are you sure you want to delete this paper and its PDF?')) return;
        try {
            const res = await fetch(`/api/papers/${id}`, { method: 'DELETE' });
            if (res.ok) {
                loadPapers();
            } else {
                alert('Error deleting paper');
            }
        } catch (e) {
            alert('Failed to connect to server');
        }
    };

    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            loadPapers(e.target.value);
        }, 300);
    });

    loadPapers();
});
