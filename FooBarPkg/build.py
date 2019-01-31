#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

"""
A front-end to build EFI driver(s) from a sandbox package.

Timothy Lin Jan/30/2019, BSD 3-Clause License.


PREREQUISITES:
1. Python 2.7 or Python 3.x
2. git 2.17.x


TODO:
1. fix-up the content of Conf/target.txt.
2. recovery from the git failure.
3. extract the relevant information in FooBarPkg.dsc into a config settings.


BACKUP BACKUP BACKUP BACKUP BACKUP BACKUP BACKUP BACKUP BACKUP BACKUP BACKUP BACKUP BACKUP BACKUP


build -h
Usage: build.exe [options] [all|fds|genc|genmake|clean|cleanall|cleanlib|modules|libraries|run]

Copyright (c) 2007 - 2018, Intel Corporation  All rights reserved.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -a TARGETARCH, --arch=TARGETARCH
                        ARCHS is one of list: IA32, X64, ARM, AARCH64 or EBC,
                        which overrides target.txt's TARGET_ARCH definition.
                        To specify more archs, please repeat this option.
  -p PLATFORMFILE, --platform=PLATFORMFILE
                        Build the platform specified by the DSC file name
                        argument, overriding target.txt's ACTIVE_PLATFORM
                        definition.
  -m MODULEFILE, --module=MODULEFILE
                        Build the module specified by the INF file name
                        argument.
  -b BUILDTARGET, --buildtarget=BUILDTARGET
                        Using the TARGET to build the platform, overriding
                        target.txt's TARGET definition.
  -t TOOLCHAIN, --tagname=TOOLCHAIN
                        Using the Tool Chain Tagname to build the platform,
                        overriding target.txt's TOOL_CHAIN_TAG definition.
  -x SKUID, --sku-id=SKUID
                        Using this name of SKU ID to build the platform,
                        overriding SKUID_IDENTIFIER in DSC file.
  -n THREADNUMBER       Build the platform using multi-threaded compiler. The
                        value overrides target.txt's
                        MAX_CONCURRENT_THREAD_NUMBER. When value is set to 0,
                        tool automatically detect number of processor threads,
                        set value to 1 means disable multi-thread build, and
                        set value to more than 1 means user specify the
                        threads number to build.
  -f FDFFILE, --fdf=FDFFILE
                        The name of the FDF file to use, which overrides the
                        setting in the DSC file.
  -r ROMIMAGE, --rom-image=ROMIMAGE
                        The name of FD to be generated. The name must be from
                        [FD] section in FDF file.
  -i FVIMAGE, --fv-image=FVIMAGE
                        The name of FV to be generated. The name must be from
                        [FV] section in FDF file.
  -C CAPNAME, --capsule-image=CAPNAME
                        The name of Capsule to be generated. The name must be
                        from [Capsule] section in FDF file.
  -u, --skip-autogen    Skip AutoGen step.
  -e, --re-parse        Re-parse all meta-data files.
  -c, --case-insensitive
                        Don't check case of file name.
  -w, --warning-as-error
                        Treat warning in tools as error.
  -j LOGFILE, --log=LOGFILE
                        Put log in specified file as well as on console.
  -s, --silent          Make use of silent mode of (n)make.
  -q, --quiet           Disable all messages except FATAL ERRORS.
  -v, --verbose         Turn on verbose output with informational messages
                        printed, including library instances selected, final
                        dependency expression, and warning messages, etc.
  -d DEBUG, --debug=DEBUG
                        Enable debug messages at specified level.
  -D MACROS, --define=MACROS
                        Macro: "Name [= Value]".
  -y REPORTFILE, --report-file=REPORTFILE
                        Create/overwrite the report to the specified filename.
  -Y REPORTTYPE, --report-type=REPORTTYPE
                        Flags that control the type of build report to
                        generate.  Must be one of: [PCD, LIBRARY, FLASH,
                        DEPEX, BUILD_FLAGS, FIXED_ADDRESS, HASH,
                        EXECUTION_ORDER].  To specify more than one flag,
                        repeat this option on the command line and the default
                        flag set is [PCD, LIBRARY, FLASH, DEPEX, HASH,
                        BUILD_FLAGS, FIXED_ADDRESS]
  -F FLAG, --flag=FLAG  Specify the specific option to parse EDK UNI file.
                        Must be one of: [-c, -s]. -c is for EDK framework UNI
                        file, and -s is for EDK UEFI UNI file. This option can
                        also be specified by setting *_*_*_BUILD_FLAGS in
                        [BuildOptions] section of platform DSC. If they are
                        both specified, this value will override the setting
                        in [BuildOptions] section of platform DSC.
  -N, --no-cache        Disable build cache mechanism
  --conf=CONFDIRECTORY  Specify the customized Conf directory.
  --check-usage         Check usage content of entries listed in INF file.
  --ignore-sources      Focus to a binary build and ignore all source files
  --pcd=OPTIONPCD       Set PCD value by command line. Format: "PcdName=Value"
  -l COMMANDLENGTH, --cmd-len=COMMANDLENGTH
                        Specify the maximum line length of build command.
                        Default is 4096.
  --hash                Enable hash-based caching during build process.
  --binary-destination=BINCACHEDEST
                        Generate a cache of binary files in the specified
                        directory.
  --binary-source=BINCACHESOURCE
                        Consume a cache of binary files from the specified
                        directory.
  --genfds-multi-thread
                        Enable GenFds multi thread to generate ffs file.
"""


from __future__ import print_function
from __future__ import absolute_import


import os
import sys
import shutil
import multiprocessing


def setup_env_vars(env_dict):
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


def setup_conf_files(files, dest_conf_dir=''):
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
UDKBUILD_TOOLCHAIN = 'GCC5'
UDKBUILD_MODULE_INF = 'I2CProtocols.inf'
UDKBUILD_PLATFORM_DSC = 'FooBarPkg.dsc'

UDK_GIT_URL = 'https://github.com/tianocore/edk2.git'


def build(workspace='', udk_home=''):
    """build!"""
    if udk_home and not os.path.isabs(udk_home):
        udk_home = os.path.join(os.getcwd(), udk_home)
    if not workspace:
        workspace = os.getcwd()

    setup_env_vars({
        '=WORKSPACE': workspace,
        '=UDK_ABSOLUTE_DIR': udk_home if udk_home else os.path.join(os.getcwd(), 'edk2'),
    })

    setup_env_vars({
        '=EDK_TOOLS_PATH': os.path.join(os.environ['UDK_ABSOLUTE_DIR'], 'BaseTools'),
    })

    setup_env_vars({
        '+PACKAGES_PATH':'$UDK_ABSOLUTE_DIR',
        '=EDK_TOOLS_PATH_BIN': os.path.join(
            os.environ['EDK_TOOLS_PATH'], 'BinWrappers', 'PosixLike'),
        '=CONF_PATH':os.path.join(os.environ['WORKSPACE'], 'Conf'),
    })

    setup_env_vars({'*PATH': '$EDK_TOOLS_PATH_BIN'})

    setup_conf_files(['build_rule', 'tools_def', 'target'])

    BUILD_BASETOOLS_CMDS = [
        'cd', os.environ['EDK_TOOLS_PATH'], ';',
        'make',
    ]
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'cleanall':
        BUILD_BASETOOLS_CMDS += ['clean']

    UDKBUILD_CMDS = [
        'cd', os.environ['WORKSPACE'], ';',
        'build',
    ] + [
        '-a %s' % a for a in UDKBUILD_ARCHS.split()
    ] + [
        '-p', UDKBUILD_PLATFORM_DSC,
        '-m', UDKBUILD_MODULE_INF,
        '-t', UDKBUILD_TOOLCHAIN,
        '-b', UDKBUILD_TARGET,
        '-n', '%d' % multiprocessing.cpu_count(),
        '-N',
    ] + sys.argv[1:]

    print_run(BUILD_BASETOOLS_CMDS)
    print_run(UDKBUILD_CMDS)

    return 0


def setup_udk_codetree(udk_home):
    """pulll the udk code tree when it does not exist locally."""
    getcode = ''
    if udk_home and not os.path.isabs(udk_home):
        udk_home = os.path.join(os.getcwd(), udk_home)

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
            return 0
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
            'cd', udk_home, ';',
            'git', 'checkout',
            '--recurse-submodules',
            '.',
        ]
        return print_run(cmds)
    return 0

if __name__ == '__main__':
    udk_dir = '/tmp/edk2'
    r = setup_udk_codetree(udk_dir)
    if r:
        print('Unable to setup the UDK code tree at: %s' % udk_dir)
        print('Do you have the access to that folder?')
        sys.exit(r)
    build(udk_home=udk_dir)
