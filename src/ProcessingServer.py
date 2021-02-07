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


dataserver_ready = False

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

@app.route("/dataStatus",methods=["GET"])
def dataStatus():
    """
    Takes the data store status
    """
    global dataserver_ready
    dataserver_ready = True


@app.route("/takeJob", methods=["POST"])
def takeJob():
    """
    Takes a job and queues it.
    :return:
    """
    js = request.get_json()
    jobQueue.put(js)

    #DoStuff
    return Response(status=200)


def doJob():
    """
    Processes the job in a extrea thread.
    """
    global dataserver_ready
    while True:
        while not dataserver_ready:
            time.sleep(5)
        status = "idle"
        if jobQueue.qsize() > 0:
            elem = jobQueue.get()
            status = "running"
            if docker:
                req = requests.get("http://frontend:8080/jobRunning/" + elem["id"])
            else:
                req = requests.get("http://localhost:8080/jobRunning/" + elem["id"])
            req = req.json()
            if req["status"] == "running":
                os.mkdir("data/"+ elem["id"])
                data = {}
                for i in elem["process"]["process_graph"]:
                    if status == "error":
                        continue
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
                            if x["status"] == "done" and x["jobid"] == elem["id"]:
                                doing = False
                                data[i] = x["id"]
                            elif x["status"] == "error" and x["jobid"]:
                                status = "error"
                                doing = False
                                if docker:
                                    requests.post("http://frontend:8080/takeData/" + str(elem["id"]),
                                                  params={"status": status,  "errorType": x["errorType"]})
                                else:
                                    requests.post("http://localhost:8080/takeData/" + str(elem["id"]),params={"status": status})
                                break #Evtl doch Continue?
                            else:
                                time.sleep(5)
                    if status == "error":
                        break
                if status != "error":
                    requests.post("http://frontend:8080/takeData/" + str(elem["id"]),  params={"status": "done"})
        else:
            print("skip Iteration")
            time.sleep(5)








def init():
    """
    Initialize the extra Thread
    """
    t = threading.Thread(target=doJob)
    t.start()
    access["ndvi"] = os.environ.get("ndvi")
    access["mean_sst"] = os.environ.get("mean_sst")
    access["load_collection"] = os.environ.get("load_collection")

def serverBoot():
    """
    Starts the Server.
    """
    global docker
    if os.environ.get("DOCKER") == "True":
        docker = True
    if docker:
        port = 80
    else:
        port = 440
    app.run(debug=True, host="0.0.0.0", port=port)

if __name__ == "__main__":
    init()
    serverBoot()
