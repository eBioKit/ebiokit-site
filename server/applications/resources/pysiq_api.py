import requests
import json

def enqueue(fn, args=[], task_id=None, depend=[], incompatible=[], server="localhost", port=4444, protocol="http"):
    server = protocol + "://" + server.replace(protocol + "://", "").rstrip("/") + ":" + str(port)
    response = requests.post(server + "/api/enqueue", json={
        'fn': fn,
        'args': args,
        'task_id': task_id,
        'depend': depend,
        'incompatible': incompatible
    })
    return Response(json.loads(response.text))

def check_status(task_id, server="localhost", port=4444, protocol="http"):
    server = protocol + "://" + server.replace(protocol + "://", "").rstrip("/") + ":" + str(port)
    response = requests.get(server + "/api/status/" + task_id)
    return Response(json.loads(response.text))

def get_result(task_id, remove=False, server="localhost", port=4444, protocol="http"):
    server = protocol + "://" + server.replace(protocol + "://", "").rstrip("/") + ":" + str(port)
    response = requests.get(server + "/api/result/" + task_id + ("?remove=1" if remove else ""))
    return Response(json.loads(response.text))

def remove_task(task_id, server="localhost", port=4444, protocol="http"):
    server = protocol + "://" + server.replace(protocol + "://", "").rstrip("/") + ":" + str(port)
    response = requests.delete(server + "/api/remove/" + task_id)
    return Response(json.loads(response.text))

class Response(object):
    def __init__(self, json_object):
        if "success" in json_object:
            self.success = json_object.get("success")
        if "status" in json_object:
            self.status = json_object.get("status")
        if "task_id" in json_object:
            self.task_id = json_object.get("task_id")
        if "result" in json_object:
            self.result = json_object.get("result")
