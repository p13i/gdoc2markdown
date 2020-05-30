import os
import pickle
import sys

import yaml
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from gdoc2markdown.transformers.google_doc_to_jekyll import transform as gdoc2jekyll
from gdoc2markdown.models.jekyll import JekyllWriteOptions

GOOGLE_APIS_SCOPES = ['https://www.googleapis.com/auth/docs.readonly']


def get_drive_service(service, version, credentials_path):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, GOOGLE_APIS_SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build(service, version, credentials=creds)

    return service


def get_document_tree(google_doc_id):
    service = get_drive_service('docs', 'v1', 'credentials.json')
    return service.documents().get(documentId=google_doc_id).execute()


def main():
    if len(sys.argv) != 2:
        return print(help('main'))

    posts_yml = sys.argv[1]

    print(f'Reading configuration from {posts_yml}')

    with open(posts_yml) as f:
        posts = yaml.load(f, Loader=yaml.FullLoader)

    base_dir = os.path.dirname(posts_yml)

    print(f'Assuming Jekyll site base path {base_dir}\n')

    for post in posts:
        id_ = post['source']['id']

        print(f'Query Google Docs API for document with ID {id_}')

        tree = get_document_tree(id_)

        jekyll_document = gdoc2jekyll(tree, extra_front_matter={'layout': 'posts/post'})

        output_markdown_path = post['output']['markdown']['file_path']
        output_images_folder = post['output']['images']['site_path']

        bytes_written = jekyll_document.write(options=JekyllWriteOptions(
            base_dir=base_dir,
            markdown_file_path=output_markdown_path,
            images_folder_path=output_images_folder,
        ))

        print(f'Wrote {bytes_written} bytes to {output_markdown_path}\n')

    print('Done.')


if __name__ == '__main__':
    main()
