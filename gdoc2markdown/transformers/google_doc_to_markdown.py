import json

from ..models.markdown import *


class TransformerError(Exception):
    pass


def __assert(condition, locals_dict):
    if not condition:
        raise TransformerError(json.dumps(locals_dict, indent=4))


def __parse_tree(google_doc_tree: dict) -> (MarkdownDocument, [dict]):
    doc = MarkdownDocument()

    def _discard(elem):
        raise ValueError

    md_list = None

    def _read_paragraph(from_elements):
        md_paragraph = MarkdownParagraph()

        for element in from_elements:

            if 'textRun' in element:
                content = element['textRun']['content']

                if 'textStyle' in element['textRun'] and len(element['textRun']['textStyle']) > 0:
                    is_code = 'weightedFontFamily' in element['textRun']['textStyle'] and \
                              element['textRun']['textStyle']['weightedFontFamily']['fontFamily'] == 'Courier New'

                    is_link = 'link' in element['textRun']['textStyle']

                    if is_code and is_link:
                        url = element['textRun']['textStyle']['link']['url']
                        md_paragraph.add(MarkdownLink(MarkdownCode(content), url))
                        continue
                    elif is_code:
                        md_paragraph.add(MarkdownCode(content))
                        continue
                    elif is_link:
                        url = element['textRun']['textStyle']['link']['url']
                        md_paragraph.add(MarkdownLink(content, url))
                        continue

                if content != '\n' and len(content.strip()) > 0:
                    md_paragraph.add(MarkdownText(element['textRun']['content']))
                    continue

                if content.strip() == '':
                    continue

            if 'inlineObjectElement' in element:
                inline_object_id = element['inlineObjectElement']['inlineObjectId']

                content_uri = google_doc_tree['inlineObjects'] \
                    [inline_object_id] \
                    ['inlineObjectProperties'] \
                    ['embeddedObject'] \
                    ['imageProperties'] \
                    ['contentUri']

                md_paragraph.add(MarkdownImage(None, content_uri))
                continue

            if 'footnoteReference' in element:
                id_ = element['footnoteReference']['footnoteId']
                number = int(element['footnoteReference']['footnoteNumber'])
                md_paragraph.add(MarkdownFootnoteReference(id_, number))

                __assert(
                    len(google_doc_tree['footnotes'][id_]['content']) == 1,
                    locals())

                footnote_content = _read_paragraph(google_doc_tree['footnotes'][id_]['content'][0]['paragraph']['elements'])

                doc.add_footnote(MarkdownFootnote(id_, number, footnote_content))

                continue

            _discard(element)

        return md_paragraph

    def _clear_list():
        if md_list is not None:
            doc.add(md_list)
        return None

    for structural_element in google_doc_tree['body']['content']:
        if 'paragraph' in structural_element:

            paragraph = structural_element['paragraph']
            named_style_type = paragraph['paragraphStyle']['namedStyleType']
            elements = paragraph['elements']

            if 'HEADING_' in named_style_type:
                __assert(
                    len(elements) == 1
                    or elements[1]['textRun']['content'] == '\n',
                    locals())

                md_list = _clear_list()

                doc.add(MarkdownHeader(
                    depth=int(named_style_type[len('HEADING_'):]),
                    text=elements[0]['textRun']['content']))
                continue

            elif 'bullet' in paragraph:

                if md_list is None:
                    md_list = MarkdownList()

                md_para = _read_paragraph(elements)

                if md_para:
                    md_list.add(md_para)

                continue

            elif 'NORMAL_TEXT' in named_style_type:

                md_list = _clear_list()

                md_para = _read_paragraph(elements)

                if md_para:
                    doc.add(md_para)

                continue

            elif 'textRun' in structural_element and structural_element['textRun']['content'] == '\n':
                continue

        elif 'sectionBreak' in structural_element:
            # Unsupported
            continue

        _discard(structural_element)

    return doc


def transform(google_doc_tree: dict) -> MarkdownDocument:
    markdown_document = __parse_tree(google_doc_tree)
    return markdown_document
