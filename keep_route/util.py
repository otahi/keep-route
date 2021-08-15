import locale
import os
import sys
import subprocess
import json
import tempfile
from json import JSONDecodeError

class Util(object):
    prefferd_encoding = locale.getpreferredencoding()

    @staticmethod
    def version():
        with open(Util.app_path('version.json')) as f:
            return json.load(f)['version']

    @staticmethod
    def app_path(path):
        frozen = 'not'

        if getattr(sys, 'frozen', False):
                # we are running in executable mode
                frozen = 'ever so'
                app_dir = sys._MEIPASS
        else:
                # we are running in a normal Python environment
                app_dir = os.path.dirname('.')
        return os.path.join(app_dir, path)

    @staticmethod
    def open_home():
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.run(["powershell", "start", "https://github.com/otahi/keep-route"],
            shell=False, capture_output=False,
            startupinfo=startupinfo,
        )

    @classmethod
    def run_ps_command(cls, cmd):
        result = {}

        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            with tempfile.TemporaryDirectory() as tmpdir:
                tmpfile = os.path.join(tmpdir, 'tmp')
                command = f"& {{{cmd} |Out-File {tmpfile} -Encoding utf8 }}"

                process = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", command],
                    shell=True,
                    startupinfo=startupinfo,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                if process.returncode == 0:
                    with open(tmpfile, "r+b") as f:
                        data = f.read()
                    text = data.decode(encoding='utf-8-sig')
                    try:
                        result = json.loads(text)
                    except JSONDecodeError as e:
                        result = {}
                    return result
                else:
                    print(f"Error: {process.returncode}")
        except:
            print(f"Execption")

        finally:
            return result

    @classmethod
    def dict_filter(cls, org_dict, org_keys, target_keys = None):
        dest_dict = []

        if target_keys is None:
            target_keys = org_keys

        if not isinstance(org_dict, list):
            org_dict = [org_dict]

        for od in org_dict:
            dd = {}
            for i, key in enumerate(org_keys):
                try:
                    dd[target_keys[i]] = od[key]
                except KeyError:
                    dd[target_keys[i]] = None
            dest_dict.append(dd)

        if not isinstance(org_dict, list):
            return dest_dict[0]

        return dest_dict