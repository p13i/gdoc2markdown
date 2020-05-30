from typing import Dict, Tuple, Union, List

from .google_doc_to_markdown import transform as gdoc2markdown
from ..models.jekyll import JekyllMarkdownDocument
from ..models.markdown import *


def __parse_front_matter(md_document: MarkdownDocument) -> Tuple[MarkdownDocument, Dict[str, Union[str, List[str]]]]:
    def _parse_error():
        raise Exception

    reading_front_matter = False
    front_matter_elements = []

    front_matter = {}

    reading_tags = False

    def _tagify(string: str):
        string = string.replace(' ', '-')
        return string.lower()

    def _track_front_matter_elem(elem):
        front_matter_elements.append(elem)

    for i, elem in enumerate(md_document.elements):

        if i == 0:
            if isinstance(elem, MarkdownHeader):
                front_matter['title'] = elem.text
                _track_front_matter_elem(elem)
                continue

            _parse_error()

        if isinstance(elem, MarkdownParagraph):
            if len(elem.elements) > 0:

                if isinstance(elem.elements[0], MarkdownText) and \
                        elem.elements[0].text == '~':

                    if not reading_front_matter:
                        reading_front_matter = True
                    else:
                        _track_front_matter_elem(elem)
                        reading_front_matter = reading_tags = False
                        break

        if reading_front_matter:
            _track_front_matter_elem(elem)

            if isinstance(elem, MarkdownParagraph):
                text = str(elem)

                if text.startswith('Author: '):
                    author = text[len('Author: '):]
                    front_matter['author'] = author
                elif text.startswith('Description: '):
                    description = text[len('Description: '):]
                    front_matter['description'] = description
                elif text.startswith('Tags:'):
                    reading_tags = True

            elif isinstance(elem, MarkdownList):
                if reading_tags:
                    front_matter['tags'] = [_tagify(str(item)) for item in elem]

    # Remove all elements from the front matter
    for elem in front_matter_elements:
        md_document.elements.remove(elem)

    return md_document, front_matter


def transform(google_doc_tree: dict, extra_front_matter: dict = None) -> JekyllMarkdownDocument:
    markdown_document: MarkdownDocument = gdoc2markdown(google_doc_tree)
    markdown_document, front_matter = __parse_front_matter(markdown_document)

    if extra_front_matter:
        front_matter.update(extra_front_matter)

    return JekyllMarkdownDocument(
        front_matter=front_matter,
        markdown_document=markdown_document,
    )
