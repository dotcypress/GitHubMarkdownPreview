import os
import sublime
import sublime_plugin
import tempfile
import webbrowser
from urllib.parse import urlparse, urlencode

def generatePreview(data):
  url = 'https://api.github.com/markdown/raw'
  http_header = { "Content-type": "text/x-markdown" }
  req = urllib.request.Request(url, data.encode('utf8'), http_header)
  resp = urllib.request.urlopen(req)
  return resp.read()


class GithubMarkdownPreviewCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    selection = sublime.Region(0, self.view.size())
    html = generatePreview(self.view.substr(selection))
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
    temp_file.write(html)
    temp_file.close()
    webbrowser.open(temp_file.name)
