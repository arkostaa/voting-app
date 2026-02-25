import time
import requests
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    time.sleep(0.1)
    try:
        # Обращаемся к service_b по имени контейнера
        response = requests.get("http://service_b:5000/calculate")
        result = response.text
    except:
        result = "Service B unavailable"
    return f"Service A says: {result}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)