import iheartla.la_tools.la_helper as la_helper
from iheartla.la_tools.la_helper import DEBUG_MODE, read_from_file, save_to_file
from iheartla.la_tools.la_logger import LaLogger
import logging
import argparse
import markdown
import os.path
from pathlib import Path
import shutil


if __name__ == '__main__':
    LaLogger.getInstance().set_level(logging.DEBUG if DEBUG_MODE else logging.ERROR)
    arg_parser = argparse.ArgumentParser(description='I Heart LA paper compiler')
    arg_parser.add_argument('--regenerate-grammar', action='store_true', help='Regenerate grammar files')
    arg_parser.add_argument('--paper', nargs='*', help='paper text')
    args = arg_parser.parse_args()
    print(args.paper)
    if args.regenerate_grammar:
        la_helper.DEBUG_PARSER = True
        import iheartla.la_tools.parser_manager
        iheartla.la_tools.parser_manager.recreate_local_parser_cache()
    else:
        args.paper = ['/Users/pressure/Downloads/lib_paper/test.md']
        for paper_file in args.paper:
            content = read_from_file(paper_file)
            body = markdown.markdown(content, extensions=['markdown.extensions.iheartla_code', \
                                                          'markdown.extensions.attr_list', \
                                                          'markdown.extensions.fenced_code', \
                                                          'markdown.extensions.abbr', \
                                                          'markdown.extensions.def_list', \
                                                          'markdown.extensions.footnotes', \
                                                          'markdown.extensions.md_in_html', \
                                                          'markdown.extensions.tables', \
                                                          'markdown.extensions.admonition', \
                                                          # 'markdown.extensions.codehilite', \
                                                          'markdown.extensions.legacy_attrs', \
                                                          'markdown.extensions.legacy_em', \
                                                          'markdown.extensions.meta', \
                                                          'markdown.extensions.nl2br', \
                                                          'markdown.extensions.sane_lists', \
                                                          'markdown.extensions.smarty', \
                                                          'markdown.extensions.toc', \
                                                          'markdown.extensions.wikilinks'], path=os.path.dirname(Path(paper_file)))
            equation_json = read_from_file("{}/data.json".format(os.path.dirname(Path(paper_file))))
            # equation_data = get_sym_data(json.loads(equation_json))
            sym_json = read_from_file("{}/sym_data.json".format(os.path.dirname(Path(paper_file))))
            dst = "{}/resource".format(os.path.dirname(Path(paper_file)))
            # if os.path.exists(dst):
            #     shutil.rmtree(dst)
            # shutil.copytree("./extras/resource", dst)
            script = r"""window.onload = parseAllSyms;
function reportWindowSize() {
  var arrows = document.querySelectorAll(".arrow");
  if (arrows) {
    for (var i = arrows.length - 1; i >= 0; i--) {
      var arrow = arrows[i];
      var body = document.querySelector("body");
      var style = window.getComputedStyle(body);
      var curOffset = parseInt(style.marginLeft, 10)
      var oldOffset = arrow.getAttribute('offset');
      arrow.setAttribute('offset', curOffset);
      // console.log(`oldOffset:${oldOffset}, curOffset:${curOffset}`);
      var arrowStyle = window.getComputedStyle(arrow); 
      var arrowOffset = parseInt(document.querySelector(".arrow").style.marginLeft, 10)
      arrow.style.marginLeft = `${arrowOffset+curOffset-oldOffset}px`;
      var newWidth = parseInt(style.width, 10) + parseInt(style.marginLeft, 10) + parseInt(style.marginRight, 10);
      arrow.style.width = `${newWidth}px`;
      arrow.style.height = style.height; 
      // console.log(`arrow.style.width:${arrow.style.width}, arrow.style.height:${arrow.style.height}`)
    }
  }
}
window.onresize = reportWindowSize;
"""
            mathjax = r'''<script>
MathJax = {
  loader: {
    load: ["[attrLabel]/attr-label.js"],
    paths: { attrLabel: "./resource" },
  },
  // options: {
  //   a11y: {
  //     speech: true, // switch on speech output
  //     braille: true, // switch on Braille output
  //     subtitles: true, // show speech as a subtitle
  //   },
  //   menuOptions: {
  //     settings: {
  //       explorer: true,
  //     },
  //   },
  // },
  tex: { packages: { "[+]": ["attr-label"] },
   inlineMath: [['$', '$'], ['\\(', '\\)']]
   },
};
    </script>'''
            html = r"""<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"> 
    {mathjax}
    <script type="text/javascript" id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script src="https://unpkg.com/@popperjs/core@2"></script>
    <script src="https://unpkg.com/tippy.js@6"></script>
    <script src="./resource/d3.min.js"></script>
    <script src="./resource/svg.min.js"></script>
    <script type="text/javascript" src='./resource/paper.js'></script>
    <link rel="stylesheet" href="./resource/paper.css">
</head>
<script>
const iheartla_data = JSON.parse('{equation_json}');
const sym_data = JSON.parse('{sym_json}');
{script}
</script>
<body>
<img src="./resource/glossary.png" id="glossary" alt="glossary" width="22" height="28">
{body}
</body>
</html>""".format(mathjax=mathjax, equation_json=equation_json,  sym_json=sym_json, script=script, body=body)
            save_to_file(html, "/Users/pressure/Downloads/lib_paper/paper.html")
            # print(html)
