import requests, os
from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')

@app.route("/")
def index():
    urls = {"url": os.environ.get("BACKEND_URL")}
    return render_template("index.html", data=urls)

if __name__=="__main__":
    app.run(host='0.0.0.0')