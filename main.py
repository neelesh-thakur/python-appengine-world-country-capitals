"""Main Entrypoint for the Application"""

import logging
import json
import base64

from flask import Flask, request
from flask import jsonify
from google.cloud import pubsub

import notebook
import utility
import storage
import StringIO


app = Flask(__name__)
gcs = storage.Storage()

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
    integer_id = int(id)
    try:
        if request.method == 'GET':
            results = book.fetch_notes(integer_id)
            if len(results) == 0:
                return jsonify({'code':integer_id, 'message':'Capital record not found'}), 404
            print type(results[0])
            return jsonify(results[0]), 200
        elif request.method == 'PUT':
            print json.dumps(request.get_json())
            request_json = request.get_json()
            book.store_note(request_json, integer_id)
            return "", 200
        elif request.method == 'DELETE':
            return book.delete_notes(integer_id)
    except Exception as e:
         return server_error(e)


@app.route('/api/capitals', methods=['GET'])
def fetch_all():
    """inserts and retrieves notes from datastore"""
    if request.method == 'GET':
        return get_all_capitals()

def get_all_capitals():
    query = request.args.get('query')
    if query is not None:
        print 'GET-query request received'
        query_attr, query_value = query.split(":")
        print 'query_attr:', query_attr, ', query_value:', query_value
        return query_capitals(query_attr, query_value)
        
    search = request.args.get('search')
    if search is not None:
        print 'GET-search request received'
        search_value = search
        print 'search_value:', search_value
        return search_capitals(search_value)

    qstr = request.query_string    
    if qstr is None or len(qstr) == 0:
        print 'GET request received: '
        book = notebook.NoteBook()
        results = book.fetch_all()
        return jsonify(results)

    print '*** unexpected GET request received: ', qstr
    return error(404, 'Unexpected error')

def query_capitals(attr, value):
    book = notebook.NoteBook()
    if attr == "location.latitude" or attr == "location.longitude":
        results = book.fetch_notes_by_attribute(attr, float(value))
        return jsonify(results)
    if attr == "id" or attr == "country" or attr == "name" or attr == "countryCode" or attr == "continent":
        results = book.fetch_notes_by_attribute(attr, value)
        return jsonify(results)
    else:
        return error(404, 'Invalid attriute name: ' + attr)

def search_capitals(search_value):
    book = notebook.NoteBook()
    results = book.fetch_notes_any_attribute(search_value)
    return jsonify(results)
    #return jsonify({'code':404, 'message':'Not implemented'})

@app.route('/api/status', methods=['GET'])
def get_status():
    """check the status of datastore and return True/False"""

    response = {'insert':True, 'fetch':True, 'delete':True, 'list':True, 'query':True, 'search':True, 'pubsub':True, 'storage':True}
    return jsonify(response), 200


@app.route('/api/capitals/<id>/store', methods=['POST'])
def fetch_and_store_in_bucket(id=-1):
    """retrieves notes from datastore and store in bucket"""

    book = notebook.NoteBook()
    try:
        results = book.fetch_notes(id)
        if len(results) == 0:
            return jsonify({'code':str(id), 'message':'Capital record not found'}), 404
        body = request.get_json()
        bucket_name = body[u'bucket']
        print "results", results[0]
        j_result = json.dumps(results[0], ensure_ascii=True)
        print "dump", j_result
        store_to_gcs = gcs.store_file_to_gcs(str(bucket_name), str(id), str(j_result))
        if store_to_gcs:
            return "", 200
        else:
            return jsonify({'code':str(id), 'message':'Bucket not found'}), 404
    except:
        return 500


@app.route('/api/capitals/<id>/publish', methods=['POST'])
def publish(id=-1):
    try:
        book = notebook.NoteBook()
        results = book.fetch_notes(id)
        if len(results) == 0:
            return jsonify({'code':str(id), 'message':'Capital not found'}), 404

        body = request.get_json()
        topic_name = body[u'topic']
        print "topic name", str(topic_name)
        j_result = json.dumps(results[0], ensure_ascii=True)
        print "dump", j_result
        data = str(j_result).encode('utf-8')

        a, project_name, c, topic_name_from_body = str(topic_name).split("/")
        client = pubsub.Client(project_name, None, None, None)
        print "pubsub client", client

        topic = client.topic(topic_name_from_body)
        topic.publish(data)
        return jsonify({'messageId':str(id)}), 200
    except Exception as e:
        server_error(e)


@app.errorhandler(500)
def server_error(err):
    """Error handler"""
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(err), 500

def error(code, message):
    return jsonify({'code':int(code), 'message':str(message)})

def convert_keys_to_string(dictionary):
    """Recursively converts dictionary keys to strings."""
    if not isinstance(dictionary, dict):
        return dictionary
    return dict((str(k), convert_keys_to_string(v))
        for k, v in dictionary.items())

if __name__ == '__main__':
    # Used for running locally
    app.run(host='127.0.0.1', port=8080, debug=True)
