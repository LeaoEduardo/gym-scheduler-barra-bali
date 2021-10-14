import sys

from google.cloud import storage

from src import BUCKET_NAME

class CloudManager:

    def __init__(self):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(BUCKET_NAME)

    def upload(self,source_file_name='/app/schedule.json',destination_blob_name='schedule.json'):
        """Uploads a file to the bucket."""
        # The path to your file to upload
        # source_file_name = "local/path/to/file"
        # The ID of your GCS object
        # destination_blob_name = "storage-object-name"

        blob = self.bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        print(
            "File {} uploaded to {}.".format(
                source_file_name, destination_blob_name
            )
        )

    def download(self, source_blob_name='schedule.json', destination_file_name='/app/schedule.json'):
        """Downloads a blob from the bucket."""
        # The ID of your GCS object
        # source_blob_name = "storage-object-name"

        # The path to which the file should be downloaded
        # destination_file_name = "local/path/to/file"

        blob = self.bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)

        print(
            "Downloaded storage object {} from bucket {} to local file {}.".format(
                source_blob_name, BUCKET_NAME, destination_file_name
            )
        )