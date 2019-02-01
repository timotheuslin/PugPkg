#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pylint: disable=invalid-name, line-too-long

"""
A front-end to build the EFI driver(s) from a sandbox package.

Timothy Lin Jan/30/2019, BSD 3-Clause License.


PREREQUISITES:
1. Python 2.7 or Python 3.x
2. git 2.17.x


PREREQUISITES for the UDK build:
    Ref. https://github.com/tianocore/tianocore.github.io/wiki/Getting%20Started%20with%20EDK%20II
1. nasm
2. iasl
3. GCC(posix) or MSVC(nt)
4. build-essential uuid-dev (posix)


TODO:
1. fix-up the content of Conf/target.txt.
2. extract the relevant information in FooBarPkg.dsc into a config settings.
3. automate the tool-chain.
"""


from __future__ import print_function
from __future__ import absolute_import


import os
import sys
import shutil
import multiprocessing


def conf_files(files, dest_conf_dir=''):
    """Ref. BaseTools/BuildEnv:
        CopySingleTemplateFile build_rule
        CopySingleTemplateFile tools_def
        CopySingleTemplateFile target"""
    if not dest_conf_dir:
        dest_conf_dir = os.environ.get('CONF_PATH', os.path.join(os.environ['WORKSPACE'], 'Conf'))
    edk_tools_path = os.environ.get(
        'EDK_TOOLS_PATH', os.path.join(os.environ['WORKSPACE'], 'BaseTools'))
    src_conf_dir = os.path.join(edk_tools_path, 'Conf')
    print('CONF_PATH: %s' % dest_conf_dir)
    if not os.path.exists(dest_conf_dir):
        os.makedirs(dest_conf_dir)
    for f in files:
        src_conf_path = os.path.join(src_conf_dir, f+'.template')
        dest_conf_path = os.path.join(dest_conf_dir, f+'.txt')
        print('Copying file:\nFrom %s\nTo   %s' % (src_conf_path, dest_conf_path))
        shutil.copyfile(src_conf_path, dest_conf_path)


def print_run(cmds):
    """print & run the commands."""
    cmd = ' '.join(cmds)
    print('%s' % cmd)
    return os.system(cmd)


#UDKBUILD_ARCHS = 'IA32 X64'
UDKBUILD_ARCHS = 'X64'
UDKBUILD_TARGET = 'RELEASE'
UDKBUILD_TOOLCHAIN = 'VS2015x86' if os.name == 'nt' else 'GCC5'
UDKBUILD_MODULE_INF = 'I2CProtocols.inf'
UDKBUILD_PLATFORM_DSC = 'FooBarPkg.dsc'

UDKBUILD_MAKETOOL = 'nmake' if os.name == 'nt' else 'make'
UDKBUILD_COMMAND_JOINTER = '&' if os.name == 'nt' else ';'

UDK_GIT_URL = 'https://github.com/tianocore/edk2.git'


def locate_nasm():
    """Try to locate the nasm's installation directory."""
    if os.name == 'nt':
        dir_candidates = [
            os.path.join('C:', os.sep, 'Program Files', 'NASM'),
            os.path.join('C:', os.sep, 'Program Files (x86)', 'NASM'),
            os.path.join(os.environ['LOCALAPPDATA'], 'bin', 'NASM'),
            os.path.join('C:', os.sep, 'NASM'),
        ]
        exe = 'nasm.exe'
    else: #'posix'
        dir_candidates = [
            os.path.join('usr', 'bin'),
            os.path.join('usr', 'local', 'bin'),
            os.path.join(os.environ['HOME'], '.local', 'bin')
        ]
        exe = 'nasm'
    for d in dir_candidates:
        d0 = os.path.join(d, exe)
        if os.path.exists(d0):
            return d
    return ''

def setup_env_vars(workspace, udk_home):
    """Setup environment variables"""
    def _env_vars(env_dict):
        """Setup environment variables"""
        for e in env_dict:
            e0 = e[0]
            e1 = e[1:]
            if env_dict[e][0] == '$':   #marco from os.environ
                env_dict[e] = os.environ.get(env_dict[e][1:], '')
            if e0 in {'+', '*'}:
                try:
                    if e0 == '+':       #append
                        ex = '%s%s%s' % (os.environ[e1], os.pathsep, env_dict[e])
                    elif e0 == '*':     #prepend
                        ex = '%s%s%s' % (env_dict[e], os.pathsep, os.environ[e1])
                    os.environ[e1] = ex
                except KeyError:
                    os.environ[e1] = env_dict[e]
            elif e0 == '=':             # conditional assignment
                if e1 not in os.environ:
                    os.environ[e1] = env_dict[e]
            else:                       # unditional assignment
                os.environ[e] = env_dict[e]
    _env_vars({
        '=WORKSPACE': workspace,
        '=UDK_ABSOLUTE_DIR': udk_home if udk_home else os.path.abspath('edk2'),
    })

    _env_vars({'=EDK_TOOLS_PATH': os.path.join(os.environ['UDK_ABSOLUTE_DIR'], 'BaseTools'),})

    _env_vars({
        '+PACKAGES_PATH':'$UDK_ABSOLUTE_DIR',
        '=CONF_PATH':os.path.join(os.environ['WORKSPACE'], 'Conf'),
        '=BASE_TOOLS_PATH': '$EDK_TOOLS_PATH',
        '=PYTHONPATH': os.path.join(os.environ['EDK_TOOLS_PATH'], 'Source', 'Python'),
    })

    _env_vars({
        '=EDK_TOOLS_PATH_BIN': os.path.join(os.environ['EDK_TOOLS_PATH'], 'BinWrappers', "WindowsLike" if os.name == 'nt' else 'PosixLike'),
    })

    if os.name == 'nt':
        _env_vars({
            '*PATH':os.path.join(os.environ['EDK_TOOLS_PATH'], 'Bin', 'Win32'),
            '=PYTHON_HOME': os.path.dirname(sys.executable),
            '=PYTHONHOME': os.path.dirname(sys.executable),
        })

    _env_vars({'*PATH': '$EDK_TOOLS_PATH_BIN'})

    if os.name == 'nt':
        nasm_path = locate_nasm()
        if nasm_path:
            _env_vars({'=NASM_PREFIX': nasm_path + os.sep})


def build_basetools(workspace='', udk_home=''):
    """build the C-lang executables in Basetools.
    
    reference: sys.argv[1]: "clean" """

    build_basetools_cmds = [
        'cd', os.environ['EDK_TOOLS_PATH'], UDKBUILD_COMMAND_JOINTER,
        UDKBUILD_MAKETOOL,
    ]
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'cleanall':
        build_basetools_cmds += ['clean']
    return print_run(build_basetools_cmds)


def build(workspace='', udk_home=''):
    """build!"""
    if udk_home:
        udk_home = os.path.abspath(udk_home)
    if not workspace:
        workspace = os.getcwd()

    r = codetree(udk_home)
    if r:
        print('Unable to setup the UDK code tree at: %s' % udk_dir)
        print('Do you have the access to that folder?')
        return r

    setup_env_vars(workspace, udk_home)
    conf_files(['build_rule', 'tools_def', 'target'])
    r = build_basetools(workspace, udk_home)
    if r:
        print('Failure to build C-lang executables in: %s' % os.environ['EDK_TOOLS_PATH'])
        return r

    udkbuild_cmds = []
    if os.name == 'nt':
        udkbuild_cmds += [
            os.path.join(os.environ['EDK_TOOLS_PATH'], 'set_vsprefix_envs.bat'),
            UDKBUILD_COMMAND_JOINTER,
        ]
    udkbuild_cmds += [
        'cd', os.environ['WORKSPACE'], UDKBUILD_COMMAND_JOINTER,
        'build',
    ]
    udkbuild_cmds += [
        '-a %s' % a for a in UDKBUILD_ARCHS.split()
    ]
    udkbuild_cmds += [
        '-p', UDKBUILD_PLATFORM_DSC,
    ]
    if UDKBUILD_MODULE_INF:
        udkbuild_cmds += [
            '-m', UDKBUILD_MODULE_INF,
        ]
    udkbuild_cmds += [
        '-t', UDKBUILD_TOOLCHAIN,
        '-b', UDKBUILD_TARGET,
        '-n', '%d' % multiprocessing.cpu_count(),
        '-N',
    ] + sys.argv[1:]


    return print_run(udkbuild_cmds)


def codetree(udk_home):
    """pulll the udk code tree when it does not exist locally."""
    getcode = ''
    if udk_home:
        udk_home = os.path.abspath(udk_home)

    if not os.path.exists(udk_home):
        print('No local UDK code tree: %s' % udk_home)
        getcode = 'clone'
    else:
        def is_missing_pkg(pkg_names):
            """check if any package is missing in the udk code tree"""
            for pkg_name in pkg_names:
                p = os.path.join(udk_home, pkg_name)
                if not os.path.exists(p):
                    return pkg_name
            return ''
        pkg = is_missing_pkg([
            'MdeModulePkg', 'MdePkg', 'BaseTools',
            'CryptoPkg', 'ShellPkg', 'UefiCpuPkg',
            'PcAtChipsetPkg'])
        if pkg:
            print('Missing package: %s' % pkg)
            getcode = 'checkout'

    if getcode:
        print('Trying to fix that...')
    if getcode == 'clone':
        cmds = [
            'git', 'clone',
            '--jobs', '8',
            '--recurse-submodules',
            UDK_GIT_URL,
            udk_home,
        ]
        return print_run(cmds)
    elif getcode == 'checkout':
        cmds = [
            'cd', udk_home, UDKBUILD_COMMAND_JOINTER,
            'git', 'checkout',
            '--recurse-submodules',
            '.',
        ]
        return print_run(cmds)
    return 0

if __name__ == '__main__':
    udk_dir = 'edk2'
    r = codetree(udk_dir)
    if r:
        print('Unable to setup the UDK code tree at: %s' % udk_dir)
        print('Do you have the access to that folder?')
        sys.exit(r)
    r = build(udk_home=udk_dir)
    sys.exit(r)
