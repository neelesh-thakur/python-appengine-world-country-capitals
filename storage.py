from google.cloud import storage, exceptions
from google.cloud.storage import Blob

class Storage:

    def __init__(self):
        self.gcs = storage.Client(project="hackathon-team-010")

    def check_bucket(self, bucket_name):
        try:
            print "check_bucket"
            self.gcs.get_bucket(bucket_name)
            return True
        except exceptions.NotFound:
            print ('Error: Bucket {} does not exists.'.format(bucket_name))
            return False
        except exceptions.BadRequest:
            print ('Error: Invalid bucket name {}'.format(bucket_name))
            return None
        except exceptions.Forbidden:
            print ('Error: Forbidden, Access denied for bucket {}'.format(bucket_name))
            return None

    def create_bucket(self, bucket_name):
        bucket_exists = self.check_bucket(bucket_name)

        if bucket_exists is not None and not bucket_exists:
            try:
                print ('creating bucket {}'.format(bucket_name))
                self.gcs.create_bucket(bucket_name)
                return True
            except Exception as e:
                print "Error: Create bucket Exception"
                print e
                return None
        return bucket_exists

    def store_file_to_gcs(self, bucket_name, filename, content):

        if self.check_bucket(bucket_name):
            try:
                print "content: ", content
                print "inside store_file_to_gcs"
                bucket = self.gcs.get_bucket(bucket_name)
                print bucket
                blob = Blob(filename, bucket)
                print "blob", blob
                blob.upload_from_string(content, content_type='application/json')
                print "upload successful"
                return True
            except IOError as e:
                print e
                #print ('Error: Cannot find the file {}'.format(filename))
        return False

    def fetch_object_from_gcs(self, bucket_name, fileobject):

        if self.check_bucket(bucket_name):
            bucket = self.gcs.get_bucket(bucket_name)
            blob = Blob(fileobject, bucket)
            outfile = fileobject + ".out"

            try:
                with open(outfile, 'wb') as output_file:
                    blob.download_to_file(output_file)
                return True
            except IOError:
                print ('Error: Cannot find the object {}'.format(fileobject))

        return False

    def list_objects(self, bucket_name):

        if self.check_bucket(bucket_name):
            bucket = self.gcs.get_bucket(bucket_name)
            print "Object in bucket " + bucket_name
            for blob in list(bucket.list_blobs()):
                print blob.name


