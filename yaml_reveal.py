__author__ = 'ashah'

import yaml
from xml.etree import ElementTree as et
import argparse
import xml.dom.minidom as minidom


# returns an ElementTree element
def parse_slide(slide, conf):
    et_slide = et.Element('section')

    if 'title' in slide:
        title = et.Element(conf['html']['title'])
        title.text = slide['title']
        et_slide.append(title)

    if 'content' in slide:
        content = slide['content']

        if 'type' in slide:
            type = slide['type']
        else:
            type = 'text'

        if type == 'text':
            section = et.Element('div')
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

    if 'children' in slide:
        for child_slide in slide['children']:
            et_slide.append(parse_slide(child_slide, conf))

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
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")


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
    return parse_slides(slides_yaml['slides'], conf)


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