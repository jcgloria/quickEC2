from flask import Flask, request, Response
from flask_cors import CORS
import utils
import json
import threading

app = Flask(__name__)

message_stream = []

CORS(app)

env = json.loads(open('credentials.json', 'r').read())
quickEC2 = utils.QuickEC2(access_key=env['access_key'], secret_key=env['secret_key'], region=env['region'])

@app.route('/api/instances', methods=['GET','POST', 'DELETE', 'PUT'])
def instances():
    if request.method == 'GET':
        return json.dumps(quickEC2.get_instances()) 
    if request.method == 'DELETE':
        data = request.get_json()
        task = threading.Thread(target=terminateTask, args=(data['instanceId'],data['instanceName']))
        task.start()
        return json.dumps({'status': 'process', 'message': 'Terminating instance ' + data['instanceName'] + '...'})
    if request.method == 'PUT':
        data = request.get_json()
        if data['action'] == 'stop':
            task = threading.Thread(target=stopTask, args=(data['instanceId'],))
            task.start()
            return json.dumps({'status': 'process', 'message': 'Instance stop task received'})
        elif data['action'] == 'start':
            task = threading.Thread(target=startTask, args=(data['instanceId'],))
            task.start()
            return json.dumps({'status': 'process', 'message': 'Instance start task received'})
    elif request.method == 'POST':
        data = request.get_json()
        task = threading.Thread(target=launchTask, args=(data,))
        task.start()
        return json.dumps({'status': 'process', 'message': 'Instance launch task received'})
    
@app.route('/api/key_path', methods=['GET'])
def get_key_path():
    return json.dumps({'status':'success', 'message': quickEC2.get_key_path()})

def launchTask(data):
    response = quickEC2.launch(data['instanceName'], data['publicIp'], data['linuxType'], data['inboundRules'])
    print(response)
    if response['message'] == 'VPC does not exist':
        response = createVPCTask()
        if response['status'] == 'success':
            emit_message(json.dumps({'status': 'process', 'message': 'VPC created successfully. Launching instance...'}))
            response = quickEC2.launch(data['instanceName'], data['publicIp'], data['linuxType'], data['inboundRules'])
            print(response)
    emit_message(json.dumps(response))

def createVPCTask():
    emit_message(json.dumps({'status': 'process', 'message': 'VPC is being created...'}))
    response = quickEC2.create_VPC()
    return response

def terminateTask(instanceId, instanceName):
    response = quickEC2.terminate_instance(instanceId, instanceName)
    print(response)
    emit_message(json.dumps(response))

def stopTask(instanceId):
    response = quickEC2.stop_instance(instanceId)
    print(response)
    emit_message(json.dumps(response))

def startTask(instanceId):
    response = quickEC2.start_instance(instanceId)
    print(response)
    emit_message(json.dumps(response))

@app.route('/stream')
def stream():
    def generate():
        global message_stream
        for message in message_stream:
            yield 'data: ' + message + '\n\n'
            message_stream.remove(message)

    return Response(generate(), mimetype='text/event-stream')

def emit_message(message):
    global message_stream
    message_stream.append(message)