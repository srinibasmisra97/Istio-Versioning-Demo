import random, string
from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')

@app.route("/generate")
def index():
    random_string = ''.join(random.choice(string.ascii_letters) for i in range(10))
    return "v1-" + random_string

if __name__=="__main__":
    app.run(host='0.0.0.0')