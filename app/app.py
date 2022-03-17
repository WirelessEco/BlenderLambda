import json
import os
import boto3

def handler(event, context):
    #Reference the S3 Bucket
    s3 = boto3.client('s3')
    bucket = event["pathParameters"]["bucket"] #Default is blender-lambda-evantobin91384

    #Reference the stored python script that blender will run as well as the intial 3D file of the leg
    pythonFileKey = 'bpyScript.py'
    legFileKey = event["queryStringParameters"]["file"] #Default is Leg.stl
    
    #Downloads the python script and 3D file to the /tmp/ directories of the linux image
    s3.download_file(bucket, legFileKey, '/tmp/' + legFileKey)
    print("Successfully downloaded " + legFileKey)
    os.rename('/tmp/' + legFileKey, '/tmp/Leg.stl')
    print("Successfully renamed " + legFileKey + " to Leg.stl")
    s3.download_file(bucket, pythonFileKey, '/tmp/' + pythonFileKey)
    print("Successfully downloaded " + pythonFileKey)

    #Runs an instance of blender which then utilizes the newly imported script
    os.system(f"blender -b -P /tmp/bpyScript.py")

    #Uses the results outputted to to bpyScript_output.txt file during the instance of blender and then attaches the results to a tuple called results
    filepath = "/tmp/bpyScript_output.txt"
    with open(filepath) as fp:
        results = fp.read().splitlines()
    
    #Configuring the output of the script to a json-type output
    Dictionary ={'thigh':results[0], 'knee_width':results[1],'calf':results[2]}
    json_string = json.dumps(Dictionary, allow_nan = True, indent = 6)
    
    return {
        "statusCode": 200,
        "body": json_string
    }

