import time
import random
from flask import Flask

app = Flask(__name__)

@app.route("/calculate")
def calculate():
    delay = random.uniform(0.1, 0.5)
    time.sleep(delay)
    return f"Calculation done in {delay:.2f} seconds!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)