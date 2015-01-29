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
            # If a slide is empty then don't append that
            non_null_node_append(et_slide, parse_slide(child_slide, conf))
    # elif 'fragments' in slide and len(slide['fragments']) > 0:
    #     pass
    else:
        if 'type' in slide:
            type = slide['type']
        else:
            type = 'text'

        if type == 'text':
            if 'title' in slide and slide['title'] != '':
                title = et.Element(conf['title'])
                title.text = slide['title']
                et_slide.append(title)
            if 'content' in slide:
                content = slide['content']
                section = et.Element(conf['content'])
                section.text = content
                et_slide.append(section)
        elif type == 'md' or type == 'markdown':
            if 'content' in slide:
                content = slide['content']
                section = et.Element('section', {'data-markdown': ''})
                script = et.Element('script', {'type': 'text/template'})
                script.text = content
                section.append(script)
                et_slide.append(section)
        elif type == 'code':
            if 'title' in slide and slide['title'] != '':
                title = et.Element(conf['title'])
                title.text = slide['title']
                et_slide.append(title)
        else:
            et_slide = None

        # it could be an empty slide
        # with just notes
        if 'notes' in slide:
            notes = et.Element('aside', {'class': 'notes'})
            notes.text = slide['notes']
            et_slide.append(notes)

    return et_slide


def parse_slides(slides_yaml, conf):
    root = et.Element('div', {'class': 'slides'})
    root.append(generate_main_slide(slides_yaml['metadata'], conf['html']['main']))
    if 'slides' in slides_yaml and\
                    slides_yaml['slides'] is not None:
        if len(slides_yaml['slides']) > 0:
            for slide_yaml in slides_yaml['slides']:
                root.append(parse_slide(slide_yaml, conf['html']['slides']))
    root.append(generate_contact_slide(slides_yaml['metadata'], conf['html']['main']))
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

    if 'author' in metadata and 'name' in metadata['author']:
        root.append(et.Element('meta', {'name': 'author',
                                        'content': metadata['author']['name']}))

    if 'mobile' in metadata:
        is_mobile = metadata['mobile']
    else:
        is_mobile = True
    if is_mobile:
        root.append(et.Element('meta', {'name': 'apple-mobile-web-app-capable', 'content': 'yes'}))
        root.append(et.Element('meta', {'name': 'apple-mobile-web-app-status-bar-style',
                                        'content': 'black-translucent'}))
        root.append(et.Element('meta', {'name': 'viewport',
                                        'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, minimal-ui'}))

    # stylesheets
    root.append(get_stylesheet('css/reveal.css'))

    general_theme = 'night'
    code_theme = 'zenburn'
    if 'theme' in metadata:
        if 'general' in metadata['theme']:
            general_theme = metadata['theme']['general']
        if 'code' in metadata['theme']:
            code_theme = metadata['theme']['code']

    theme_elem = get_stylesheet('css/theme/' + general_theme + '.css')
    theme_elem.attrib['id'] = 'theme'
    root.append(theme_elem)
    root.append(get_stylesheet('lib/css/' + code_theme + '.css'))

    if 'printable' in metadata:
        is_printable = metadata['printable']
    else:
        is_printable = True
    if is_printable:
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
    slides_ctr.append(parse_slides(slides_yaml, conf))
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

    # reveal.js initialization
    script_node = et.Element('script', {'type': 'text/javascript'})
    reveal_params = {'controls': 'true', 'progress': 'true', 'history': 'true',
                     'center': 'true', 'transition': 'convex', 'touch': 'true'}
    if 'reveal' in slides_yaml['metadata']:
        overlay_dict_on(slides_yaml['metadata']['reveal'], reveal_params)
    revealjs_pre = '''  // Full list of configuration options available at:
    // https://github.com/hakimel/reveal.js#configuration
    Reveal.initialize({'''
    revealjs_dependencies = '''// Optional reveal.js plugins
        dependencies: [
            { src: 'lib/js/classList.js', condition: function() { return !document.body.classList; } },
            { src: 'plugin/markdown/marked.js', condition: function() { return !!document.querySelector( '[data-markdown]' ); } },
            { src: 'plugin/markdown/markdown.js', condition: function() { return !!document.querySelector( '[data-markdown]' ); } },
            { src: 'plugin/highlight/highlight.js', async: true, condition: function() { return !!document.querySelector( 'pre code' ); }, callback: function() { hljs.initHighlightingOnLoad(); } },
            { src: 'plugin/zoom-js/zoom.js', async: true },
            { src: 'plugin/notes/notes.js', async: true },
            { src: 'plugin/remotes/remotes.js', async: true },
            { src: 'plugin/math/math.js', async: true }
        ]'''
    revealjs_post = '''
    });'''
    script_node.text = revealjs_pre\
                       + dict_to_js_str(reveal_params)\
                       + revealjs_dependencies\
                       + revealjs_post
    root.append(script_node)

    return root


def generate_main_slide(slides_yaml, conf):
    root = et.Element('section')

    title = et.Element(conf['title'])
    title.text = slides_yaml['presentation']['title']

    desc = et.Element(conf['description'])
    desc.text = slides_yaml['presentation']['description']

    author = et.Element(conf['author'])
    author.text = slides_yaml['author']['name']

    root.append(title)
    root.append(desc)
    root.append(author)

    return root


def generate_contact_slide(slides_yaml, conf):
    root = et.Element('section')

    author = et.Element(conf['title'])
    author.text = slides_yaml['author']['name']

    email_addr = slides_yaml['author']['email']
    email = et.Element('a', {'href': 'mailto:' + email_addr})
    email.text = email_addr

    root.append(author)
    root.append(email)

    return root


def dict_to_js_str(dictionary):
    js_str = ''
    for key in dictionary.keys():
        js_str += key+': '
        value = dictionary[key].lower()
        if value == 'true' or value == 'false':
            js_str += value
        else:
            js_str += '\'' + value + '\''
        js_str += ',\n\t'
    return js_str


def non_null_node_append(src_node, tgt_node):
    if tgt_node is not None:
        src_node.append(tgt_node)


def overlay_dict_on(src_dict, tgt_dict):
    for key in src_dict.keys():
        tgt_dict[key] = src_dict[key]


def get_stylesheet(css_file):
    return et.Element('link', {'rel': 'stylesheet',
                      'href': css_file})


def generate_html(root_node):
    return '<!doctype html>\n' + prettify(root_node)


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
    out.write(generate_html(root_node))


if __name__ == '__main__':
    main()