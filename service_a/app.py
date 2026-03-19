import os
import requests
import socket
from flask import Flask, render_template, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)

BACKEND_URL = "http://service_b:5000"

TITLE = os.environ.get("POLL_TITLE", "Default Poll")
OPT_A = os.environ.get("OPTION_A", "Option A")
OPT_B = os.environ.get("OPTION_B", "Option B")

@app.route("/")
def index():
    try:
        r = requests.get(f"{BACKEND_URL}/results")
        data = r.json()
    except:
        data = {OPT_A: 0, OPT_B: 0}
    
    container_id = socket.gethostname()
    
    return render_template("index.html", 
                           title=TITLE, 
                           option_a=OPT_A, 
                           option_b=OPT_B, 
                           data=data,
                           container_id=container_id)

@app.route("/api/vote", methods=["POST"])
def api_vote():
    data = request.json
    vote = data.get("vote")

    try:
        requests.post(f"{BACKEND_URL}/vote", json={"tech": vote})
        results_resp = requests.get(f"{BACKEND_URL}/results")
        return jsonify({
            "status": "success", 
            "message": f"Голос за {vote} принят!",
            "results": results_resp.json()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)