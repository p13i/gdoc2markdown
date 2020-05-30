import yaml
import sys
import os
from .markdown import MarkdownDocument, MarkdownImage, MarkdownHeader
import requests


class JekyllTOCNode:
    def __init__(self, header: MarkdownHeader):
        self.header = header
        self.children = []

    def to_dict(self):
        d = {}
        d['text'] = self.header.text
        d['id'] = self.header.id_
        d['children'] = []

        for child in self.children:  # type: JekyllTOCNode
            d['children'].append(child.to_dict())

        return d


class JekyllWriteOptions:
    def __init__(self, base_dir, markdown_file_path, images_folder_path=None):
        self.base_dir = base_dir
        self.markdown_file_path = markdown_file_path
        self.images_folder_path = images_folder_path


class JekyllMarkdownDocument:
    def __init__(self, front_matter: dict, markdown_document: MarkdownDocument):
        self.front_matter = front_matter
        self.markdown_document = markdown_document

    def __str__(self):
        front_matter_s = yaml.dump(self.front_matter, width=sys.maxsize)
        markdown_document_s = str(self.markdown_document)
        return f'---\n{front_matter_s}---\n\n{markdown_document_s}'

    def _write_images(self, base_dir, images_folder_path, images_written=0, iterator=None):
        if not iterator:
            iterator = iter(self.markdown_document)

        for element in iterator:
            if hasattr(element, '__iter__'):
                child_elements = list(element)
                if child_elements:
                    self._write_images(base_dir, images_folder_path, images_written, child_elements)
            elif isinstance(element, MarkdownImage):

                response = requests.get(element.src)
                content_type = response.headers.get('Content-Type')
                type_, extension = content_type.split('/')

                if type_ != 'image':
                    continue

                image_path = f'{images_folder_path}/image{images_written}.{extension}'
                full_image_path = f'{base_dir}{os.path.sep}{image_path}'

                os.makedirs(os.path.dirname(image_path), exist_ok=True)

                with open(full_image_path, mode='wb') as f:
                    bytes_written = f.write(response.content)

                element.src = image_path

                print(f'> Wrote image with {bytes_written} bytes to {full_image_path}')

                images_written += 1

    def write(self, options: JekyllWriteOptions):
        if options.images_folder_path:
            self._write_images(options.base_dir, options.images_folder_path)

        full_markdown_path = os.path.join(options.base_dir, options.markdown_file_path)
        with open(full_markdown_path, mode='wb') as f:
            return f.write(str(self).encode('utf-8'))

