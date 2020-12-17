import requests
from flask import Flask, request, jsonify, Response
import uuid
import threading
import time

port = 90

app = Flask(__name__)

supportedJobs = ["ndvi","sst","load_collection"]

@app.route("/takeJob", methods=["POST"])
def takeJob():
    print("Todo")
    print(request.get_json())
    #DoStuff
    return jsonify(None)


def sendBack():
    data = None
    requests.post("/getDataBack",json=data)




def init():
    data = {
        "id":0,
        "port": port,
        "supportedJobs":supportedJobs,
        "status": "idle"
    }
    requests.post("http://localhost:80/customRegister", json=data)

def serverBoot():
    """
    Startet den Server. Aktuell im Debug Modus und Reagiert auf alle eingehenden Anfragen auf Port 80.
    """
    app.run(debug=True, host="0.0.0.0", port=port)#Todo: Debug  Ausschalten, Beißt sich  mit Threading

if __name__ == "__main__":
    init()
    serverBoot()
