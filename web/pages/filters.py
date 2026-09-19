# # web.pages.filters.py
# from web.templates import FILTERS_TEMPLATE


# def build_filters_page(rows):
#     if not rows:
#         rows_html = '<tr><td colspan="3" class="empty-msg">No filter phrases.</td></tr>'
#     else:
#         rows_html = ""
#         for phrase, added_at in rows:
#             escaped_phrase = phrase.replace("'", "\\'").replace('"', '\\"')
#             rows_html += f"""
#             <tr>
#                 <td>{phrase}</td>
#                 <td>{added_at or 'N/A'}</td>
#                 <td><button class="delete-btn" onclick="deleteFilter('{escaped_phrase}')">Delete</button></td>
#             </tr>
#             """

#     return FILTERS_TEMPLATE % {"rows": rows_html}
