from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ["queue","uuid","hmac","cgi","nturl2path","idnadata"], excludes = [])

# base = 'Console'
base = 'Win32Gui'

executables = [
    Executable('ListenWrite.py', base=base)
]

setup(name='test_project',
      version = '3.0',
      description = 'test for cxfreeze',
      options = dict(build_exe = buildOptions),
      executables = executables)





# from cx_Freeze import setup, Executable
#
# base = 'Win32Gui'
#
# setup(name='listenwrite exe',
#       version='3.0',
#       description='listenwrite exe file',
#       executables=[Executable("ListenWrite.py",base=base)]
#       )
