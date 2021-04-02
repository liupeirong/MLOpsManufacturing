import json
from azure.iot.device import Message
from datetime import datetime

DATETIME_STRING_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

def GenerateHighConfidenceMessage():
    et = datetime.now().strftime(DATETIME_STRING_FORMAT)
    return GenerateDetectedObjectsMessage(confidence=0.95494674, eventTime=et)

def GenerateLowConfidenceMessage():
    et = datetime.now().strftime(DATETIME_STRING_FORMAT)
    return GenerateDetectedObjectsMessage(confidence=0.00954946, eventTime=et)

def GenerateDetectedObjectsMessage(route='detectedObjects', tag='truck', confidence=0.5, eventTime="2020-11-24T19:22:05.912Z"):
    data = {"timestamp": 145381193281325}
    entityTag = {"value": tag, "confidence": confidence}
    entityBox = {"l": 0.55859375, "t": 0.03125, "w": 0.3046875, "h": 0.6076389}
    entity = {"tag": entityTag, "box": entityBox}
    inferenceDict = {"type": "entity", "entity": entity}
    inferences = [inferenceDict]
    data["inferences"] = inferences
    message = CreateMessage(data)
    message.input_name = route
    message.custom_properties = {
        "$.cdid": "virtualMachine",
        "subject": "/graphInstances/Truck/processors/grpcExtension",
        "eventType": "Microsoft.Media.Graph.Analytics.Inference",
        "eventTime": eventTime,
        "dataVersion": "1.0"
    }
    return message

def CreateMessage(data):
    return Message(json.dumps(data).encode('utf-8'), content_type="application/json")
