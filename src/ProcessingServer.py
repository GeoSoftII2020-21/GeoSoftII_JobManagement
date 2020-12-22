import requests
from flask import Flask, request, jsonify, Response
import uuid
import threading
import time
import queue

app = Flask(__name__)

access = {
    "ndvi":445,
    "mean_sst":444,
    "load_collection":443
}

jobQueue = queue.Queue()


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
            doing = True
            requests.post("http://localhost:" + access[elem["process"]["process_graph"][i]["process_id"]] + "/doJob",
                                   json=elem["process"]["process_graph"][i])#Todo: Bearbeiten auf grudnlage der Prozess beschreibung
            while doing:
                x = requests.get("http://localhost:" + access[elem["process"]["process_graph"][i]["process_id"]] + "/jobStatus")
                if x["status"] == "done":
                    doing = False
                    data[i] = x
                time.sleep(5)
        requests.post("http://localhost:80/takeData" + elem["id"], json=None)
    else:
        print("skip Iteration")
        time.sleep(5)
    doJob()
    #Send Main Server Data






def init():
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
