#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, line-too-long, too-many-nested-blocks, too-many-branches, too-many-locals


"""
PUG: "Pug, the UEFI Guidedog", or "the Programmer's UEFI Guide".

A front-end to build the EFI driver(s) from a sandbox package.

8b,dPPYba,  88       88  ,adPPYb,d8
88P'    "8a 88       88 a8"    `Y88
88       d8 88       88 8b       88
88b,   ,a8" "8a,   ,a88 "8a,   ,d88
88`YbbdP"'   `"YbbdP'Y8  `"YbbdP"Y8
88                       aa,    ,88
88                        "Y8bbdP"

Timothy Lin Jan/30/2019, BSD 3-Clause License.

PREREQUISITES:
1. Python 2.7 or Python 3.x
2. git 2.17.x

PREREQUISITES for the UDK build:
    Ref. https://github.com/tianocore/tianocore.github.io/wiki/Getting%20Started%20with%20EDK%20II
1. nasm
2. iasl
3. GCC(Posix) or MSVC(Windows)
4. build-essential uuid-dev (Posix)
5. pip2 install future

TODO:
1. keyword list of the supported section names of DSC and INF.
2. X64/IA32 section differentiation.
3. automate the tool-chain for Windows/Linux/Mac.

"""

from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import shutil
import threading
import subprocess
import multiprocessing

sys.dont_write_bytecode = True      # To inhibit the creation of .pyc file

VERBOSE_LEVEL = 1
UDKBUILD_MAKETOOL = 'nmake' if os.name == 'nt' else 'make'
UDKBUILD_COMMAND_JOINTER = '&' if os.name == 'nt' else ';'

default_pug_signature = '#\n# This file is automatically created by PUG.\n#\n'

try:
    import config
except ImportError:
    print('Unable to load the configuration file, config.py.')
    raise


def abs_path(sub_dir, base_dir):
    """return an absolute path."""
    return sub_dir if os.path.isabs(sub_dir) else os.path.join(base_dir, sub_dir)


def write_file(path, content, signature=''):
    """update a platform's dsc file content.
    - create the folder when it does not exist.
    - skip write attempt when the contents are identical"""

    if isinstance(content, (list, tuple)):
        content = '\n'.join(content)
    if signature:
        content = signature + content
    path_dir = os.path.dirname(path)
    content0 = ''
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)
    else:
        if os.path.exists(path):
            with open(path, 'r') as pf:
                content0 = pf.read()
            if content0 == content:
                return
    with open(path, 'w') as pf:
        pf.write(content)


def conf_files(files, dest_conf_dir, verbose=False):
    """Ref. BaseTools/BuildEnv for build_rule.txt , tools_def.txt and target.txt"""
    dest_conf_dir = os.path.abspath(dest_conf_dir)
    if not os.path.exists(dest_conf_dir):
        os.makedirs(dest_conf_dir)
    os.environ["CONF_PATH"] = dest_conf_dir
    src_conf_dir = os.path.join(os.environ.get('EDK_TOOLS_PATH', os.path.join(os.environ['WORKSPACE'], 'BaseTools')), 'Conf')
    for f in files:
        src_conf_path = os.path.join(src_conf_dir, '%s.template' % f)
        dest_conf_path = os.path.join(dest_conf_dir, '%s.txt' % f)
        if verbose:
            print('Copy %s\nTo   %s' % (src_conf_path, dest_conf_path))
        shutil.copyfile(src_conf_path, dest_conf_path)


def gen_section(items, override=None, section='', sep='=', ident=0):
    """generate a section's content"""
    ret_list = []
    if section:
        ret_list += ['\n%s[%s]' % (' '*ident*2, section)]
    if items:
        if isinstance(items, (tuple, list)) or (override in {list, tuple}):
            for d in items:
                if d:
                    if isinstance(d, (list, tuple)):
                        ret_list += ['%s%s' % (' '*(ident+1)*2, sep.join(d))]
                    else:
                        ret_list += ['%s%s' % (' '*(ident+1)*2, str(d))]
        elif isinstance(items, dict):
            ret_list += ['%s%s %s %s' % (' '*(ident+1)*2, str(d), sep, str(items[d])) for d in sorted(items) if d]
    return ret_list


def gen_target_txt(target_txt):
    """generate the content of Conf/target.txt"""
    tt = []
    for s in sorted(target_txt):
        if s.isupper():
            tt += ['%s = %s' % (s, target_txt[s])]
    write_file(target_txt["path"], tt)


def LaunchCommand(Command, WorkingDir='.', verbose=False):
    """A derivative of UDK's BaseTools/build/build.py"""
    LaunchCommand.stdout_buffer = []
    LaunchCommand.stderr_buffer = []
    def ReadMessage(From, To, ExitFlag):
        """read message fro stream"""
        while True:
            Line = From.readline()
            if Line:
                To(Line.rstrip())
            if not Line or ExitFlag.isSet():
                break

    def __logger(msg, bufferx):
        if isinstance(msg, bytes):
            msg = msg.decode('utf-8')
        if verbose:
            print('%s' % msg)
        else:
            bufferx += [msg]

    def logger_stdout(msg):
        """print message from stdout"""
        __logger(msg, LaunchCommand.stdout_buffer)

    def logger_stderr(msg):
        """print message from stderr"""
        __logger(msg, LaunchCommand.stderr_buffer)

    if isinstance(Command, (list, tuple)):
        Command = ' '. join(Command)
    print('%s' % Command)

    WorkingDir = os.path.abspath(WorkingDir)
    Proc = EndOfProcedure = StdOutThread = StdErrThread = None
    _stdout = sys.stdout if verbose else subprocess.PIPE
    _stderr = sys.stderr if verbose else subprocess.PIPE
    try:
        Proc = subprocess.Popen(Command, stdout=_stdout, stderr=_stderr, env=os.environ, cwd=WorkingDir, bufsize=-1, shell=True)
        if not verbose:
            EndOfProcedure = threading.Event()
            EndOfProcedure.clear()
            if Proc.stdout:
                StdOutThread = threading.Thread(target=ReadMessage, args=(Proc.stdout, logger_stdout, EndOfProcedure))
                StdOutThread.setName("STDOUT-Redirector")
                StdOutThread.setDaemon(False)
                StdOutThread.start()
            if Proc.stderr:
                StdErrThread = threading.Thread(target=ReadMessage, args=(Proc.stderr, logger_stderr, EndOfProcedure))
                StdErrThread.setName("STDERR-Redirector")
                StdErrThread.setDaemon(False)
                StdErrThread.start()
            # waiting for program exit
        Proc.wait()
    except Exception:
        raise

    return_code = -1
    if Proc:
        if Proc.stdout and StdOutThread:
            StdOutThread.join()
        if Proc.stderr and StdErrThread:
            StdErrThread.join()
        return_code = Proc.returncode
    s1 = '\n'.join(LaunchCommand.stdout_buffer)
    s2 = '\n'.join(LaunchCommand.stderr_buffer)
    return return_code, s1, s2

LaunchCommand.stdout_buffer = []
LaunchCommand.stderr_buffer = []

def locate_nasm():
    """Try to locate the nasm's installation directory. For Windows only."""
    for d in [
            'C:\\Program Files\\NASM\nasm.exe',
            'C:\\Program Files (x86)\\NASM\nasm.exe',
            os.environ.get('LOCALAPPDATA', '') + '\\bin\\NASM\\nasm.exe',
            'C:\\NASM\\nasm.exe',
        ]:
        if os.path.exists(d):
            return os.path.dirname(d)
    return ''


def env_vars(workspace, udk_home):
    """Setup environment variables"""
    #def _env_vars(env_dict):
    def _env_vars(k, v):
        """Setup environment variables"""
        k0 = k[0]
        k1 = k[1:]
        if v[0] == '$':             #marco from os.environ
            v = os.environ.get(v[1:], '')
        if k0 in {'+', '*'}:
            try:
                ex = ''
                if k0 == '+':       #append
                    ex = '%s%s%s' % (os.environ[k1], os.pathsep, v)
                elif k0 == '*':     #prepend
                    ex = '%s%s%s' % (v, os.pathsep, os.environ[k1])
                os.environ[k1] = ex
            except KeyError:
                os.environ[k1] = v
        elif k0 == '=':             # conditional assignment
            if k1 not in os.environ:
                os.environ[k1] = v
        else:                       # unconditional assignment
            os.environ[k] = v
    _env_vars('=WORKSPACE', os.path.abspath(workspace))
    _env_vars('=UDK_ABSOLUTE_DIR', os.path.abspath(udk_home))
    _env_vars('=EDK_TOOLS_PATH', os.path.join(os.environ['UDK_ABSOLUTE_DIR'], 'BaseTools'))
    _env_vars('+PACKAGES_PATH', '$UDK_ABSOLUTE_DIR')
    _env_vars('+PACKAGES_PATH', os.path.abspath(".."))
    _env_vars('=CONF_PATH', os.path.join(os.environ['WORKSPACE'], 'Conf'))
    _env_vars('=BASE_TOOLS_PATH', '$EDK_TOOLS_PATH')
    _env_vars('=PYTHONPATH', os.path.join(os.environ['EDK_TOOLS_PATH'], 'Source', 'Python'))
    _env_vars('=EDK_TOOLS_PATH_BIN', os.path.join(os.environ['EDK_TOOLS_PATH'], 'BinWrappers', "WindowsLike" if os.name == 'nt' else 'PosixLike'))

    if os.name == 'nt':
        _env_vars('*PATH', os.path.join(os.environ['EDK_TOOLS_PATH'], 'Bin', 'Win32'))
        _env_vars('=PYTHON_HOME', os.path.dirname(sys.executable))
        _env_vars('=PYTHONHOME', os.path.dirname(sys.executable))
        nasm_path = locate_nasm()
        if nasm_path:
            _env_vars('=NASM_PREFIX', nasm_path + os.sep)

    _env_vars('*PATH', '$EDK_TOOLS_PATH_BIN')

    print('WORKSPACE      = %s' % os.environ['WORKSPACE'])
    print('PACKAGES_PATH  = %s' % os.environ['PACKAGES_PATH'])
    print('EDK_TOOLS_PATH = %s' % os.environ['EDK_TOOLS_PATH'])
    print('CONF_PATH      = %s' % os.environ['CONF_PATH'])


def basetools(verbose=0):
    """build the C-lang executables in Basetools.
    Use: sys.argv[1]: "clean" """

    build_basetools_cmds = [
        'cd', os.environ['EDK_TOOLS_PATH'], UDKBUILD_COMMAND_JOINTER,
        UDKBUILD_MAKETOOL,
    ]
    if UDKBUILD_MAKETOOL == 'make':
        build_basetools_cmds += [
            '--jobs', '%d' % multiprocessing.cpu_count()
        ]
    if 'cleanall' in sys.argv[1:]:
        build_basetools_cmds += ['clean']
    return LaunchCommand(build_basetools_cmds, verbose=verbose)


def codetree(udk_home, udk_url):
    """pull the udk code tree when it does not locally/correctly exist."""
    if udk_home:
        udk_home = os.path.abspath(udk_home)
    dot_git = os.path.join(udk_home, '.git')
    getcode = ''
    if not os.path.exists(dot_git):
        print('No local UDK code tree: %s.' % udk_home, end='')
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
            print('Missing package: %s.' % pkg, end='')
            getcode = 'checkout'

    if getcode:
        print('  Trying to fix that...')
        if getcode == 'clone':
            cmds = [
                'git', 'clone',
                '--jobs', '%d' % multiprocessing.cpu_count(),
                '--recurse-submodules',
                udk_url,
                udk_home,
            ]
        elif getcode == 'checkout':
            cmds = [
                'cd', udk_home, UDKBUILD_COMMAND_JOINTER,
                'git', 'checkout',
                '--recurse-submodules',
                '.',
            ]
        r = LaunchCommand(cmds, verbose=True)
        return r[0]
    return 0


def platform_dsc(platform, components, workspace):
    """generate a platform's dsc file."""

    dsc_path = abs_path(platform["path"], workspace)
    print("PLATFORM_DSC = %s" % dsc_path)
    if not platform.get("update", False):
        return
    sections = ["Defines", "Components"]
    overrides = {"LibraryClasses", "PcdsFixedAtBuild"} #, "BuildOptions"}
    pfile = []
    for s in sections:
        if s == 'Components':
            pfile += gen_section(None, section=s)
            for compc in components:
                pfile += ['  %s' % compc["path"]]
                in_override = False
                ovs = overrides.intersection(set(compc.keys()))
                for ov in ovs:
                    #print("Override: %s" % ov)
                    if not in_override:
                        pfile[-1] += ' {'
                        in_override = True
                    pfile += ['    <%s>' % ov]
                    sep = '|' if ov in {"LibraryClasses", "PcdsFixedAtBuild"} else '='
                    for d in compc[ov]:
                        if d and d[0]:
                            pfile += ['      %s %s %s' % (d[0], sep, d[1])]
                if in_override:
                    pfile += ['  }']
        else:
            pfile += gen_section(platform[s], section=s)
    write_file(dsc_path, pfile, default_pug_signature)


def component_inf(components, workspace):
    """generate INF files of components."""
    sections = [
        'Sources', 'Packages', 'LibraryClasses', 'Protocols', 'Ppis',
        'Guids', 'FeaturePcd', 'Pcd', 'BuildOptions', 'Depex', 'UserExtensions',
    ]
    for comp in components:
        cfile = []
        inf_path = abs_path(comp.get('path', ""), workspace)
        print('COMPONENT: %s' % inf_path)
        if not comp.get("update", False):
            continue
        defines = comp.get('Defines', '')
        if not defines:
            raise Exception('INF must contain [Defines] section.')
        cfile += gen_section(defines, section='Defines')
        for s in comp:
            s0 = s.split('.')[0]
            if s0 not in sections:
                continue
            #cfile += ['[%s]' % s]
            if  s0 == 'LibraryClasses':
                cfile += gen_section([v[0] for v in comp[s] if v[0] != 'NULL'], section=s, override=list)
            else:
                cfile += gen_section(comp[s], section=s)
        write_file(inf_path, cfile, default_pug_signature)


def build():
    """0. prepare the UDK code tree.
       1. setup environment variables.
       2. build C-lang executables in BaseTools.
       3. UDK build."""

    workspace = os.path.abspath(config.WORKSPACE["path"])
    udk_home = os.path.abspath(config.WORKSPACE["udk_dir"])

    r = codetree(udk_home, config.WORKSPACE["udk_url"])
    if r:
        print('Unable to setup the UDK code tree at: %s' % udk_home)
        print('Do you have the valid read-write access to that folder?')
        return r

    env_vars(workspace, udk_home)
    conf_files(['build_rule', 'tools_def', 'target'], config.WORKSPACE["conf_path"], VERBOSE_LEVEL > 1)
    gen_target_txt(config.TARGET_TXT)

    r, out, err = basetools(verbose=(VERBOSE_LEVEL > 1))
    if r:
        if out or err:
            print('%s' % '\n'.join([out, 'Error:', err]))
        return r

    platform_dsc(config.PLATFORM, config.COMPONENTS, workspace)
    component_inf(config.COMPONENTS, workspace)

    udkbuild_cmds = []
    if os.name == 'nt':
        udkbuild_cmds += [
            os.path.join(os.environ['EDK_TOOLS_PATH'], 'set_vsprefix_envs.bat'),
            UDKBUILD_COMMAND_JOINTER,
        ]
    udkbuild_cmds += [
        'cd', os.environ['WORKSPACE'], UDKBUILD_COMMAND_JOINTER,
        'build',
        '-n', '%d' % multiprocessing.cpu_count(),
        '-N',
    ]
    report_log = config.WORKSPACE.get('report_log', '')
    log_type = config.WORKSPACE.get('log_type', '')
    if report_log:
        udkbuild_cmds += ["-y", config.WORKSPACE["report_log"]]
    if log_type:
        udkbuild_cmds += ["-Y %s" % s for s in log_type.split()]

    udkbuild_cmds += sys.argv[1:]

    r, out, err = LaunchCommand(udkbuild_cmds, verbose=VERBOSE_LEVEL)
    if r:
        if out or err:
            print('%s' % '\n'.join([out, 'Error:', err]))
    else:
        print("Success.")
    return r


if __name__ == '__main__':
    sys.exit(build())
