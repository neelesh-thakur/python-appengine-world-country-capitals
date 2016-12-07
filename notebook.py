from datetime import datetime
from google.cloud import datastore

import utility

from flask import jsonify

class NoteBook:

    def __init__(self):
        self.ds = datastore.Client(project=utility.project_id())
        self.kind = "Country"
       
    def store_note(self, request_json, id):
        key = self.ds.key(self.kind)
        entity = datastore.Entity(key)
        entity['id'] = request_json['id']
        entity['country'] = request_json['country']
        entity['name'] = request_json['name']
        entity['location'] = datastore.Entity(key=self.ds.key('EmbeddedKind'))
        entity['location']['latitude'] = request_json['location']['latitude']
        entity['location']['longitude'] = request_json['location']['longitude']
        entity['countryCode'] = request_json['countryCode']
        entity['continent'] = request_json['continent']
        entity['timestamp'] = datetime.utcnow()

        return self.ds.put(entity), 200

    def fetch_notes(self, id):
        id_filter = [('id', '=', int(id))]
        query = self.ds.query(kind=self.kind, filters=id_filter)
        return self.get_query_results(query)

    def fetch_all(self):
        query = self.ds.query(kind=self.kind)
        query.order = ['-timestamp']
        return self.get_query_results(query)

    def get_query_results(self, query):
        results = list()
        for entity in list(query.fetch()):
            results.append(dict(entity))
        return results
    
    def delete_notes(self, id):
        id_filter = [('id', '=', int(id))]
        query = self.ds.query(kind=self.kind, filters=id_filter)
        results = list()
        for entity in list(query.fetch()):
            results.append(entity)
        if len(results) == 0: 
            return jsonify({'id':str(id), 'message':'Not found'}), 404

        print type(results[0]), str(results[0]), len(results)
        for e in results:
            self.ds.delete(e.key)
        return '', 200
        

def parse_note_time(note):
    """converts a greeting to an object"""
    return {
        'text': note['text'],
        'timestamp': note['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    }
