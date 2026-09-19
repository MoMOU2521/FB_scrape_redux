# # web.pages.blacklist.py
# from web.templates import BLACKLIST_TEMPLATE


# def build_blacklist_page(rows):
#     if not rows:
#         rows_html = (
#             '<tr><td colspan="3" class="empty-msg">No blacklisted authors.</td></tr>'
#         )
#     else:
#         rows_html = ""
#         for author, count in rows:
#             escaped_author = author.replace("'", "\\'").replace('"', '\\"')
#             rows_html += f"""
#             <tr>
#                 <td>{author}</td>
#                 <td>{count}</td>
#                 <td><button class="delete-btn" onclick="deleteBlacklist('{escaped_author}')">Delete</button></td>
#             </tr>
#             """

#     return BLACKLIST_TEMPLATE % {"rows": rows_html}
