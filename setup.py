import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ["queue","uuid","hmac","cgi","nturl2path"], excludes = [], include_msvcr = True)

# aip json requests urllib3 chardet certifi

# GUI applications require a different base on Windows (the default is for a
# console application).
# base = 'Console'
base = None
if sys.platform == "win32":
    base = 'Win32Gui'

executables = [
    Executable('ListenWrite.py', base=base),

]
# , icon='icon.ico'

setup(name='listenwrite',
      version = '3.1',
      description = 'listen and write tools',
      options = dict(build_exe = buildOptions),
      executables = executables)



