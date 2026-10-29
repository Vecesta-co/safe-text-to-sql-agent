import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from .executor import SafeSQLExecutor
from .validator import validate_and_sanitize_sql

class SafeSQLServerHandler(BaseHTTPRequestHandler):
    executor: SafeSQLExecutor = None

    def _send_json(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _send_html(self, html: str, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._send_html(self._render_dashboard())
        elif parsed.path == "/schema":
            self._send_json(self.executor.schema.model_dump())
        elif parsed.path == "/tables":
            tables_summary = {
                tname: {"columns": [c.name for c in t.columns], "row_count": t.row_count}
                for tname, t in self.executor.schema.tables.items()
            }
            self._send_json(tables_summary)
        elif parsed.path == "/health":
            self._send_json({"status": "healthy", "service": "safe-text-to-sql-agent"})
        else:
            self._send_json({"error": "not found"}, status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"

        try:
            payload = json.loads(body)
        except Exception:
            self._send_json({"error": "Invalid JSON payload"}, status=400)
            return

        if parsed.path == "/query":
            natural_q = payload.get("query")
            raw_sql = payload.get("sql")
            res = self.executor.execute_query(natural_query=natural_q, raw_sql=raw_sql)
            self._send_json(res.model_dump())
        elif parsed.path == "/validate":
            sql = payload.get("sql", "")
            val = validate_and_sanitize_sql(sql)
            self._send_json(val.model_dump())
        else:
            self._send_json({"error": "not found"}, status=404)

    def _render_dashboard(self) -> str:
        return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Vecesta Safe Text-to-SQL Studio</title>
  <style>
    body { background: #0f172a; color: #f8fafc; font-family: -apple-system, sans-serif; padding: 25px; }
    h1 { color: #38bdf8; margin-bottom: 5px; }
    .subtitle { color: #94a3b8; margin-top: 0; }
    .card { background: #1e293b; padding: 20px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 20px; max-width: 800px; }
    input { width: 100%; padding: 10px; background: #0f172a; border: 1px solid #475569; color: #fff; border-radius: 4px; box-sizing: border-box; }
    button { margin-top: 10px; padding: 10px 16px; background: #0284c7; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
    button:hover { background: #0369a1; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }
    th, td { border: 1px solid #334155; padding: 8px 12px; text-align: left; }
    th { background: #0f172a; color: #38bdf8; }
    pre { background: #0f172a; padding: 10px; border-radius: 4px; border: 1px solid #334155; overflow-x: auto; font-family: monospace; }
  </style>
</head>
<body>
  <h1>Safe Text-to-SQL Studio</h1>
  <p class="subtitle">AST-Validated Read-Only Natural Query Interface</p>

  <div class="card">
    <h3>Ask Database Question</h3>
    <input type="text" id="queryInput" value="Show top 5 tracks by price" placeholder="e.g. Sales by country, list all artists, albums by Queen...">
    <button onclick="runQuery()">Execute Natural Query</button>
    <div id="queryOutput" style="margin-top: 15px;"></div>
  </div>

  <script>
    async function runQuery() {
      const q = document.getElementById('queryInput').value;
      const res = await fetch('/query', { method: 'POST', body: JSON.stringify({ query: q }) });
      const data = await res.json();
      const div = document.getElementById('queryOutput');
      if (data.error) {
        div.innerHTML = `<p style="color: #ef4444;">❌ ${data.error}</p>`;
      } else {
        let tableHtml = '<table><thead><tr>' + data.columns.map(c => `<th>${c}</th>`).join('') + '</tr></thead><tbody>';
        data.rows.forEach(r => {
          tableHtml += '<tr>' + r.map(v => `<td>${v}</td>`).join('') + '</tr>';
        });
        tableHtml += '</tbody></table>';
        div.innerHTML = `
          <p style="color: #94a3b8; font-size: 13px;">Generated SQL: <code>${data.generated_sql}</code> (${data.execution_time_ms} ms, ${data.row_count} rows)</p>
          ${tableHtml}
        `;
      }
    }
  </script>
</body>
</html>"""

    def log_message(self, format, *args):
        pass

def run_server(port: int = 8080, db_path: str = "fixtures/chinook.db"):
    executor = SafeSQLExecutor(db_path)
    SafeSQLServerHandler.executor = executor
    server = HTTPServer(("0.0.0.0", port), SafeSQLServerHandler)
    print(f"Safe SQL server listening on http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

