import json
import os


def handler(event, context):
    os.system(f"blender -b -P script.py -- {event.get('width', 0)} {event.get('height', 0)}")
    return {
        "statusCode": 200,
        "body": json.dumps({"circumference": 'ok'})
    }