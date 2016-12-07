"""Main Entrypoint for the Application"""

import logging
import json
import base64

from flask import Flask, request
from flask import jsonify

import notebook
import utility


app = Flask(__name__)


@app.route('/')
def hello_world():

    """hello world"""
    return 'Hello World!'

@app.route('/pubsub/receive', methods=['POST'])
def pubsub_receive():
    """dumps a received pubsub message to the log"""

    data = {}
    try:
        obj = request.get_json()
        utility.log_info(json.dumps(obj))

        data = base64.b64decode(obj['message']['data'])
        utility.log_info(data)

    except Exception as e:
        # swallow up exceptions
        logging.exception('Oops!')

    return jsonify(data), 200


@app.route('/api/capitals/<id>', methods=['PUT', 'GET', 'DELETE'])

def access_notes(id=-1):
    """inserts and retrieves notes from datastore"""

    book = notebook.NoteBook()
    if request.method == 'GET':
        print int(id)
        print type(id)
        results = book.fetch_notes(id)
        #result = [notebook.parse_note_time(obj) for obj in results]
        return jsonify(results)
    elif request.method == 'PUT':
        print json.dumps(request.get_json())
        request_json = request.get_json()
        book.store_note(request_json, id)
        return "done"
    elif request.method == 'DELETE':
        try:
            book.delete_notes(id)
            return '',200
        except:
            return 500
    
@app.route('/api/capitals', methods=['GET'])

def fetch_all():
    """inserts and retrieves notes from datastore"""

    book = notebook.NoteBook()
    if request.method == 'GET':
        results = book.fetch_all()
        return jsonify(results)

@app.route('/api/status', methods=['GET'])
def get_status():
    """check the status of datastore and return True/False"""
    response = {'insert':True, 'fetch':True, 'delete':True, 'list':True }
    return jsonify(response), 200 
    
@app.errorhandler(500)
def server_error(err):
    """Error handler"""
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(err), 500


if __name__ == '__main__':
    # Used for running locally
    app.run(host='127.0.0.1', port=8080, debug=True)
