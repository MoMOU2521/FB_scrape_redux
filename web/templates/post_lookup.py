# POST_LOOKUP_TEMPLATE = """<!DOCTYPE html>
# <html>
# <head>
# <meta charset="utf-8">
# <title>Scraped Post Lookup</title>

# <style>
#   body {
#     font-family: sans-serif;
#     max-width: 900px;
#     margin: 20px auto;
#     padding: 0 15px;
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

#   .nav-stats a.back-link {
#     background: #666;
#   }

#   .search-box {
#     margin: 20px 0;
#     padding: 15px;
#     border: 1px solid #ccc;
#     border-radius: 6px;
#     background: #fafafa;
#   }

#   .search-box input {
#     width: 220px;
#     padding: 8px;
#     font-size: 16px;
#   }

#   .search-box button {
#     padding: 9px 18px;
#     margin-left: 8px;
#     cursor: pointer;
#   }

#   .error {
#     margin: 15px 0;
#     padding: 12px;
#     color: #b71c1c;
#     background: #ffebee;
#     border: 1px solid #ef9a9a;
#     border-radius: 4px;
#   }

#   .meta {
#     color: #555;
#     margin-bottom: 12px;
#   }

#   .post-text {
#     white-space: pre-wrap;
#     background: #f5f5f5;
#     padding: 12px;
#     border-radius: 4px;
#     margin-bottom: 15px;
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


# </style>
# </head>

# <body>

# <h2>🔎 Scraped Post Lookup</h2>

# <div class="nav-stats">
#   <a href="/" class="back-link">← Back to posts</a>
#   <a href="/processed">✅ Processed</a>
#   <a href="/review" class="admin-link">🔎 Review Queue</a>
# </div>

# <div class="search-box">
#   <form method="GET" action="/post-lookup">
#     <label for="row_id"><strong>SQLite Row ID:</strong></label>
#     <input
#       type="number"
#       id="row_id"
#       name="id"
#       min="1"
#       value="%(searched_id)s"
#       required
#       autofocus
#     >
#     <button type="submit">Search</button>
#   </form>
# </div>

# %(error)s

# %(post_content)s

# </body>
# </html>
# """


# def build_post_lookup_content(post):
#     if not post:
#         return ""

#     images_html = post.get("images_html", "")

#     return f"""
# <h3>Post #{post["id"]}</h3>

# <div class="meta">
#   <strong>Author:</strong> {post.get("author", "")}<br>
#   <strong>Group:</strong> {post.get("group_name", "")}<br>
#   <strong>SQLite Row ID:</strong> {post.get("id", "")}<br>
#   <strong>Post ID:</strong> {post.get("post_id", "")}<br>
#   <strong>Processed:</strong> {"Yes" if post.get("processed") else "No"}<br>
#   <strong>Selected:</strong> {"Yes" if post.get("selected") else "No"}<br>
#   <strong>AI Processed:</strong> {"Yes" if post.get("ai_processed") else "No"}<br>
#   <strong>Building Review:</strong> {"Yes" if post.get("review_building") else "No"}<br>
#   <strong>Scraped at:</strong> {post.get("scraped_at", "")}
# </div>

# <div class="meta">
#   Original:
#   <a href="{post.get("post_url", "")}" target="_blank">
#     {post.get("post_url", "")}
#   </a>
# </div>

# <div class="meta">Post text:</div>
# <div class="post-text">{post.get("text", "")}</div>

# <div class="meta">AI Result (Gate 1):</div>
# <div class="post-text">{post.get("result_json_v1") or "Not yet AI-processed"}</div>

# <details class="reasoning-panel">
#   <summary>
#     🧠 Gate 1 reasoning
#     (prompt v{post.get("gate1_prompt_version") or "unknown"})
#   </summary>
#   <div class="post-text reasoning-text">
#     {post.get("gate1_reasoning") or "No reasoning recorded."}
#   </div>
# </details>

# <div class="meta">AI Result (Extraction):</div>
# <div class="post-text">
#   {post.get("extraction_result_json") or "Not yet extracted"}
# </div>

# <details class="reasoning-panel">
#   <summary>
#     🧠 Extraction reasoning
#     (prompt v{post.get("extraction_prompt_version") or "unknown"})
#   </summary>
#   <div class="post-text reasoning-text">
#     {post.get("extraction_reasoning") or "No reasoning recorded."}
#   </div>
# </details>

# {images_html}
# """


# def render_post_lookup_page(post=None, searched_id=None, error=None):
#     post_content = ""

#     if post:
#         images_html = ""

#         for img_path in post.get("images", []):
#             images_html += f'<img src="/{img_path}" alt="">\n'

#         post["images_html"] = images_html
#         post_content = build_post_lookup_content(post)

#     error_html = ""

#     if error:
#         error_html = f'<div class="error">{error}</div>'

#     return POST_LOOKUP_TEMPLATE % {
#         "searched_id": ("" if searched_id is None else str(searched_id)),
#         "error": error_html,
#         "post_content": post_content,
#     }
