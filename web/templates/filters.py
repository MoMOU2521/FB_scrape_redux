FILTERS_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Filter Phrases</title>
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
  .empty-msg {
    color: #666;
    font-style: italic;
    padding: 20px 0;
  }
</style>
</head>
<body>
<h1>🔍 Filter Phrases</h1>
<a href="/" class="back-link">← Back to posts</a>
<a href="/stats" class="back-link">📊 Stats</a>
<a href="/blacklist" class="back-link admin-link">🚫 Blacklist</a>
<a href="/authors" class="back-link admin-link">👤 Authors</a>

<table>
  <thead>
    <tr>
      <th>Phrase</th>
      <th>Added At</th>
      <th>Action</th>
    </tr>
  </thead>
  <tbody>
    %(rows)s
  </tbody>
</table>

<script>
async function deleteFilter(phrase) {
  if (!confirm(`Remove "${phrase}" from filter phrases?`)) return;
  try {
    const resp = await fetch('/delete-filter', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phrase: phrase })
    });
    if (resp.ok) {
      window.location.reload();
    } else {
      alert('Failed to delete');
    }
  } catch (e) {
    alert('Request failed');
    console.error(e);
  }
}
</script>
</body>
</html>
"""
