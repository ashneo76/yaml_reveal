__author__ = 'ashah'

import yaml
from xml.etree import ElementTree as et
import argparse
import xml.sax.saxutils as saxutils
from BeautifulSoup import BeautifulSoup


# returns an ElementTree element
def parse_slide(slide, conf):
    et_slide = et.Element('section')

    if 'children' in slide and len(slide['children']) > 0:
        for child_slide in slide['children']:
            et_slide.append(parse_slide(child_slide, conf))
    else:
        if 'title' in slide and slide['title'] != '':
            title = et.Element(conf['title'])
            title.text = slide['title']
            et_slide.append(title)

        if 'content' in slide:
            content = slide['content']

            if 'type' in slide:
                type = slide['type']
            else:
                type = 'text'

            if type == 'text':
                section = et.Element(conf['content'])
                section.text = content
                et_slide.append(section)
            elif type == 'md' or type == 'markdown':
                section = et.Element('section', {'data-markdown': ''})
                script = et.Element('script', {'type': 'text/template'})
                script.text = content
                section.append(script)
                et_slide.append(section)
            elif type == 'code':
                pass

        if 'notes' in slide:
            notes = et.Element('aside', {'class': 'notes'})
            notes.text = slide['notes']
            et_slide.append(notes)

    return et_slide


def parse_slides(slides_yaml, conf):
    root = et.Element('div', {'class': 'slides'})
    for slide_yaml in slides_yaml:
        root.append(parse_slide(slide_yaml, conf))
    return root


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = et.tostring(elem, 'utf-8')
    unescaped = saxutils.unescape(rough_string)
    soup = BeautifulSoup(unescaped)
    return unescaped


def generate_head_node(metadata, conf):
    root = et.Element('head')

    if 'charset' in metadata:
        charset = metadata['charset']
    else:
        charset = 'utf-8'
    root.append(et.Element('meta', {'charset': charset}))

    if 'presentation' in metadata:
        title_node = et.Element('title')
        title_node.text = metadata['presentation']['title']
        root.append(title_node)
        root.append(et.Element('meta', {'name': 'description',
                                        'content': metadata['presentation']['description']}
        ))

    if 'author' in metadata:
        root.append(et.Element('meta', {'name': 'author',
                                        'content': metadata['author']['name']}))

    if 'mobile' in metadata and metadata['mobile']:
        root.append(et.Element('meta', {'name': 'apple-mobile-web-app-capable', 'content': 'yes'}))
        root.append(et.Element('meta', {'name': 'apple-mobile-web-app-status-bar-style',
                                        'content': 'black-translucent'}))
        root.append(et.Element('meta', {'name': 'viewport',
                                        'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, minimal-ui'}))

    # stylesheets
    root.append(et.Element('link', {'rel': 'stylesheet',
                                    'href': 'css/reveal.css'}))
    if 'theme' in metadata:
        if 'general' in metadata['theme']:
            general_theme = metadata['theme']['general']
        else:
            general_theme = 'black'
        root.append(et.Element('link', {'rel': 'stylesheet',
                                        'id': 'theme',
                                        'href': 'css/theme/' + general_theme + '.css'}))

        if 'code' in metadata['theme']:
            code_theme = metadata['theme']['code']
        else:
            code_theme = 'zenburn'
        root.append(et.Element('link', {'rel': 'stylesheet',
                                        'href': 'lib/css/' + code_theme + '.css'}))

    if 'printable' in metadata and metadata['printable']:
        print_node = et.Element('script')
        print_node.text = '''var link = document.createElement( 'link' );
        link.rel = 'stylesheet';
        link.type = 'text/css';
        link.href = window.location.search.match( /print-pdf/gi ) ? 'css/print/pdf.css' : 'css/print/paper.css';
        document.getElementsByTagName( 'head' )[0].appendChild( link );'''
        root.append(print_node)

    return root


def generate_body_node(slides_yaml, conf):
    root = et.Element('body')

    # parse slides
    slides_ctr = et.Element('div', {'class': 'reveal'})
    slides_ctr.append(parse_slides(slides_yaml['slides'], conf['html']['slides']))
    root.append(slides_ctr)

    # include necessary script tags
    script_node = et.Element('script', {'type': 'text/javascript',
                                        'src': 'lib/js/head.min.js'})
    script_node.text = "// do nothing"
    root.append(script_node)

    script_node = et.Element('script', {'type': 'text/javascript',
                                        'src': 'js/reveal.js'})
    script_node.text = "// do nothing"
    root.append(script_node)

    script_node = et.Element('script', {'type': 'text/javascript'})
    script_node.text = '''  // Full list of configuration options available at:
    // https://github.com/hakimel/reveal.js#configuration
    Reveal.initialize({
        controls: true,
        progress: true,
        history: true,
        center: true,

        transition: 'slide', // none/fade/slide/convex/concave/zoom

        // Optional reveal.js plugins
        dependencies: [
            { src: 'lib/js/classList.js', condition: function() { return !document.body.classList; } },
            { src: 'plugin/markdown/marked.js', condition: function() { return !!document.querySelector( '[data-markdown]' ); } },
            { src: 'plugin/markdown/markdown.js', condition: function() { return !!document.querySelector( '[data-markdown]' ); } },
            { src: 'plugin/highlight/highlight.js', async: true, condition: function() { return !!document.querySelector( 'pre code' ); }, callback: function() { hljs.initHighlightingOnLoad(); } },
            { src: 'plugin/zoom-js/zoom.js', async: true },
            { src: 'plugin/notes/notes.js', async: true }
        ]
    });'''
    root.append(script_node)

    return root


def generate_main_slide(slides_yaml, conf):
    pass


def generate_contact_slide(slides_yaml, conf):
    pass


def main():
    parser = argparse.ArgumentParser('yaml_reveal', description='YAML to Reveal.js converter')
    parser.add_argument('-o', dest='output_filename', help='Output filename')
    parser.add_argument('filename', help='Input file')
    args = parser.parse_args()

    conf = yaml.load(open('parser_conf.yaml'))
    slide_yaml = yaml.load(open(args.filename))

    root_node = et.Element('html', {'lang': 'en'})
    head_node = generate_head_node(slide_yaml['metadata'], conf)
    body_node = generate_body_node(slide_yaml, conf)
    root_node.append(head_node)
    root_node.append(body_node)

    # fileDom = et.ElementTree(root_node)
    # fileDom.write(open(args.output_filename, 'w+'))
    out = open(args.output_filename, 'w+')
    out.write(prettify(root_node))


if __name__ == '__main__':
    main()