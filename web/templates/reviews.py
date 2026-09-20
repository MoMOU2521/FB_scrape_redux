# # templates/reviews.py
# REVIEW_TEMPLATE = """<!DOCTYPE html>
# <html>
# <head>
# <meta charset="utf-8">
# <title>Review Queue (%(current)d / %(total)d)</title>
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

#   .admin-actions {
#     margin: 20px 0;
#     padding: 15px;
#     border: 1px solid #ccc;
#     border-radius: 6px;
#     background: #fafafa;
#   }

#   .admin-actions .action-row {
#     margin: 8px 0;
#   }

#   .admin-actions button {
#     padding: 8px 16px;
#     cursor: pointer;
#     color: white;
#     border: none;
#     border-radius: 4px;
#     margin-right: 8px;
#   }

#   .btn-approve {
#     background: #4CAF50;
#   }

#   .btn-reject {
#     background: #f44336;
#   }

#   .btn-dismiss {
#     background: #666;
#   }

#   .feedback {
#     font-size: 0.9em;
#     color: #2e7d32;
#     margin-left: 10px;
#   }

#   .feedback-error {
#     color: #d32f2f;
#   }

#   .candidate-box {
#     margin: 10px 0;
#     padding: 10px 12px;
#     background: #fffbe6;
#     border: 1px solid #ddd;
#     border-radius: 4px;
#   }
# </style>
# </head>

# <body>

# <h2>🔎 Review Queue (%(current)d / %(total)d)</h2>

# <div class="nav-stats">
#   <a href="/" class="back-link">← Back to posts</a>
#   <a href="/">📋 Unprocessed</a>
#   <a href="/processed">✅ Processed</a>
#   <a href="/stats">📊 Group Statistics</a>
#   <a href="/blacklist" class="admin-link">🚫 Blacklist</a>
#   <a href="/filters" class="admin-link">🔍 Filter Phrases</a>
#   <a href="/authors" class="admin-link">👤 Authors</a>
# </div>

# <div class="nav">
#   %(prev_button)s
#   %(next_button)s
# </div>

# <div class="meta">
#   <strong>Author:</strong> %(author)s<br>
#   <strong>Post URL:</strong> <a href="%(post_url)s" target="_blank">%(post_url)s</a><br>
#   <strong>Scraped at:</strong> %(scraped_at)s
# </div>

# <div class="candidate-box">%(candidate_html)s</div>

# <div class="meta">Post text:</div>
# <div class="post-text">%(text)s</div>

# <div class="meta">Extraction JSON:</div>
# <div class="post-text">%(extraction_result_json)s</div>

# <div class="admin-actions">
#   <div class="action-row">
#     <button class="btn-approve" onclick="reviewAction(%(review_id)d, 'approve')">✅ Approve (insert)</button>
#     <button class="btn-reject" onclick="reviewAction(%(review_id)d, 'reject')">❌ Reject (discard)</button>
#     <button class="btn-dismiss" onclick="reviewAction(%(review_id)d, 'dismiss')">↩️ Dismiss (leave as-is)</button>
#     <span id="review-feedback" class="feedback"></span>
#   </div>
# </div>

# <script>
# async function reviewAction(id, action) {
#   const feedback = document.getElementById('review-feedback');
#   feedback.textContent = 'Working...';
#   feedback.className = 'feedback';
#   try {
#     const resp = await fetch('/review-action', {
#       method: 'POST',
#       headers: { 'Content-Type': 'application/json' },
#       body: JSON.stringify({ id: id, action: action })
#     });
#     const result = await resp.json();
#     if (resp.ok && result.ok) {
#       feedback.textContent = '✅ Done!';
#       feedback.className = 'feedback';
#       setTimeout(() => { window.location.href = '/review'; }, 300);
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
