## Usage
* Tested with python 3
* The command line is helpful to provide information about all the accepted parameters
* `./yaml_reveal.py -o <outputfile.htm> <inputfile>`

## Metadata configuration

### Required section
```yaml
metadata:
  author:
    name: "Ashish Shah"
    email: "ashneo76@gmail.com"
  presentation:
    title: "Presentation Title"
    description: "Presentation Decsripton"
```

### Example with filled in defaults

```yaml
metadata:
  author:
    name: "Ashish Shah"
    email: "ashneo76@gmail.com"
    social:
      - link: "http://"
        name: Website
      - link: "http://twitter.com/"
        name: "@twitterHandle"
  presentation:
    title: "Presentation Title"
    description: "Presentation Decsripton"
  theme:
    general: 'night'
    code: 'zenburn'
  printable: true
  mobile: true
  reveal:
    transition: convex
```

### Reveal.js configuration

|Parameter|Value|Options|
|:-----|:----|:---|
|controls|true|Default Value: `true`|
|progress|true|Default Value: `true`|
|slideNumber|false||
|history|false|Default Value: `true`|
|keyboard|true||
|overview|true||
|center|true|Default Value: `true`|
|touch|true|Default Value: `true`|
|loop|false||
|rtl|false||
|fragments|true||
|embedded|false||
|help|true||
|autoSlide|0||
|autoSlideStoppable|true||
|mouseWheel|false||
|hideAddressBar|true||
|previewLinks|false||
|transition|`'default'`|`none` `fade` `slide` `convex` `concave` `zoom`|
|transitionSpeed|`'default'`|`default` `fast` `slow`|
|backgroundTransition|`'default'`|`none` `fade` `slide` `convex` `concave` `zoom` Default Value: `'convex'`|
|viewDistance|3||
|parallaxBackgroundImage|''|`'https://s3.amazonaws.com/hakim-static/reveal-js/reveal-parallax-1.jpg'`|
|parallaxBackgroundSize|CSS syntax|`"2100px 900px`|

# Slides Section
** Please refer to the sample `presentation.yaml` included. **
