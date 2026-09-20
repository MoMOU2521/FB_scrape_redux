# AUTHOR_LIST_TEMPLATE = """<!DOCTYPE html>
# <html>
# <head>
# <meta charset="utf-8">
# <title>Authors by Unprocessed Posts</title>
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
#   .author-link {
#     color: #2196F3;
#     text-decoration: none;
#     font-weight: bold;
#   }
#   .author-link:hover {
#     text-decoration: underline;
#   }
#   .empty-msg {
#     color: #666;
#     font-style: italic;
#     padding: 20px 0;
#   }
#   .count-badge {
#     display: inline-block;
#     background: #e3f2fd;
#     padding: 2px 12px;
#     border-radius: 12px;
#     font-weight: bold;
#     color: #1565C0;
#   }
# </style>
# </head>
# <body>
# <h1>👤 Authors with Most Unprocessed Posts</h1>
# <a href="/" class="back-link">← Back to posts</a>
# <a href="/stats" class="back-link">📊 Stats</a>
# <a href="/blacklist" class="back-link admin-link">🚫 Blacklist</a>
# <a href="/filters" class="back-link admin-link">🔍 Filter Phrases</a>

# <table>
#   <thead>
#     <tr>
#       <th>#</th>
#       <th>Author</th>
#       <th>Unprocessed Posts</th>
#       <th>Action</th>
#     </tr>
#   </thead>
#   <tbody>
#     %(rows)s
#   </tbody>
# </table>
# </body>
# </html>
# """
