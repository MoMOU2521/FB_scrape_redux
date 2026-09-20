# # templates/post.py
# PAGE_TEMPLATE = """<!DOCTYPE html>
# <html>
# <head>
# <meta charset="utf-8">
# <title>Posts Viewer</title>

# <style>
#   body {
#     font-family: sans-serif;
#     max-width: 700px;
#     margin: 20px auto;
#     padding: 0 15px;
#   }

#   .nav {
#     display: flex;
#     gap: 10px;
#     align-items: center;
#     margin: 15px 0;
#   }

#   .nav button {
#     padding: 8px 16px;
#     cursor: pointer;
#   }

#   img {
#     max-width: 100%%;
#     margin: 8px 0;
#     display: block;
#   }

#   .post-text {
#     white-space: pre-wrap;
#     background: #f5f5f5;
#     padding: 12px;
#     border-radius: 4px;
#   }

#   .meta {
#     color: #555;
#     margin-bottom: 10px;
#   }

#   .proc {
#     margin: 10px 0;
#   }

#   .author-copy {
#     user-select: all;
#     font-weight: bold;
#     font-size: 1.1em;
#   }

#   .admin-actions {
#     margin: 20px 0;
#     padding: 15px;
#     border: 1px solid #ccc;
#     border-radius: 6px;
#     background: #fafafa;
#   }

#   .admin-actions input[type="text"] {
#     width: 70%%;
#     padding: 6px;
#     margin-right: 8px;
#   }

#   .admin-actions button {
#     padding: 6px 14px;
#     cursor: pointer;
#     background: #2196F3;
#     color: white;
#     border: none;
#     border-radius: 4px;
#   }

#   .admin-actions .btn-blacklist {
#     background: #f44336;
#   }

#   .admin-actions .btn-dbentry {
#     background: #4CAF50;
#   }

#   .admin-actions .btn-filter {
#     background: #ff9800;
#   }

#   .admin-actions .action-row {
#     margin: 8px 0;
#   }

#   .admin-actions .feedback {
#     font-size: 0.9em;
#     color: #2e7d32;
#     margin-left: 10px;
#   }

#   .admin-actions .feedback-error {
#     color: #d32f2f;
#   }

#   .nav-stats {
#     margin: 15px 0;
#   }

#   .nav-stats a {
#     display: inline-block;
#     padding: 8px 16px;
#     background: #4CAF50;
#     color: white;
#     text-decoration: none;
#     border-radius: 4px;
#     margin-right: 10px;
#   }

#   .nav-stats a.admin-link {
#     background: #ff9800;
#   }

#   .nav-stats a.back-link {
#     background: #666;
#   }

#   .author-action-row {
#     margin: 10px 0;
#   }

#   .author-action-row a {
#     display: inline-block;
#     padding: 8px 16px;
#     background: #9C27B0;
#     color: white;
#     text-decoration: none;
#     border-radius: 4px;
#     font-weight: bold;
#   }

#   .author-action-row a:hover {
#     background: #7B1FA2;
#   }

#   .reasoning-panel {
#     margin: 10px 0;
#     border: 1px solid #ddd;
#     border-radius: 4px;
#     padding: 8px 12px;
#     background: #fffbe6;
#   }

#   .reasoning-panel summary {
#     cursor: pointer;
#     font-weight: bold;
#     color: #555;
#   }

#   .reasoning-text {
#     margin-top: 8px;
#     font-size: 0.9em;
#     color: #444;
#     max-height: 400px;
#     overflow-y: auto;
#   }

#   .btn-delete {
#   background: #d32f2f;
#   color: white;
#   border: none;
#   padding: 8px 16px;
#   border-radius: 4px;
#   cursor: pointer;
# }
#   .btn-delete:hover {
#   background: #b71c1c;
# }
# </style>
# </head>

# <body>

# <h2>%(page_title)s (%(current)d / %(total)d)</h2>
# <div class="action-row" style="margin-top: 10px;">
#   <button class="btn-delete" onclick="deletePost(%(row_id)d)" style="background: #d32f2f; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
#     🗑️ Delete this post
#   </button>
#   <span id="delete-feedback" class="feedback"></span>
# </div>

# <div class="action-row" style="margin-top: 10px;">
#   %(dismiss_button)s
# </div>

# <div class="nav-stats">
#   %(back_button)s
#   <a href="/">📋 Unprocessed</a>
#   <a href="/processed">✅ Processed</a>
#   <a href="/post-lookup">🔎 Post Lookup</a>
#   <a href="/stats">📊 Group Statistics</a>
#   <a href="/blacklist" class="admin-link">🚫 Blacklist</a>
#   <a href="/review" class="admin-link">🔎 Review Queue</a>
#   <a href="/review-building" class="admin-link">🏗️ Building Review</a>
#   <a href="/authors" class="admin-link">👤 Authors</a>
#   <a href="/filters" class="admin-link">🔍 Filter Phrases</a>
#   </div>

# <div class="proc">
#   <label>
#     <input
#       type="checkbox"
#       id="processed"
#       %(checked)s
#       onchange="toggleProcessed(%(row_id)d, this.checked)"
#     >
#     Processed
#   </label>
#   <label style="margin-left: 20px;">
#     <input
#       type="checkbox"
#       id="selected"
#       %(selected_checked)s
#       onchange="toggleSelected(%(row_id)d, this.checked)"
#     >
#     Selected (valuable)
#   </label>
#   <span id="selected-feedback" class="feedback" style="margin-left: 10px;"></span>
# </div>


# <div class="nav">
#   %(prev_button)s
#   %(next_button)s
# </div>

# <div class="meta">
#   <span class="author-copy">%(author)s</span><br>
#   Group: %(group_name)s<br>
#   Post ID: %(post_id)s<br>
#   Row ID: %(row_id)d<br>
#   Unprocessed by this author: %(unprocessed_count)d
# </div>

# %(author_button)s

# <div class="meta">
#   Original:
#   <a href="%(url)s" target="_blank">%(url)s</a>
# </div>

# <div class="post-text">%(text)s</div>

# <div class="meta">AI Result (Gate 1):</div>
# <div class="post-text">%(ai_result)s</div>

# <div class="action-row">
#     <button class="btn-dbentry" onclick="enterIntoDb(%(row_id)d)">
#       📥 Enter into DB
#     </button>
#     <span id="dbentry-feedback" class="feedback"></span>
#   </div>

# <details class="reasoning-panel">
#   <summary>🧠 Gate 1 reasoning (prompt v%(gate1_prompt_version)s)</summary>
#   <div class="post-text reasoning-text">%(gate1_reasoning)s</div>
# </details>

# <div class="meta">AI Result (Extraction):</div>
# <div class="post-text">%(extraction_result)s</div>

# <details class="reasoning-panel">
#   <summary>🧠 Extraction reasoning (prompt v%(extraction_prompt_version)s)</summary>
#   <div class="post-text reasoning-text">%(extraction_reasoning)s</div>
# </details>

# %(images)s

# <div class="admin-actions">
#   <h4>Add Building Alias</h4>
#   <select id="building-select">
#     <option value="">-- select building --</option>
#     %(building_options)s
#   </select>
#   <input type="text" id="alias-input" placeholder="Raw building name from post" value="%(building_name)s" />
#   <button onclick="addAlias(%(row_id)d)">➕ Add Alias</button>
#   <span id="alias-feedback" class="feedback"></span>
# </div>

# <!-- ====== Admin Actions ====== -->
# <div class="admin-actions">
#   <h4>Quick Admin</h4>

#   <div class="action-row">
#     <button class="btn-blacklist" onclick="blacklistAuthor('%(author)s')">
#       ⛔ Blacklist this author (and skip all their posts)
#     </button>
#     <span id="blacklist-feedback" class="feedback"></span>
#   </div>

#   <div class="action-row">
#     <input type="text" id="new-filter-phrase" placeholder="Enter filter phrase..." />
#     <button class="btn-filter" onclick="addFilterPhrase()">➕ Add filter phrase</button>
#     <span id="filter-feedback" class="feedback"></span>
#   </div>
# </div>

# <script>
# async function enterIntoDb(rowId) {
#   const feedback = document.getElementById('dbentry-feedback');
#   feedback.textContent = 'Processing...';
#   feedback.className = 'feedback';
#   try {
#     const resp = await fetch('%(db_entry_endpoint)s', {
#       method: 'POST',
#       headers: { 'Content-Type': 'application/json' },
#       body: JSON.stringify({ id: rowId })
#     });
#     const result = await resp.json();
#     if (!resp.ok) {
#       feedback.textContent = '❌ Error: ' + (result.error || 'unknown');
#       feedback.className = 'feedback feedback-error';
#       return;
#     }
#     if (result.discarded === true) {
#       feedback.textContent = '⏭️ Skipped: exact duplicate exists.';
#       feedback.className = 'feedback';
#       setTimeout(() => {
#         window.location.href = window.location.pathname.startsWith('/review-building/')
#           ? '/review-building'
#           : '/';
#       }, 1000);
#       return;
#     }
#     if (result.sent_to_review === true) {
#       feedback.textContent = '⏳ Sent to review (candidate ID: ' + result.candidate_property_id + ')';
#       feedback.className = 'feedback';
#       setTimeout(() => {
#         window.location.href = window.location.pathname.startsWith('/review-building/')
#           ? '/review-building'
#           : '/';
#       }, 1000);
#       return;
#     }
#     if (result.property_id !== undefined && result.property_id !== null) {
#       feedback.textContent = '✅ Entered! Property ID: ' + result.property_id;
#       feedback.className = 'feedback';
#       setTimeout(() => {
#         window.location.href = window.location.pathname.startsWith('/review-building/')
#           ? '/review-building'
#           : '/';
#       }, 1000);
#       return;
#     }
#     feedback.textContent = '⚠️ Unknown response: ' + JSON.stringify(result);
#     feedback.className = 'feedback feedback-error';
#   } catch (e) {
#     feedback.textContent = '❌ Request failed';
#     feedback.className = 'feedback feedback-error';
#     console.error(e);
#   }
# }

# async function dismissBuilding(postId) {
#   if (!confirm('Remove this post from building review?')) return;
#   const feedback = document.getElementById('dismiss-feedback');
#   feedback.textContent = 'Dismissing...';
#   try {
#     const resp = await fetch('/dismiss-building', {
#       method: 'POST',
#       headers: { 'Content-Type': 'application/json' },
#       body: JSON.stringify({ post_id: postId })
#     });
#     if (resp.ok) {
#       feedback.textContent = '✅ Dismissed!';
#       window.location.href = '/review-building';
#     } else {
#       feedback.textContent = '❌ Error';
#     }
#   } catch (e) {
#     feedback.textContent = '❌ Request failed';
#   }
# }

# async function blacklistAuthor(author) {
#   const feedback = document.getElementById('blacklist-feedback');
#   feedback.textContent = 'Adding...';
#   try {
#     const resp = await fetch('/add-blacklist', {
#       method: 'POST',
#       headers: { 'Content-Type': 'application/json' },
#       body: JSON.stringify({ author: author })
#     });
#     const result = await resp.json();
#     if (resp.ok) {
#       feedback.textContent = '✅ Blacklisted! Skipping all their posts...';
#       window.location.href = "/";
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

# async function addFilterPhrase() {
#   const input = document.getElementById('new-filter-phrase');
#   const phrase = input.value.trim();
#   const feedback = document.getElementById('filter-feedback');
#   if (!phrase) {
#     feedback.textContent = '⚠️ Enter a phrase first';
#     feedback.className = 'feedback feedback-error';
#     return;
#   }
#   feedback.textContent = 'Adding...';
#   feedback.className = 'feedback';
#   try {
#     const resp = await fetch('/add-filter', {
#       method: 'POST',
#       headers: { 'Content-Type': 'application/json' },
#       body: JSON.stringify({ phrase: phrase })
#     });
#     const result = await resp.json();
#     if (resp.ok) {
#       if (result.already_exists) {
#         feedback.textContent = '⚠️ Phrase already exists in filter list';
#         feedback.className = 'feedback feedback-error';
#       } else {
#         feedback.textContent = '✅ Filter phrase added!';
#         feedback.className = 'feedback';
#         input.value = '';
#       }
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

# async function toggleProcessed(rowId, checked) {
#   try {
#     const response = await fetch('/mark', {
#       method: 'POST',
#       headers: { 'Content-Type': 'application/json' },
#       body: JSON.stringify({ id: rowId, processed: checked ? 1 : 0 })
#     });
#     if (!response.ok) {
#       const txt = await response.text();
#       alert("Failed: " + txt);
#       return;
#     }
#     const currentPath = window.location.pathname;
#     if (currentPath.startsWith('/author/')) {
#       window.location.reload();
#     } else {
#       window.location.href = "/";
#     }
#   } catch (err) {
#     console.error(err);
#     alert("Request failed");
#   }
# }

# async function toggleSelected(rowId, checked) {
#   const feedback = document.getElementById('selected-feedback');
#   feedback.textContent = 'Saving...';
#   feedback.className = 'feedback';
#   try {
#     const response = await fetch('/toggle-selected', {
#       method: 'POST',
#       headers: { 'Content-Type': 'application/json' },
#       body: JSON.stringify({ id: rowId, selected: checked ? 1 : 0 })
#     });
#     if (!response.ok) {
#       const txt = await response.text();
#       feedback.textContent = '❌ Failed';
#       feedback.className = 'feedback feedback-error';
#       alert("Failed: " + txt);
#       return;
#     }
#     feedback.textContent = '✅ Selected';
#     feedback.className = 'feedback';
#     setTimeout(() => { window.location.reload(); }, 300);
#   } catch (err) {
#     feedback.textContent = '❌ Request failed';
#     feedback.className = 'feedback feedback-error';
#     console.error(err);
#   }
# }
# async function addAlias(rowId) {
#   const buildingId = document.getElementById('building-select').value;
#   const alias = document.getElementById('alias-input').value.trim();
#   const feedback = document.getElementById('alias-feedback');
#   if (!buildingId || !alias) {
#     feedback.textContent = '⚠️ Select a building and enter alias';
#     feedback.className = 'feedback feedback-error';
#     return;
#   }
#   feedback.textContent = 'Adding...';
#   try {
#     const resp = await fetch('/add-alias', {
#       method: 'POST',
#       headers: { 'Content-Type': 'application/json' },
#       body: JSON.stringify({ building_id: parseInt(buildingId), alias: alias })
#     });
#     const result = await resp.json();
#     if (resp.ok) {
#       feedback.textContent = '✅ Alias added!';
#       feedback.className = 'feedback';
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
# async function deletePost(rowId) {
#   const feedback = document.getElementById('delete-feedback');
#   if (!confirm('Are you sure you want to delete this post? This cannot be undone.')) {
#     return;
#   }
#   feedback.textContent = 'Deleting...';
#   feedback.className = 'feedback';
#   try {
#     const resp = await fetch('/delete-post', {
#       method: 'POST',
#       headers: { 'Content-Type': 'application/json' },
#       body: JSON.stringify({ id: rowId })
#     });
#     const result = await resp.json();
#     if (resp.ok && result.ok) {
#       feedback.textContent = '✅ Deleted!';
#       feedback.className = 'feedback';
#       // Stay on processed page
#       const currentPath = window.location.pathname;
#       if (currentPath.startsWith('/processed/') || currentPath === '/processed') {
#         window.location.href = '/processed';
#       } else if (currentPath.startsWith('/author/')) {
#         // If in author mode, stay in author mode
#         window.location.reload();
#       } else {
#         window.location.href = '/';
#       }
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
# </script>

# </body>
# </html>
# """
