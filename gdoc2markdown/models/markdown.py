
class MarkdownDocument:
    def __init__(self):
        self.elements = []
        self.footnotes = []

    def add(self, other):
        self.elements.append(other)

    def add_footnote(self, footnote):
        self.footnotes.append(footnote)

    def __str__(self):
        s = '\n'.join(str(elem) for elem in self.elements)
        s += '\n\n---\n\n'
        s += '\n'.join(str(ft) for ft in self.footnotes)
        return s

    def __iter__(self):
        return iter(self.elements + self.footnotes)

    def get_headers(self):
        for elem in self:
            if isinstance(elem, MarkdownHeader):
                yield elem

class MarkdownElement:
    def __str__(self):
        raise NotImplementedError


class MarkdownParagraph(MarkdownElement):
    def __init__(self):
        self.elements = []

    def add(self, other):
        self.elements.append(other)

    def __str__(self):
        return ''.join(str(elem) for elem in self.elements)

    def __iter__(self):
        return iter(self.elements)


class MarkdownList(MarkdownElement):
    def __init__(self):
        self.items: [MarkdownElement] = []

    def add(self, elem: MarkdownElement):
        self.items.append(elem)

    def __str__(self):
        s = ''
        for i, item in enumerate(self.items):
            s += f'* {str(item)}'

            if i < len(self.items) - 1:
                s += '\n'

        return s

    def __iter__(self):
        return iter(self.items)


class MarkdownText(MarkdownElement):
    def __init__(self, text):
        if text.endswith('\n'):
            text = text[:-1]

        self.text = text

    def __str__(self):
        return self.text


class MarkdownHeader(MarkdownElement):
    def __init__(self, depth: int, text: str, id_: str = None):

        if text.endswith('\n'):
            text = text[:-1]

        self.depth = depth
        self.text = text
        self.id_ = id_

    def __str__(self):
        s = '#' * self.depth + ' ' + self.text
        if self.id_:
            s += ' {#' + self.id_ + '}'
        return s


class MarkdownCode(MarkdownElement):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return f'`{self.code}`'


class MarkdownLink(MarkdownElement):
    def __init__(self, title, url):
        self.title = title
        self.url = url

    def __str__(self):
        return f'[{self.title}]({self.url})'


class MarkdownImage(MarkdownElement):
    def __init__(self, alt_text, src):
        self.alt_text = alt_text
        self.src = src

    def __str__(self):
        return f'![{self.alt_text}]({self.src})'


class MarkdownFootnoteReference(MarkdownElement):
    def __init__(self, id_, number):
        self.id_ = id_
        self.number = number

    def __str__(self):
        return f'[^footnote-{self.number}]'


class MarkdownFootnote(MarkdownElement):
    def __init__(self, id_, number, content):
        self.id_ = id_
        self.number = number
        self.content = content

    def __str__(self):
        return f'[^footnote-{self.number}]: {self.content}'
