#!/usr/bin/python2
__author__ = 'ashish'

import yaml
from xml.etree import ElementTree as et
import argparse
import xml.sax.saxutils as saxutils
from BeautifulSoup import BeautifulSoup


# returns an ElementTree element
def parse_slide(slide, conf):
    add_notes = True
    et_slide = et.Element('section')

    if 'children' in slide and len(slide['children']) > 0:
        for child_slide in slide['children']:
            # If a slide is empty then don't append that
            non_null_node_append(et_slide, parse_slide(child_slide, conf))
    else:
        if 'type' in slide:
            type = slide['type']
        else:
            type = 'text'

        if type == 'text':
            title_append(et_slide, slide, conf['title'])
            if 'content' in slide:
                content = slide['content']
                section = et.Element(conf['content'])
                section.text = content
                non_null_node_append(et_slide, section)
        elif type == 'md' or type == 'markdown':
            if 'content' in slide:
                content = slide['content']
                section = et.Element('section', {'data-markdown': ''})
                script = et.Element('script', {'type': 'text/template'})
                script.text = content
                non_null_node_append(section, script)
                non_null_node_append(et_slide, section)
        elif type == 'code':
            title_append(et_slide, slide, conf['title'])
            if 'content' in slide and slide['content'] != '':
                pre_node = et.Element('pre')
                code_node = et.Element('code', {'data-trim': ''})
                code_node.text = slide['content']
                non_null_node_append(pre_node, code_node)
                non_null_node_append(et_slide, pre_node)
        elif type == 'file':
            horiz_sep = '^\\n\\n\\n'
            vert_sep = '^\\n\\n'
            notes = '^Note:'
            charset = 'utf-8'

            if 'separator' in slide:
                if 'horizontal' in slide['separator']:
                    horiz_sep = slide['separator']['horizontal']
                if 'vertical' in slide['separator']:
                    vert_sep = slide['separator']['vertical']
            if 'notes' in slide:
                notes = slide['notes']
            if 'charset' in slide:
                charset = slide['charset']

            if 'filename' in slide and slide['filename'] is not None:
                et_slide.attrib['data-markdown'] = slide['filename']
                et_slide.attrib['data-separator'] = horiz_sep
                et_slide.attrib['data-separator-vertical'] = vert_sep
                et_slide.attrib['data-separator-notes'] = notes
                et_slide.attrib['data-charset'] = charset
                add_notes = False
        elif type == 'fragments':
            title_append(et_slide, slide, conf['title'])
            count = 1
            for fragment in slide['items']:
                p_node = et.Element('p', {'class': 'fragment', 'data-fragment-index': str(count)})
                p_node.text = fragment
                non_null_node_append(et_slide, p_node)
                count += 1
        elif type == 'ul' or type == 'ol':
            title_append(et_slide, slide, conf['title'])
            list_node = et.Element(type)
            if 'items' in slide:
                for item in slide['items']:
                    list_item = et.Element('li')
                    list_item.text = item
                    non_null_node_append(list_node, list_item)
            non_null_node_append(et_slide, list_node)
        elif type == 'div':
            title_append(et_slide, slide, conf['title'])
            list_node = et.Element(type)
            if 'items' in slide:
                for item in slide['items']:
                    list_item = et.Element('p')
                    list_item.text = item
                    non_null_node_append(list_node, list_item)
            non_null_node_append(et_slide, list_node)
        else:
            et_slide = None

        # it could be an empty slide
        # with just notes
        if 'notes' in slide and add_notes:
            notes = et.Element('aside', {'class': 'notes'})
            notes.text = slide['notes']
            non_null_node_append(et_slide, notes)

    return et_slide


def parse_slides(slides_yaml, conf):
    root = et.Element('div', {'class': 'slides'})
    non_null_node_append(root, generate_main_slide(slides_yaml['metadata'], conf['html']['main']))
    if 'slides' in slides_yaml and \
                    slides_yaml['slides'] is not None:
        if len(slides_yaml['slides']) > 0:
            for slide_yaml in slides_yaml['slides']:
                non_null_node_append(root, parse_slide(slide_yaml, conf['html']['slides']))
    non_null_node_append(root, generate_contact_slide(slides_yaml['metadata'], conf['html']['main']))
    return root


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = et.tostring(elem, 'utf-8')
    unescaped = saxutils.unescape(rough_string)
    soup = BeautifulSoup(unescaped)
    return unescaped


def generate_head_node(metadata):
    root = et.Element('head')

    if 'charset' in metadata:
        charset = metadata['charset']
    else:
        charset = 'utf-8'
    non_null_node_append(root, et.Element('meta', {'charset': charset}))

    if 'presentation' in metadata:
        title_node = et.Element('title')
        title_node.text = metadata['presentation']['title']
        non_null_node_append(root, title_node)
        non_null_node_append(root, et.Element('meta', {'name': 'description',
                                              'content': metadata['presentation']['description']}
        ))

    if 'author' in metadata and 'name' in metadata['author']:
        non_null_node_append(root, et.Element('meta', {'name': 'author',
                                              'content': metadata['author']['name']}))

    if 'mobile' in metadata:
        is_mobile = metadata['mobile']
    else:
        is_mobile = True
    if is_mobile:
        non_null_node_append(root, et.Element('meta', {'name': 'apple-mobile-web-app-capable', 'content': 'yes'}))
        non_null_node_append(root, et.Element('meta', {'name': 'apple-mobile-web-app-status-bar-style',
                                        'content': 'black-translucent'}))
        non_null_node_append(root, et.Element('meta', {'name': 'viewport',
                                        'content': 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, minimal-ui'}))

    # stylesheets
    non_null_node_append(root, get_stylesheet_node('css/reveal.css'))

    general_theme = 'night'
    code_theme = 'zenburn'
    if 'theme' in metadata:
        if 'general' in metadata['theme']:
            general_theme = metadata['theme']['general']
        if 'code' in metadata['theme']:
            code_theme = metadata['theme']['code']

    theme_elem = get_stylesheet_node('css/theme/' + general_theme + '.css')
    theme_elem.attrib['id'] = 'theme'
    non_null_node_append(root, theme_elem)
    non_null_node_append(root, get_stylesheet_node('lib/css/' + code_theme + '.css'))

    if 'custom' in metadata:
        if 'css' in metadata['custom'] and type(metadata['custom']['css']) == list:
            for css in metadata['custom']['css']:
                non_null_node_append(root, get_stylesheet_node(css))
        if 'js' in metadata['custom'] and type(metadata['custom']['js']) == list:
            for js in metadata['custom']['js']:
                non_null_node_append(root, get_script_node(js))

        if 'font' in metadata['custom']:
            style_node = et.Element('style')
            style_node.text = 'html * { font-family: \'' + metadata['custom']['font'] + '\', serif !important; }'
            non_null_node_append(root, style_node)

    if 'printable' in metadata:
        is_printable = metadata['printable']
    else:
        is_printable = True
    if is_printable:
        print_node = et.Element('script')
        print_node.text = '''var link = document.createElement( 'link' );
        link.rel = 'stylesheet';
        link.type = 'text/css';
        link.href = window.location.search.match( /print-pdf/gi ) ? '../css/print/pdf.css' : '../css/print/paper.css';
        document.getElementsByTagName( 'head' )[0].appendChild( link );'''
        non_null_node_append(root, print_node)

    fullscreen_node = et.Element('script')
    fullscreen_node.text = '''
        var fullscreen = false;
        // Find the right method, call on correct element
        function launchFullscreen(element) {
          if(element.requestFullscreen) {
            element.requestFullscreen();
          } else if(element.mozRequestFullScreen) {
            element.mozRequestFullScreen();
          } else if(element.webkitRequestFullscreen) {
            element.webkitRequestFullscreen();
          } else if(element.msRequestFullscreen) {
            element.msRequestFullscreen();
          }
        }

        // Exit fullscreen
        function exitFullscreen() {
          if(document.exitFullscreen) {
            document.exitFullscreen();
          } else if(document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
          } else if(document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
          }
        }

        function toggleFullScreen(){
            if(fullscreen == false)
            {
                launchFullscreen(document.documentElement); // the whole page
                fullscreen = true;
            }else{
                exitFullscreen();
                fullscreen = false;
            }
        }

    '''
    non_null_node_append(root, fullscreen_node)
    return root


def generate_body_node(slides_yaml, conf):
    root = et.Element('body')

    # parse slides
    slides_ctr = et.Element('div', {'class': 'reveal'})
    non_null_node_append(slides_ctr, parse_slides(slides_yaml, conf))
    non_null_node_append(root, slides_ctr)

    # include necessary script tags
    non_null_node_append(root, get_script_node('lib/js/head.min.js'))
    non_null_node_append(root, get_script_node('js/reveal.js'))

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
            { src: '../lib/js/classList.js', condition: function() { return !document.body.classList; } },
            { src: '../plugin/markdown/marked.js', condition: function() { return !!document.querySelector( '[data-markdown]' ); } },
            { src: '../plugin/markdown/markdown.js', condition: function() { return !!document.querySelector( '[data-markdown]' ); } },
            { src: '../plugin/highlight/highlight.js', async: true, condition: function() { return !!document.querySelector( 'pre code' ); }, callback: function() { hljs.initHighlightingOnLoad(); } },
            { src: '../plugin/zoom-js/zoom.js', async: true },
            { src: '../plugin/notes/notes.js', async: true },
            { src: '../plugin/remotes/remotes.js', async: true },
            { src: '../plugin/math/math.js', async: true }
        ]'''
    revealjs_post = '''
    });'''
    revealjs_fs = '''
    Reveal.configure({
        keyboard: {
            102: 'toggleFullScreen'
        }
    });
    '''
    script_node.text = revealjs_pre \
                       + dict_to_js_str(reveal_params) \
                       + revealjs_dependencies \
                       + revealjs_post \
                       + revealjs_fs
    non_null_node_append(root, script_node)

    return root


def generate_main_slide(slides_yaml, conf):
    root = et.Element('section')

    title = et.Element(conf['title'])
    title.text = slides_yaml['presentation']['title']

    desc = et.Element(conf['description'])
    desc.text = slides_yaml['presentation']['description']

    author = et.Element(conf['author'])
    author.text = slides_yaml['author']['name']

    non_null_node_append(root, title)
    non_null_node_append(root, desc)
    non_null_node_append(root, author)

    return root


def generate_contact_slide(slides_yaml, conf):
    root = et.Element('section')

    if 'name' in slides_yaml['author']:
        author = et.Element(conf['title'])
        author.text = slides_yaml['author']['name']
        non_null_node_append(root, author)

    if 'email' in slides_yaml['author']:
        email_ctr = et.Element(conf['author'])
        email_addr = slides_yaml['author']['email']
        email = et.Element('a', {'href': 'mailto:' + email_addr})
        email.text = email_addr
        non_null_node_append(email_ctr, email)
        non_null_node_append(root, email_ctr)

    if 'website' in slides_yaml['author']:
        website_ctr = et.Element(conf['author'])
        website = slides_yaml['author']['website']
        site_node = et.Element('a', {'href': website})
        site_node.text = website.replace('http://', '')
        non_null_node_append(website_ctr, site_node)
        non_null_node_append(root, website_ctr)

    return root


def title_append(et_slide, slide, title_tag):
    if 'title' in slide and slide['title'] != '':
        title = et.Element(title_tag)
        title.text = slide['title']
        non_null_node_append(et_slide, title)


def dict_to_js_str(dictionary):
    js_str = ''
    for key in dictionary.keys():
        js_str += key + ': '
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


def get_stylesheet_node(css_file):
    if css_file.startswith('http://') or css_file.startswith('https://'):
        prepend = ''
    else:
        prepend = '../'
    return et.Element('link', {'rel': 'stylesheet',
                               'href': prepend + css_file,
                               'type': 'text/css'})


def get_script_node(js):
    if js.startswith('http://') or js.startswith('https://'):
        prepend = ''
    else:
        prepend = '../'
    script_node = et.Element('script', {'type': 'text/javascript',
                                        'src': prepend + js})
    script_node.text = "// do nothing"
    return script_node


def generate_html(root_node):
    return '<!doctype html>\n' + prettify(root_node)


def parse_yaml(conf, slide_yaml):
    root_node = et.Element('html', {'lang': 'en'})
    head_node = generate_head_node(slide_yaml['metadata'])
    body_node = generate_body_node(slide_yaml, conf)
    non_null_node_append(root_node, head_node)
    non_null_node_append(root_node, body_node)
    return root_node


def main():
    parser = argparse.ArgumentParser('yaml_reveal', description='YAML to Reveal.js converter')
    parser.add_argument('-o', dest='output_filename', help='Output filename')
    parser.add_argument('filename', help='Input file')
    args = parser.parse_args()

    try:
        conf = yaml.load(open('parser_conf.yaml'))
    except IOError:
        conf = {'html':
                    {'slides': {'title': 'h2', 'content': 'p'},
                     'main': {
                        'title': 'h1',
                        'description': 'h3',
                        'author': 'div',
                        'social': '',
                        'fragment': 'p'
               }}}
    slide_yaml = yaml.load(open(args.filename))
    root_node = parse_yaml(conf, slide_yaml)

    # fileDom = et.ElementTree(root_node)
    # fileDom.write(open(args.output_filename, 'w+'))
    out = open(args.output_filename, 'w+')
    out.write(generate_html(root_node))


if __name__ == '__main__':
    main()
