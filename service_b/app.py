import time
import os
import redis
from flask import Flask, request, jsonify

app = Flask(__name__)

r = redis.Redis(host='redis', port=6379, db=0)

OPT_A = os.environ.get("OPTION_A", "Option A")
OPT_B = os.environ.get("OPTION_B", "Option B")

@app.route("/vote", methods=["POST"])
def vote():
    time.sleep(0.1) # Simulate load
    
    data = request.json
    tech = data.get("tech")
    
    if tech in [OPT_A, OPT_B]:
        r.incr(tech)
        return jsonify({"status": "ok", "voted_for": tech})
    
    return jsonify({"error": "Invalid option. Allowed: " + OPT_A + ", " + OPT_B}), 400

@app.route("/results", methods=["GET"])
def results():
    val_a = r.get(OPT_A) or 0
    val_b = r.get(OPT_B) or 0
    
    # Form a dynamic response, e.g., {"Cats": 5, "Dogs": 10}
    return jsonify({
        OPT_A: int(val_a),
        OPT_B: int(val_b)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)