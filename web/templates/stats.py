STATS_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Group Statistics</title>
<style>
  body {
    font-family: sans-serif;
    max-width: 900px;
    margin: 20px auto;
    padding: 0 15px;
  }
  table {
    width: 100%%;
    border-collapse: collapse;
    margin: 20px 0;
  }
  th, td {
    padding: 10px 15px;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }
  th {
    background: #f5f5f5;
    font-weight: bold;
  }
  .back-link {
    display: inline-block;
    margin: 15px 0;
    padding: 8px 16px;
    background: #4CAF50;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    margin-right: 10px;
  }
  .back-link.admin-link {
    background: #ff9800;
  }
  .total-row {
    font-weight: bold;
    background: #fafafa;
  }
  .percentage {
    color: #555;
  }
  .delete-btn {
    background: #f44336;
    color: white;
    border: none;
    padding: 4px 12px;
    border-radius: 4px;
    cursor: pointer;
  }
  .delete-btn:hover {
    background: #d32f2f;
  }
  .list-table td {
    word-break: break-all;
  }
</style>
</head>
<body>
<h1>📊 Group Statistics</h1>
<a href="/" class="back-link">← Back to posts</a>
<a href="/blacklist" class="back-link admin-link">🚫 Blacklist</a>
<a href="/filters" class="back-link admin-link">🔍 Filter Phrases</a>
<a href="/authors" class="back-link admin-link">👤 Authors</a>

<table>
  <thead>
    <tr>
      <th>Group Name</th>
      <th>Total Posts</th>
      <th>Selected</th>
      <th>Selection Rate</th>
    </tr>
  </thead>
  <tbody>
    %(rows)s
    <tr class="total-row">
      <td>TOTAL</td>
      <td>%(total_posts)d</td>
      <td>%(total_selected)d</td>
      <td>%(total_rate)s%%</td>
    </tr>
  </tbody>
</table>
</body>
</html>
"""
