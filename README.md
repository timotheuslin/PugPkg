FooBarPkg
===
A sandbox package to build standalone UEFI drivers using a front-end script.

## Prerequisites:
1. Python 2.7 or Python 3.x
2. git 2.17.x

## Generic prerequisites for the UDK build:
0. Reference:
    - [Getting Started with EDK II](https://github.com/tianocore/tianocore.github.io/wiki/Getting%20Started%20with%20EDK%20II) 
    - [Xcode](https://github.com/tianocore/tianocore.github.io/wiki/Xcode)
1. nasm (2.0 or above)
2. iasl (version 2018xxxx or later)
3. MSVC(Windows) or Xcode(Mac) or GCC(Open-source Posix)
4. build-essential uuid-dev (Posix)
5. pip2 install future (Optional)
6. motc (Xcode)

## Tool installation hints for any Debian-Based Linux:
 `$ sudo apt update ; sudo apt install nasm iasl build-essential uuid-dev`

## Usage: 
0. Change-directory to folder **Pug** .
1. (Optional) Edit config.py for the settings accordingly in: WORKSPACE, PLATFORM, TARGET_TXT, COMPONENTS.
2. Run `./pug.py` <br>
    pug.py would automatically try to git-clone the [edk2 code tree](https://github.com/tianocore/edk2) and the submodule, openssl for the 1st time.
3. Browse folder **\_pug\_** for the temporary files (.dsc/.inf) and folder **\_pug\_/Conf** for CONF_PATH settings files.
4. Browse folder **\.\./Build** for the build results.

## Additional use cases:
1. To build an edk2 package: (Taking OvmfPkg and ShellPkg for examples.)<br>
  `$ ./pug.py -p OvmfPkg/OvmfPkgX64.dsc`<br>
  `$ ./pug.py -p ShellPkg/ShellPkg.dsc`<br>
