import requests, os
from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')

@app.route("/")
def index():
    data = requests.get(os.environ.get("BACKEND_URL") + "/generate")
    return render_template("index.html", data=data.text)

if __name__=="__main__":
    app.run(host='0.0.0.0')