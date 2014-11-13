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
        stderr=subprocess.PIPE,
        universal_newlines=True)
    stdout, stderr = process.communicate()
    exit_code = process.wait()
    if exit_code:
        raise Exception(stdout)
    return stdout

def get_github_repo_name(filename):
    if filename is None:
        return None
    directory = os.path.dirname(filename)
    remotes = call_exe(['git', 'remote'], directory).splitlines()
    for remote in remotes:
        url = call_exe(['git', 'config', '--get', 'remote.' + remote + '.url'], directory)
        if url.startswith('git@github.com:'):
            return url.replace('git@github.com:', '')[0:-5]
        if url.startswith('https://github.com/'):
            return url.replace('https://github.com/', '')[0:-5]

def generate_preview(text, repo_name):
    http_header = { 'Content-type': 'application/json' }
    url = 'https://api.github.com/markdown'
    body = json.dumps({'text': text, 'mode': 'gfm', 'context': repo_name}).encode('utf8')
    if use_curl:
        return call_exe(['curl', url, "-d", body], ".").encode('utf8')
    try:
        resp = urllib2.urlopen(url, body)
    except NameError:
        req = urllib.request.Request(url, body, http_header)
        resp = urllib.request.urlopen(req)
    return resp.read()

class github_markdown_preview_command(sublime_plugin.TextCommand):
    def run(self, edit):
        try:
            selection = sublime.Region(0, self.view.size())
            repoName = get_github_repo_name(self.view.file_name())
            html = generate_preview(self.view.substr(selection), repoName)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
            temp_file.write(html)
            temp_file.close()
            webbrowser.open("file://" + temp_file.name)
        except Exception as e:
            sublime.error_message("Error in GitHubMarkdownPreview package:\n\n" + str(e))
