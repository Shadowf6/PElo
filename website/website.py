import http.server, importlib, pathlib, re, sys, io, threading, contextlib, urllib.parse

ROOT = pathlib.Path(__file__).parent.parent
# deployment files; testing: ROOT / "data" / "events.json" and ROOT / "data" / "elos.json"
DATA = ROOT / "Override-events.json"
ELOS = ROOT / "Override.json"
eval_lock = threading.Lock()  # evaluateTeam prints, and stdout capture is process-wide


def run_eval(team: str) -> str:
    """Runs src/eval.py's evaluateTeam and returns what it prints."""
    sys.path.insert(0, str(ROOT / "src"))
    import eval as team_eval  # needs requests + python-dotenv, and API_KEY in .env
    importlib.reload(team_eval)  # pick up edits to eval.py without restarting the server

    out = io.StringIO()
    with eval_lock, contextlib.redirect_stdout(out):
        try:
            team_eval.evaluateTeam(team)
        except Exception as e:
            print(f"\nEval failed: {type(e).__name__}: {e}")
    return out.getvalue()


class H(http.server.SimpleHTTPRequestHandler):
    def send_body(self, body: bytes, ctype: str, code: int = 200):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == "/events.json":
            self.send_body(DATA.read_bytes(), "application/json")
        elif url.path == "/elos.json":
            self.send_body(ELOS.read_bytes(), "application/json")
        elif url.path == "/eval":
            team = urllib.parse.parse_qs(url.query).get("team", [""])[0]
            if not re.fullmatch(r"[0-9A-Za-z]{1,10}", team):
                return self.send_body(b"Invalid team number.", "text/plain", 400)
            try:
                self.send_body(run_eval(team).encode(), "text/plain; charset=utf-8")
            except Exception as e:
                self.send_body(f"Could not run eval: {e}".encode(), "text/plain; charset=utf-8", 500)
        else:
            super().do_GET()


if __name__ == "__main__":
    import os
    os.chdir(pathlib.Path(__file__).parent)
    print("http://localhost:8000")
    # localhost only: /eval spends the API key from .env
    http.server.ThreadingHTTPServer(("127.0.0.1", 8000), H).serve_forever()
