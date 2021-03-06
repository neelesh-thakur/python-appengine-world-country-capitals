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
        #entity['timestamp'] = datetime.utcnow()

        return self.ds.put(entity), 200

    def fetch_notes_by_attribute(self, query_attr, query_value):
        id_filter = [(query_attr, '=', query_value)]
        query = self.ds.query(kind=self.kind, filters=id_filter)
        return self.get_query_results(query)

    def fetch_notes_any_attribute(self, search_value):
        if (search_value.isdigit()):
            print "fetch_notes_any_attribute - is digit"
            result = self.get_query_results(self.ds.query(kind=self.kind, filters=[('id', '=', int(search_value))]))
            return result

        result = self.get_query_results(self.ds.query(kind=self.kind, filters=[('country', '=', search_value)]))
        if len(result) > 0:
            return result

        result = self.get_query_results(self.ds.query(kind=self.kind, filters=[('name', '=', search_value)]))
        if len(result) > 0:
            return result

        result = self.get_query_results(self.ds.query(kind=self.kind, filters=[('countryCode', '=', search_value)]))
        if len(result) > 0:
            return result

        result = self.get_query_results(self.ds.query(kind=self.kind, filters=[('continent', '=', search_value)]))
        if len(result) > 0:
            return result

        return []

    

    def fetch_notes(self, id):
        id_filter = [('id', '=', int(id))]
        query = self.ds.query(kind=self.kind, filters=id_filter)
        return self.get_query_results(query)

    def fetch_all(self):
        query = self.ds.query(kind=self.kind)
        #query.order = ['-timestamp']
        return self.get_query_results(query)

    def fetch_all_unique(self):
        query = self.ds.query(kind=self.kind)
        query.distinct_on = ["id"]
        return self.get_query_results(query)


    ''''

    result_with_url = list()
        for entity in results

    def fetch_all_unique_by_id(self)
        results = list()
        results_dict = dict()
        count = 0
        for entity in list(book.fetch_all()):
        if not results_dict.__contains__(entity)
            results.append(entity)
            count = count + 1
            if count == 20:
            break
    '''

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
            return jsonify({'code':404, 'message':'Capital record not found'}), 404

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