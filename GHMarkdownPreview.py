import os
import sublime
import sublime_plugin
import tempfile
import webbrowser
import json
import subprocess

# The python package included with sublime text for Linux is missing the ssl
# module (for technical reasons), so this import will fail. But, we can use the
# curl command instead, which should be present on just about any Linux.
use_curl = False
try:
    import ssl
except ImportError as e:
    use_curl = True

try:
    import urllib2
except ImportError:
    import urllib.request

def call_exe(command, dir):
    process = subprocess.Popen(
        command,
        cwd=dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True)
    stdout, stderr = process.communicate()
    exit_code = process.wait()
    if exit_code:
        raise Exception(stdout)
    return stdout

def generate_preview(text):
    http_header = { 'Content-type': 'application/json' }
    url = 'https://api.github.com/markdown'
    body = json.dumps({'text': text, 'mode': 'gfm', 'context': ''}).encode('utf8')
    if use_curl:
        return call_exe(['curl', url, "-d", body], ".").encode('utf8')
    try:
        resp = urllib2.urlopen(url, body)
    except NameError:
        req = urllib.request.Request(url, body, http_header)
        resp = urllib.request.urlopen(req)
    return resp.read()

def wrap_content(tempfile, content):
    html = ("<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\"><link rel=\"stylesheet\" type=\"text/css\" href=\"https://gist.githubusercontent.com/andyferra/2554919/raw/2e66cabdafe1c9a7f354aa2ebf5bc38265e638e5/github.css\" media=\"screen\" /></head><body>%s</body></html>" % content.decode('utf8')).encode('utf8')
    return html

class github_markdown_preview_command(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            selection = sublime.Region(0, self.view.size())
            html = generate_preview(self.view.substr(selection))
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
            temp_file.write(wrap_content(temp_file, html))
            temp_file.close()
            webbrowser.open("file://" + temp_file.name)
        except Exception as e:
            sublime.error_message("Error in GitHubMarkdownPreview package:\n\n" + str(e))
