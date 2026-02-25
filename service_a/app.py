import requests
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    # POST запрос
    if request.method == "POST":
        vote = request.form.get("vote")
        try:
            requests.post(f"http://service_b:5000/vote", json={"tech": vote})
            message = f"Спасибо! Ваш голос за {vote} принят."
        except:
            message = "Ошибка на внутренней стороне."

    try:
        r = requests.get("http://service_b:5000/results")
        data = r.json()
    except:
        data = {"python": 0, "go": 0}

    return render_template("index.html", data=data, message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)