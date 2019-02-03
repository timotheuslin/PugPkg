#
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, line-too-long

"""config.py"""
import os

# Basic global settings for all the workspace.
# The relative path are based from current-working-dir
WORKSPACE = {
    "path"              : os.environ.get("WORKSPACE", ".."),
    "udk_dir"           : "../edk2",
    "udk_url"           : "https://github.com/tianocore/edk2.git",
    "output_directory"  : "Build/FooBarZ",
    "platform_name"     : "FooBarPkg",
    "target_arch"       : "X64",            #"IA32 X64"
    "tool_chain_tag"    : "GCC5",           #"VS2012x86"
    "target"            : "RELEASE",        # DEBUG, NOOPT
}
WORKSPACE["conf_path"] = os.environ.get("CONF_PATH", "%s/%s" % (WORKSPACE["path"], 'Conf'))

#
# PLATFORM DSC's content.
# The relative path are based from $(WORKSPACE)
PLATFORM = {
    "path"                          : "%s/%s.dsc" % (WORKSPACE["output_directory"], WORKSPACE["platform_name"]),
    "Defines"                       : {
        "PLATFORM_GUID"             : "f54ef133-c2ec-441e-a105-7fc1f5fdfbac",
        "OUTPUT_DIRECTORY"          : WORKSPACE["output_directory"],
        "PLATFORM_NAME"             : WORKSPACE["platform_name"],
        "BUILD_TARGETS"             : "DEBUG|RELEASE|NOOPT",
        "PLATFORM_VERSION"          : "0.1",
        "SKUID_IDENTIFIER"          : "DEFAULT",
        "DSC_SPECIFICATION"         : "0x00010006",
        "SUPPORTED_ARCHITECTURES"   : "IA32|X64|ARM|AARCH64",
    },
}


# Conf/target.txt
# Ref. BaseTools/Conf/target.template
# The relative path are based from $(WORKSPACE)
TARGET_TXT = {
    "path"              : "%s/%s" % (WORKSPACE["conf_path"], 'target.txt'),
    "TOOL_CHAIN_CONF"   : "Conf/tools_def.txt",
    "BUILD_RULE_CONF"   : "Conf/build_rule.txt",
    "ACTIVE_PLATFORM"   : PLATFORM["path"],
    "TARGET"            : WORKSPACE["target"],
    "TARGET_ARCH"       : WORKSPACE["target_arch"],
    "TOOL_CHAIN_TAG"    : WORKSPACE["tool_chain_tag"]
}


# The relative path are based from $(WORKSPACE)
COMPONENTS = {
    "I2CProtocols.inf" : {
        "path" : WORKSPACE["output_directory"] + "/I2CProtocols.inf",
        "source_dir" : os.path.basename(os.getcwd()),
        "Defines" : {
            "VERSION_STRING": "0.1",
            "INF_VERSION":    "0x00010006",
            "BASE_NAME":      "I2CProtocols",
            "MODULE_TYPE":    "UEFI_APPLICATION",
            "ENTRY_POINT":    "ShellCEntryLib",
            "FILE_GUID":      "92e7ac00-49bc-47dd-9790-f1dec616981d"
        },
        "Sources" : [
            "I2CProtocols.c"
        ],
        "Packages" : [
            "MdePkg/MdePkg.dec",
            "ShellPkg/ShellPkg.dec"
        ],
        "Protocols" : [
            "gEfiI2cIoProtocolGuid",
            "gEfiI2cHostProtocolGuid",
            "gEfiI2cMasterProtocolGuid",
            "gEfiI2cEnumerateProtocolGuid",
            "gEfiI2cBusConfigurationManagementProtocolGuid",
            "gEfiPciIoProtocolGuid",
            "gEfiUsb2HcProtocolGuid",
            "gEfiUsbHcProtocolGuid",
            "gEfiUsbIoProtocolGuid",
            "gEfiUsbFunctionIoProtocolGuid",
            "gEfiDriverBindingProtocolGuid",
            "gEfiComponentName2ProtocolGuid",
            "gEfiPciRootBridgeIoProtocolGuid"
        ],
        "LibraryClasses" : {
            "PcdLib": "MdePkg/Library/BasePcdLibNull/BasePcdLibNull.inf",
            "BaseLib": "MdePkg/Library/BaseLib/BaseLib.inf",
            "UefiLib": "MdePkg/Library/UefiLib/UefiLib.inf",
            "DebugLib": "MdePkg/Library/BaseDebugLibNull/BaseDebugLibNull.inf",
            "PrintLib": "MdePkg/Library/BasePrintLib/BasePrintLib.inf",
            "BaseMemoryLib": "MdePkg/Library/BaseMemoryLibRepStr/BaseMemoryLibRepStr.inf",
            "DevicePathLib": "MdePkg/Library/UefiDevicePathLibDevicePathProtocol/UefiDevicePathLibDevicePathProtocol.inf",
            "ShellCEntryLib": "ShellPkg/Library/UefiShellCEntryLib/UefiShellCEntryLib.inf",
            "MemoryAllocationLib": "MdePkg/Library/UefiMemoryAllocationLib/UefiMemoryAllocationLib.inf",
            "UefiBootServicesTableLib": "MdePkg/Library/UefiBootServicesTableLib/UefiBootServicesTableLib.inf",
            "UefiApplicationEntryPoint": "MdePkg/Library/UefiApplicationEntryPoint/UefiApplicationEntryPoint.inf",
            "UefiRuntimeServicesTableLib": "MdePkg/Library/UefiRuntimeServicesTableLib/UefiRuntimeServicesTableLib.inf"
        }
    }
}
