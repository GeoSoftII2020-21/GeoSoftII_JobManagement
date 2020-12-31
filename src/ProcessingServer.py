import requests
from flask import Flask, request, jsonify, Response
import uuid
import threading
import time
import queue
import os
import json
docker = False

app = Flask(__name__)



access = {
    "ndvi":None,
    "mean_sst":None,
    "load_collection": None
}

ports = {
    "ndvi": 441,
    "mean_sst": 442,
    "load_collection": 443
}
jobQueue = queue.Queue()


@app.route("/takeJob", methods=["POST"])
def takeJob():
    js = request.get_json()
    jobQueue.put(js)

    #DoStuff
    return Response(status=200)


def doJob():
    while True:
        if jobQueue.qsize() > 0:
            elem = jobQueue.get()
            if docker:
                requests.get("http://frontend:80/jobRunning/" + elem["id"])
            else:
                requests.get("http://localhost:80/jobRunning/" + elem["id"])
            data = {}
            for i in elem["process"]["process_graph"]:
                doing = True
                js = json.loads(elem["process"]["process_graph"][i])
                if "data" in elem["process"]["process_graph"][i]["arguments"]["data"]:
                    if "from_node"  in elem["process"]["process_graph"][i]["arguments"]["data"]:
                        if elem["process"]["process_graph"][i]["arguments"]["data"]["from_node"] in data:
                            elem["process"]["process_graph"][i]["arguments"]["data"]["from_node"] = data[elem["process"]["process_graph"][i]["arguments"]["data"]["from_node"]]
                if docker:
                    requests.post("http://" + access[elem["process"]["process_graph"][i]["process_id"]] + ":80/doJob",
                                  json=elem["process"]["process_graph"][i])  # Todo: Bearbeiten auf grudnlage der Prozess beschreibung
                else:
                    requests.post("http://localhost:" + ports[elem["process"]["process_graph"][i]["process_id"]] + "/doJob",
                                  json=elem["process"]["process_graph"][i])  # Todo: Bearbeiten auf grudnlage der Prozess beschreibung
                while doing:
                    if docker:
                        x = requests.get(
                            "http://" + access[elem["process"]["process_graph"][i]["process_id"]] + ":80/jobStatus")
                    else:
                        x = requests.get("http://localhost:" + ports[elem["process"]["process_graph"][i]["process_id"]] + "/jobStatus")  # Todo: Ersetzen durch direkte Request ohne Docker
                    x = x.json()
                    if x["status"] == "done":
                        doing = False
                        data[i] = x["result"]  #Todo: Ersetzen durch  Job Ergebnis
                    else:
                        time.sleep(5)
            if docker:
                requests.post("http://frontend:80/takeData" + elem["id"], json=data)
            else:
                requests.post("http://localhost:80/takeData" + elem["id"], json=data)
        else:
            print("skip Iteration")
            time.sleep(5)








def init():
    t = threading.Thread(target=doJob)
    t.start()
    access["ndvi"] = os.environ.get("ndvi")
    access["mean_sst"] = os.environ.get("mean_sst")
    access["load_collection"] = os.environ.get("load_collection")

def serverBoot():
    """
    Startet den Server. Aktuell im Debug Modus und Reagiert auf alle eingehenden Anfragen auf Port 80.
    """
    global docker
    if os.environ.get("DOCKER") == "True":
        docker = True
    if docker:
        port = 80
    else:
        port = 440
    app.run(debug=True, host="0.0.0.0", port=port)#Todo: Debug  Ausschalten, Beißt sich  mit Threading

if __name__ == "__main__":
    init()
    serverBoot()
