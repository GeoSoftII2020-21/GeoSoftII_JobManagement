import requests
from flask import Flask, request, jsonify, Response
import uuid
import threading
import time
import queue
import os
import json
import xarray
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
    """
    Nimmt job vom Frontend entgegen und queued ihn für die weitere bearbeitung. Antwortet mit status code 200.
    :return:
    """
    js = request.get_json()
    jobQueue.put(js)

    #DoStuff
    return Response(status=200)


def doJob():
    """
    Führt den Job in einem Extra Thread aus. Dazu wird erst der Status überprüft und danach wird jeder job teil an die dafür spezialisierten server weiter geleitet.
    Das ergebnis wird am ende zurück ans Frontend gepostet.
    """
    while True:
        if jobQueue.qsize() > 0:
            elem = jobQueue.get()
            if docker:
                req = requests.get("http://frontend:80/jobRunning/" + elem["id"])
            else:
                req = requests.get("http://localhost:80/jobRunning/" + elem["id"])
            req = req.json()
            if req["status"] == "running":
                os.mkdir("data/"+ elem["id"])
                data = {}
                for i in elem["process"]["process_graph"]:
                    if elem["process"]["process_graph"][i]["process_id"] == "save_result":
                        if elem["process"]["process_graph"][i]["arguments"]["Format"] == "netcdf":
                            os.mkdir("data/" + str(elem["id"])+ "/saves")
                            x = data[elem["process"]["process_graph"][i]["arguments"]["SaveData"]["from_node"]]
                            x = xarray.load_dataset("data/"+str(elem["id"])+"/"+str(x)+".nc")
                            x.to_netcdf("data/" + str(elem["id"])+ "/saves"+ "/" + str(uuid.uuid1())+ ".nc")
                    else:
                        doing = True
                        if "data" in elem["process"]["process_graph"][i]["arguments"]:
                            if "from_node"  in elem["process"]["process_graph"][i]["arguments"]["data"]:
                                if elem["process"]["process_graph"][i]["arguments"]["data"]["from_node"] in data:
                                    elem["process"]["process_graph"][i]["arguments"]["data"]["from_node"] = str(data[elem["process"]["process_graph"][i]["arguments"]["data"]["from_node"]])
                        if docker:
                            requests.post("http://" + access[elem["process"]["process_graph"][i]["process_id"]] + ":80/doJob/"+ str(elem["id"]),
                                          json=elem["process"]["process_graph"][i])
                        else:
                            requests.post("http://localhost:" + str(ports[elem["process"]["process_graph"][i]["process_id"]]) + "/doJob/"+str(elem["id"]),
                                          json=elem["process"]["process_graph"][i])
                        while doing:
                            if docker:
                                x = requests.get(
                                    "http://" + access[elem["process"]["process_graph"][i]["process_id"]] + ":80/jobStatus")
                            else:
                                x = requests.get("http://localhost:" + str(ports[elem["process"]["process_graph"][i]["process_id"]]) + "/jobStatus")
                            x = x.json()
                            if x["status"] == "done":
                                doing = False
                                data[i] = x["id"]  #Todo: Ersetzen durch  Job Ergebnis
                            else:
                                time.sleep(5)
                if docker:
                    requests.post("http://frontend/takeData/" + str(elem["id"]))
                else:
                    requests.post("http://localhost:80/takeData/" + str(elem["id"]))
        else:
            print("skip Iteration")
            time.sleep(5)








def init():
    """
    Initialisiert etwas logik in dem es den Thread startet und notwendige umgebungs variablen ausliest
    """
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
