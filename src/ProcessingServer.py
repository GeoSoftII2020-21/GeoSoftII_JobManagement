import requests
from flask import Flask, request, jsonify, Response
import uuid
import threading
import time
import queue

app = Flask(__name__)

access = {
    "ndvi":445,
    "sst":444,
    "load_collection":443
}

jobQueue = queue.Queue()
doneJobs = queue.Queue()

@app.route("/takeJob", methods=["POST"])
def takeJob():
    js = request.get_json()
    jobQueue.put(js)

    #DoStuff
    return jsonify(None)


def doJob():
    if jobQueue.qsize() > 0:
        elem = jobQueue.get()
        requests.get("http://localhost:80/jobRunning/"+elem["id"])
        print(elem)
        data = {}
        for i in elem["process"]["process_graph"]:
            if elem["process"]["process_graph"][i]["process_id"] == "load_collection":
                data[i] = requests.get("http://localhost:" + str(access["load_collection"]) + "/data",
                                       json=elem["process"]["process_graph"][i])
            if jobQueue[0]["process"]["process_graph"][i]["process_id"] == "sst":
                data[i] = requests.get("http://localhost:" + str(access["sst"]) + "/doJob", json={})

        doneJobs.put(elem)#Ersetzen durch ergebnis
    else:
        print("skip Iteration")
        time.sleep(5)
        doJob()
    #Send Main Server Data






def init():
    data = {
        "id":0,
        "port": 442,
        "status": "idle"
    }
    t = threading.Thread(target=doJob)
    t.start()

def serverBoot():
    """
    Startet den Server. Aktuell im Debug Modus und Reagiert auf alle eingehenden Anfragen auf Port 80.
    """
    app.run(debug=True, host="0.0.0.0", port=442)#Todo: Debug  Ausschalten, Beißt sich  mit Threading

if __name__ == "__main__":
    init()
    serverBoot()
