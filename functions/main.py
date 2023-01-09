from google.cloud import storage
from google.cloud.storage import Blob
        
def hello_gcs(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    file = event
    file_name = file['name']
    video = file_name.endswith('.mp4')
    image = file_name.endswith('.jpg')
    print(f"Processing file: {file['name']}.")
    storage_client = storage.Client(project='YOUR_PROJECT_ID')
    source_bucket = storage_client.get_bucket('YOUR_GCS_UPLOAD_BUCKET')
    destination_bucket_videos = storage_client.get_bucket('YOUR_GCS_VIDEO_TRANSFER_BUCKET')
    destination_bucket_images = storage_client.get_bucket('YOUR_GCS_IMAGES_TRANSFER_BUCKET')
    blobs=list(source_bucket.list_blobs(prefix=''))
    blobs=list
    print(blobs)
    storage_client = storage.Client(project='YOUR_PROJECT_ID')
    source_bucket = storage_client.get_bucket('YOUR_GCS_UPLOAD_BUCKET')
    destination_bucket_videos = storage_client.get_bucket('YOUR_GCS_VIDEO_TRANSFER_BUCKET')
    destination_bucket_images = storage_client.get_bucket('YOUR_GCS_IMAGES_TRANSFER_BUCKET')
    blobs=list(source_bucket.list_blobs(prefix=''))
    print(blobs)
    for blob in blobs:
     if blob.size < 35000000 and video == True and blob.name == file_name:
      print("Size of blob is "+ str(blob.size))
      source_blob = source_bucket.blob(blob.name)
      new_blob = source_bucket.copy_blob(
      source_blob, destination_bucket_videos, blob.name)
      print(f'File moved from {source_blob} to {new_blob}')
     elif blob.size < 35000000 and image == True and blob.name == file_name:
      print("Size of blob is "+ str(blob.size))
      source_blob = source_bucket.blob(blob.name)
      new_blob = source_bucket.copy_blob(
      source_blob, destination_bucket_images, blob.name)
      print(f'File moved from {source_blob} to {new_blob}')
     else:
      print("File size is greater 35MB")
