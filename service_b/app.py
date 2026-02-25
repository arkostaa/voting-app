import time
import redis
from flask import Flask, request, jsonify

app = Flask(__name__)

r = redis.Redis(host='redis', port=6379, db=0)

@app.route("/vote", methods=["POST"])
def vote():
    time.sleep(0.1)
    
    data = request.json
    tech = data.get("tech")
    
    if tech in ["python", "go"]:
        r.incr(tech)
        return jsonify({"status": "ok", "voted_for": tech})
    return jsonify({"error": "invalid choice"}), 400

@app.route("/results", methods=["GET"])
def results():
    python_votes = r.get("python") or 0
    go_votes = r.get("go") or 0
    
    return jsonify({
        "python": int(python_votes),
        "go": int(go_votes)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)