import requests, os
from flask import Flask, render_template, request

app = Flask(__name__, template_folder='templates')

@app.route("/")
def index():
    version = "live" if request.headers.get("version") is None else request.headers.get("version")
    data = requests.get(os.environ.get("BACKEND_URL") + "/generate", headers={"version": version})
    return render_template("index.html", data=data.text)

if __name__=="__main__":
    app.run(host='0.0.0.0')