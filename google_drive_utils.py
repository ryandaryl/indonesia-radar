from oauth2client.file import Storage
from apiclient.http import MediaFileUpload
from apiclient import discovery
import httplib2
import os


def upload_file(file_name, directory, parent_directory, mimetype):
    credential_path = 'drive-python-quickstart.json'
    with open(credential_path, 'w') as json_file:
        json_file.write(os.environ.get('GOOGLE_DRIVE_JSON_STRING'))
    store = Storage(credential_path)
    credentials = store.get()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    parent_id = service.files().list(
        q="name = '{}'".format(parent_directory),
        pageSize=1,
        fields="files(name, id, mimeType, parents)").execute()['files'][0]['id']
    id = service.files().list(
        q="name = '{directory}' and '{parent_id}' in parents".format(
            directory=directory,
            parent_id=parent_id),
        pageSize=1,
        fields="files(name, id, mimeType, parents)").execute()['files'][0]['id']
    service.files().create(**{
        'body': {
            'name': file_name,
            'mimeType': mimetype,
            'parents': [id]},
        'fields': 'id',
        'media_body': MediaFileUpload(
            file_name,
            mimetype=mimetype,
            resumable=True)}).execute()


if __name__ == '__main__':
    upload_file(
        file_name='west_java.png',
        directory='data',
        parent_directory='west-java',
        mimetype='image/png')