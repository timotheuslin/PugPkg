Pug
===
"Pug, the UDK Guide dog" is a front-end to build a standalone [UDK/EDK2](https://github.com/tianocore/edk2) driver using .C source files and a .PY as the config file.
- The UDK build process is automated and simplified by Pug, so the user does not need to tackle the tedious details in .INF/.DSC files when she/he is simply intent to write a tiny driver for proof-of-concept.
- Since only .C and .PY files are created or touched, the user can easily deliver those touched files to peers/repositories for reviewing/archiving purpose.
- Pug runs with MSVC(Windows) or GCC(Linux) or Xcode(Mac)

## Prerequisites:
1. Python 2.7.x or Python 3.7.x
2. git 2.17.x

## Generic prerequisites for the UDK build:
0. Reference:
    - [Getting Started with EDK II](https://github.com/tianocore/tianocore.github.io/wiki/Getting%20Started%20with%20EDK%20II) 
    - [Xcode](https://github.com/tianocore/tianocore.github.io/wiki/Xcode)
1. nasm (2.0 or above)
2. iasl (version 2018xxxx or later)
3. MSVC(Windows) or Xcode(Mac) or GCC(Open-source Posix)
4. build-essential uuid-dev (Posix)
5. pip2 install future (Python 2.7.x)
6. motc (Xcode)

## Tool installation hints for any Debian-Based Linux:
 `$ sudo apt update ; sudo apt install nasm iasl build-essential uuid-dev`

## Usage: 
0. Change-directory to folder **Pug** .
1. (Optional) Edit `config.py` for the settings accordingly in: WORKSPACE, PLATFORM, TARGET_TXT.
2. (Optional) Edit `CODETREE` in `config.py` to specify where to place the downloaded source files of the UDK git repo or any other additional respos.
3. (Optional) Edit `COMPONENTS` in `config.py` for the target entry(-ies) to be built.
4. Run `./pug.py` <br>
    `pug.py` would automatically try to git-clone the [edk2 code tree](https://github.com/tianocore/edk2) and the submodule, openssl for the 1st time.
5. Browse folder **\_pug\_** for the temporary files (.dsc/.inf) and folder **\_pug\_/Conf** for CONF_PATH setting files.
6. Browse folder **\.\./Build** for the build results.
7. Run `./pug.py clean` or `./pug.py cleanall` to clean (all) the artifact files.

## Additional use cases:
1. To build an edk2 package: (Taking OvmfPkg and ShellPkg for examples.)<br>
  `$ ./pug.py -p OvmfPkg/OvmfPkgX64.dsc`<br>
  `$ ./pug.py -p ShellPkg/ShellPkg.dsc`<br>
