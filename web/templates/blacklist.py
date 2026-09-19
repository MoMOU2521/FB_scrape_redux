# BLACKLIST_TEMPLATE = """<!DOCTYPE html>
# <html>
# <head>
# <meta charset="utf-8">
# <title>Blacklist</title>
# <style>
#   body {
#     font-family: sans-serif;
#     max-width: 900px;
#     margin: 20px auto;
#     padding: 0 15px;
#   }
#   table {
#     width: 100%%;
#     border-collapse: collapse;
#     margin: 20px 0;
#   }
#   th, td {
#     padding: 10px 15px;
#     text-align: left;
#     border-bottom: 1px solid #ddd;
#   }
#   th {
#     background: #f5f5f5;
#     font-weight: bold;
#   }
#   .back-link {
#     display: inline-block;
#     margin: 15px 0;
#     padding: 8px 16px;
#     background: #4CAF50;
#     color: white;
#     text-decoration: none;
#     border-radius: 4px;
#     margin-right: 10px;
#   }
#   .back-link.admin-link {
#     background: #ff9800;
#   }
#   .delete-btn {
#     background: #f44336;
#     color: white;
#     border: none;
#     padding: 4px 12px;
#     border-radius: 4px;
#     cursor: pointer;
#   }
#   .delete-btn:hover {
#     background: #d32f2f;
#   }
#   .empty-msg {
#     color: #666;
#     font-style: italic;
#     padding: 20px 0;
#   }
#   .add-row input[type="text"] {
#     padding: 6px;
#     width: 300px;
#     margin-right: 8px;
#   }
#   .add-row button {
#     padding: 6px 14px;
#     cursor: pointer;
#     background: #f44336;
#     color: white;
#     border: none;
#     border-radius: 4px;
#   }
#   .feedback {
#     font-size: 0.9em;
#     color: #2e7d32;
#     margin-left: 10px;
#   }
#   .feedback-error {
#     color: #d32f2f;
#   }
# </style>
# </head>
# <body>
# <h1>🚫 Blacklisted Authors</h1>
# <a href="/" class="back-link">← Back to posts</a>
# <a href="/stats" class="back-link">📊 Stats</a>
# <a href="/filters" class="back-link admin-link">🔍 Filter Phrases</a>
# <a href="/authors" class="back-link admin-link">👤 Authors</a>

# <div style="margin:10px 0;">
#   Sort by:
#   <a href="/blacklist?sort=count">Count</a> |
#   <a href="/blacklist?sort=alpha">Alphabetical</a>
# </div>

# <div class="add-row" style="margin: 20px 0;">
#   <input type="text" id="new-blacklist-author" placeholder="Paste author name here" />
#   <button onclick="addBlacklistDirect()">⛔ Add to blacklist</button>
#   <span id="add-blacklist-feedback" class="feedback"></span>
# </div>

# <table>
#   <thead>
#     <tr>
#       <th>Author</th>
#       <th>Count</th>
#       <th>Action</th>
#     </tr>
#   </thead>
#   <tbody>
#     %(rows)s
#   </tbody>
# </table>

# <script>
# async function addBlacklistDirect() {
#   const input = document.getElementById('new-blacklist-author');
#   const author = input.value.trim();
#   const feedback = document.getElementById('add-blacklist-feedback');
#   if (!author) {
#     feedback.textContent = '⚠️ Enter a name first';
#     feedback.className = 'feedback feedback-error';
#     return;
#   }
#   feedback.textContent = 'Adding...';
#   feedback.className = 'feedback';
#   try {
#     const resp = await fetch('/add-blacklist', {
#       method: 'POST',
#       headers: { 'Content-Type': 'application/json' },
#       body: JSON.stringify({ author: author })
#     });
#     const result = await resp.json();
#     if (resp.ok) {
#       feedback.textContent = '✅ Added';
#       input.value = '';
#       window.location.reload();
#     } else {
#       feedback.textContent = '❌ Error: ' + (result.error || 'unknown');
#       feedback.className = 'feedback feedback-error';
#     }
#   } catch (e) {
#     feedback.textContent = '❌ Request failed';
#     feedback.className = 'feedback feedback-error';
#     console.error(e);
#   }
# }

# async function deleteBlacklist(author) {
#   if (!confirm(`Remove "${author}" from blacklist?`)) return;
#   try {
#     const resp = await fetch('/delete-blacklist', {
#       method: 'POST',
#       headers: { 'Content-Type': 'application/json' },
#       body: JSON.stringify({ author: author })
#     });
#     if (resp.ok) {
#       window.location.reload();
#     } else {
#       alert('Failed to delete');
#     }
#   } catch (e) {
#     alert('Request failed');
#     console.error(e);
#   }
# }
# </script>
# </body>
# </html>
# """
