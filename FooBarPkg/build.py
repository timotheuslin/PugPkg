"""
"""

import os
import sys
import shutil
import collections

UDK_SUB_DIR = 'edk2'
UDK_ABS_DIR = ''

def SetEnvVar(env_dict):
    for e in env_dict:
        e0 = e[0]
        e1 = e[1:]
        if env_dict[e][0] == '$':
            env_dict[e] = os.environ.get(env_dict[e][1:], '')
        if e0 in {'+', '*'}:
            try:
                if e0 == '+':
                    ex = '%s%s%s' % (os.environ[e1], os.pathsep, env_dict[e])
                elif e0 == '*':
                    ex = '%s%s%s' % (env_dict[e], os.pathsep, os.environ[e1])
                os.environ[e1] = ex
            except KeyError:
                os.environ[e1] = env_dict[e]
        elif e0 == '=':
            if e1 not in os.environ:
                os.environ[e1] = env_dict[e]
        else:
            raise Exception('error.')

SetEnvVar(
    collections.OrderedDict([
        ('=WORKSPACE', os.path.dirname(os.getcwd())),
        ('=EDK_TOOLS_PATH', os.path.join(os.getcwd(), UDK_SUB_DIR, 'BaseTools')),
        ('=UDK_ABS_DIR', os.path.join(os.getcwd(), UDK_SUB_DIR)),
        ('+PACKAGES_PATH', '$UDK_ABS_DIR'),
    ])
)

SetEnvVar(
    collections.OrderedDict([
        ('=EDK_TOOLS_PATH_BIN', os.path.join(os.environ['EDK_TOOLS_PATH'], 'BinWrappers', 'PosixLike')),
        ('=CONF_PATH', os.path.join(os.environ['WORKSPACE'], 'Conf')),
        ('*PATH', '$EDK_TOOLS_PATH_BIN'),
    ])
)


def CopyTemplate(files):
    """
    CopySingleTemplateFile build_rule
    CopySingleTemplateFile tools_def
    CopySingleTemplateFile target"""

    dest_conf_dir = os.environ.get('CONF_PATH', os.environ['WORKSPACE'])
    edk_tools_path = os.environ.get('EDK_TOOLS_PATH', os.path.join(os.environ['WORKSPACE'], 'BaseTools'))
    src_conf_dir = os.path.join(edk_tools_path, 'Conf')
    print('CONF_PATH: %s' % dest_conf_dir)
    if not os.path.exists(dest_conf_dir):
        os.makedirs(dest_conf_dir)
    for f in files:
        src_conf_path = os.path.join(src_conf_dir, f+'.template')
        dest_conf_path = os.path.join(dest_conf_dir, f+'.txt')
        print('Copying %s\n--> %s' % (src_conf_path, dest_conf_path))
        shutil.copyfile(src_conf_path, dest_conf_path)

CopyTemplate(['build_rule', 'tools_def', 'target'])

buildenv = os.path.join(os.environ['EDK_TOOLS_PATH'], 'BuildEnv')
print(buildenv)
os.system(buildenv)

build_basetools = 'cd %s; make' % os.environ['EDK_TOOLS_PATH']
os.system(build_basetools)

cmd = ' '.join(['build -a X64 -p FooBarPkg/FooBarPkg.dsc -t GCC5 -b RELEASE -N'] + sys.argv[1:])
print('%s' % cmd)
os.system(cmd)