#
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, line-too-long

"""config.py

TODO:
1. automate the LibraryClasses content of the existing INF using info from:
     1.1 their static_library_files.lst, and
     1.2 their $(BASE_NAME).map - "Linker script and memory map"
2. automate the global/local (fixed) PCD settings from the -y/-Y build log.
"""

import os

# Basic global settings for all the workspace.
# The relative-paths are relative to the current-working-dir.
WORKSPACE = {
    "path"              : os.environ.get("WORKSPACE", ".."),
    "udk_dir"           : "../edk2",
    "udk_url"           : "https://github.com/tianocore/edk2.git",
    "output_directory"  : "Build/Pug",
    "platform_name"     : "Pug",
    "target_arch"       : "X64",            # "IA32", "X64", "IA32 X64"
    "tool_chain_tag"    : "GCC5",           # "VS2012x86"
    "target"            : "RELEASE",        # "DEBUG", "NOOPT"
    "log_type"          : "PCD",            # PCD, LIBRARY, FLASH, DEPEX, HASH, BUILD_FLAGS, FIXED_ADDRESS
    "tmp_dir"           : os.path.abspath("_pug_"),
}

WORKSPACE["conf_path"] = os.environ.get("CONF_PATH", WORKSPACE["tmp_dir"] + "/Conf")
WORKSPACE["report_log"] = WORKSPACE["output_directory"] + "/build_report.log"

# [WORKAROUND] disable logging due to the failure of report-log under Windows.
if os.name == 'nt':
    WORKSPACE['report_log'] = ''

#
# PLATFORM DSC's content.
# The relative-paths are relative to entries in {$(WORKSPACE), $(PACKAGES_PATH)}
PLATFORM = {
    "path"                          : WORKSPACE["tmp_dir"] + "/" + WORKSPACE["platform_name"] + '.dsc',
    "update"                        : True,
    "Defines"                       : {
        "PLATFORM_GUID"             : "24e4eeb9-7566-4a41-a268-794dbf5bc58b",
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
# The relative-paths are relative to entries in {$(WORKSPACE), $(PACKAGES_PATH)}
TARGET_TXT = {
    "path"              : WORKSPACE["conf_path"] + "/" + "target.txt",
    "update"            : True,
    "TOOL_CHAIN_CONF"   : "tools_def.txt",
    "BUILD_RULE_CONF"   : "build_rule.txt",
    "ACTIVE_PLATFORM"   : PLATFORM["path"],
    "TARGET"            : WORKSPACE["target"],
    "TARGET_ARCH"       : WORKSPACE["target_arch"],
    "TOOL_CHAIN_TAG"    : WORKSPACE["tool_chain_tag"]
}


# An EFI application written from scratch.
I2CProtocols_INF = {
    "path" : WORKSPACE["tmp_dir"] + "/I2CProtocols.inf",
    "update" : True,
    "Defines" : {
        "VERSION_STRING": "0.1",
        "INF_VERSION":    "0x00010006",
        "BASE_NAME":      "I2CProtocols",
        "MODULE_TYPE":    "UEFI_APPLICATION",
        "ENTRY_POINT":    "ShellCEntryLib",
        "FILE_GUID":      "a05e1015-cdca-493d-a79d-55a2e4805988",
    },
    "Sources" : [
        os.path.basename(os.getcwd()) + "/I2CProtocols.c"
    ],
    "Packages" : [
        "MdePkg/MdePkg.dec",
        "ShellPkg/ShellPkg.dec",
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
    "LibraryClasses" : [
        ["PcdLib", "MdePkg/Library/BasePcdLibNull/BasePcdLibNull.inf",],
        ["BaseLib", "MdePkg/Library/BaseLib/BaseLib.inf",],
        ["UefiLib", "MdePkg/Library/UefiLib/UefiLib.inf",],
        ["DebugLib", "MdePkg/Library/BaseDebugLibNull/BaseDebugLibNull.inf",],
        ["PrintLib", "MdePkg/Library/BasePrintLib/BasePrintLib.inf",],
        ["BaseMemoryLib", "MdePkg/Library/BaseMemoryLibRepStr/BaseMemoryLibRepStr.inf",],
        ["DevicePathLib", "MdePkg/Library/UefiDevicePathLibDevicePathProtocol/UefiDevicePathLibDevicePathProtocol.inf",],
        ["ShellCEntryLib", "ShellPkg/Library/UefiShellCEntryLib/UefiShellCEntryLib.inf",],
        ["MemoryAllocationLib", "MdePkg/Library/UefiMemoryAllocationLib/UefiMemoryAllocationLib.inf",],
        ["UefiBootServicesTableLib", "MdePkg/Library/UefiBootServicesTableLib/UefiBootServicesTableLib.inf",],
        ["UefiApplicationEntryPoint", "MdePkg/Library/UefiApplicationEntryPoint/UefiApplicationEntryPoint.inf",],
        ["UefiRuntimeServicesTableLib", "MdePkg/Library/UefiRuntimeServicesTableLib/UefiRuntimeServicesTableLib.inf"],
    ],
}

# OvmfPkg/ResetVector/ResetVector.inf
ResetVector_INF_dir = "OvmfPkg/ResetVector/"
ResetVector_INF = {
    "path" : WORKSPACE["tmp_dir"] + "/ResetVector.inf",
    "update" : True,
    "Defines" : {
        "INF_VERSION"       : "0x00010005",
        "BASE_NAME"         : "ResetVector",
        "FILE_GUID"         : "1BA0062E-C779-4582-8566-336AE8F78F09",
        "MODULE_TYPE"       : "SEC",
        "VERSION_STRING"    : "1.1",
    },
    "Sources" : [
        ResetVector_INF_dir + "ResetVector.nasmb"
    ],
    "Packages" : [
        "OvmfPkg/OvmfPkg.dec",
        "MdePkg/MdePkg.dec",
        "UefiCpuPkg/UefiCpuPkg.dec",
    ],
    "BuildOptions" : [
        ["*_*_IA32_NASMB_FLAGS", "-I$(WORKSPACE)/UefiCpuPkg/ResetVector/Vtf0/"],
        ["*_*_X64_NASMB_FLAGS", "-I$(WORKSPACE)/UefiCpuPkg/ResetVector/Vtf0/"],
    ],
    "Pcd" : [
        "gUefiOvmfPkgTokenSpaceGuid.PcdOvmfSecPageTablesBase",
        "gUefiOvmfPkgTokenSpaceGuid.PcdOvmfSecPageTablesSize",
    ],
    # Ref. OvmfPkg/OvmfPkg{Ia32, X64, Ia32X64}.fdf
    "PcdsFixedAtBuild" : [
        ["gUefiOvmfPkgTokenSpaceGuid.PcdOvmfSecPageTablesBase", 0],
        ["gUefiOvmfPkgTokenSpaceGuid.PcdOvmfSecPageTablesSize", 0x6000],
    ]
}

# OvmfPkg/PlatformDxe/Platform.inf
Platform_INF = {
    "path" : WORKSPACE["tmp_dir"] + "/Platform.inf",
    "update" : True,
    "Defines" : [
        "INF_VERSION                    = 0x00010005",
        "BASE_NAME                      = PlatformDxe",
        "FILE_GUID                      = D9DCC5DF-4007-435E-9098-8970935504B2",
        "MODULE_TYPE                    = DXE_DRIVER",
        "VERSION_STRING                 = 1.0",
        "ENTRY_POINT                    = PlatformInit",
        "UNLOAD_IMAGE                   = PlatformUnload",
    ],
    "Sources" : [
        "OvmfPkg/PlatformDxe/Platform.c",
        "OvmfPkg/PlatformDxe/Platform.h",
        "OvmfPkg/PlatformDxe/Platform.uni",
        "OvmfPkg/PlatformDxe/PlatformConfig.c",
        "OvmfPkg/PlatformDxe/PlatformConfig.h",
        "OvmfPkg/PlatformDxe/PlatformForms.vfr",
    ],
    "Packages" : [
        "MdePkg/MdePkg.dec",
        "MdeModulePkg/MdeModulePkg.dec",
        "OvmfPkg/OvmfPkg.dec",
    ],
    "LibraryClasses" : [
        ["BaseLib", "MdePkg/Library/BaseLib/BaseLib.inf"],
        ["BaseMemoryLib", "MdePkg/Library/BaseMemoryLibRepStr/BaseMemoryLibRepStr.inf"],
        #["DebugLib", "OvmfPkg/Library/PlatformDebugLibIoPort/PlatformDebugLibIoPort.inf"],
        ["DebugLib", "MdePkg/Library/BaseDebugLibNull/BaseDebugLibNull.inf"],
        ["PcdLib", "MdePkg/Library/DxePcdLib/DxePcdLib.inf"],
        ["DevicePathLib", "MdePkg/Library/UefiDevicePathLib/UefiDevicePathLib.inf"],
        ["HiiLib", "MdeModulePkg/Library/UefiHiiLib/UefiHiiLib.inf"],
        ["MemoryAllocationLib", "MdePkg/Library/UefiMemoryAllocationLib/UefiMemoryAllocationLib.inf"],
        ["PrintLib", "MdePkg/Library/BasePrintLib/BasePrintLib.inf",],
        ["UefiBootServicesTableLib", "MdePkg/Library/UefiBootServicesTableLib/UefiBootServicesTableLib.inf",],
        ["UefiHiiServicesLib", "MdeModulePkg/Library/UefiHiiServicesLib/UefiHiiServicesLib.inf"],
        ["UefiLib", "MdePkg/Library/UefiLib/UefiLib.inf",],
        ["UefiRuntimeServicesTableLib", "MdePkg/Library/UefiRuntimeServicesTableLib/UefiRuntimeServicesTableLib.inf"],
        ["UefiDriverEntryPoint", "MdePkg/Library/UefiDriverEntryPoint/UefiDriverEntryPoint.inf"],
    ],
    "Pcd" : [
        "gEfiMdeModulePkgTokenSpaceGuid.PcdVideoHorizontalResolution",
        "gEfiMdeModulePkgTokenSpaceGuid.PcdVideoVerticalResolution",
    ],
    "Protocols" : [
        "gEfiDevicePathProtocolGuid",      ## PRODUCES
        "gEfiGraphicsOutputProtocolGuid",  ## CONSUMES
        "gEfiHiiConfigAccessProtocolGuid", ## PRODUCES
    ],
    "Guids" : [
        "gEfiIfrTianoGuid",
        "gOvmfPlatformConfigGuid",
    ],
    "Depex" : [
        "gEfiHiiConfigRoutingProtocolGuid  AND",
        "gEfiHiiDatabaseProtocolGuid       AND",
        "gEfiVariableArchProtocolGuid      AND",
        "gEfiVariableWriteArchProtocolGuid",
    ],
}

# NetworkPkg/Application/IpsecConfig/IpSecConfig.inf
IpSecConfig_INF = {
    "path" : WORKSPACE["tmp_dir"] + "/IpSecConfig.inf",
    "arch" : "X64",
    "update" : True,
    "Defines" : [
        "INF_VERSION                    = 0x00010006",
        "BASE_NAME                      = IpSecConfig",
        "FILE_GUID                      = 0922E604-F5EC-42ef-980D-A35E9A2B1844",
        "MODULE_TYPE                    = UEFI_APPLICATION",
        "VERSION_STRING                 = 1.0",
        "ENTRY_POINT                    = InitializeIpSecConfig",
        "MODULE_UNI_FILE                = IpSecConfig.uni",
        "#",
        "#",
        "#  This flag specifies whether HII resource section is generated into PE image.",
        "#",
        "UEFI_HII_RESOURCE_SECTION      = TRUE",
    ],
    "Sources" : [
        "NetworkPkg/Application/IpsecConfig/IpSecConfigStrings.uni",
        "NetworkPkg/Application/IpsecConfig/IpSecConfig.c",
        "NetworkPkg/Application/IpsecConfig/IpSecConfig.h",
        "NetworkPkg/Application/IpsecConfig/Dump.c",
        "NetworkPkg/Application/IpsecConfig/Dump.h",
        "NetworkPkg/Application/IpsecConfig/Indexer.c",
        "NetworkPkg/Application/IpsecConfig/Indexer.h",
        "NetworkPkg/Application/IpsecConfig/Match.c",
        "NetworkPkg/Application/IpsecConfig/Match.h",
        "NetworkPkg/Application/IpsecConfig/Delete.h",
        "NetworkPkg/Application/IpsecConfig/Delete.c",
        "NetworkPkg/Application/IpsecConfig/Helper.c",
        "NetworkPkg/Application/IpsecConfig/Helper.h",
        "NetworkPkg/Application/IpsecConfig/ForEach.c",
        "NetworkPkg/Application/IpsecConfig/ForEach.h",
        "NetworkPkg/Application/IpsecConfig/PolicyEntryOperation.c",
        "NetworkPkg/Application/IpsecConfig/PolicyEntryOperation.h",
    ],
    "Packages" : [
        "MdePkg/MdePkg.dec",
        "MdeModulePkg/MdeModulePkg.dec",
        "ShellPkg/ShellPkg.dec",
    ],
    "Protocols" : [
        "gEfiIpSec2ProtocolGuid",
        "gEfiIpSecConfigProtocolGuid",
        "gEfiHiiPackageListProtocolGuid",
    ],
    'UserExtensions.TianoCore."ExtraFiles"' : [
        "NetworkPkg/Application/IpsecConfig/IpSecConfigExtra.uni"
    ],
    "LibraryClasses" : [
        ["UefiBootServicesTableLib", "MdePkg/Library/UefiBootServicesTableLib/UefiBootServicesTableLib.inf"],
        ["UefiApplicationEntryPoint", "MdePkg/Library/UefiApplicationEntryPoint/UefiApplicationEntryPoint.inf"],
        ["UefiHiiServicesLib", "MdeModulePkg/Library/UefiHiiServicesLib/UefiHiiServicesLib.inf"],
        ["BaseMemoryLib", "MdePkg/Library/BaseMemoryLibRepStr/BaseMemoryLibRepStr.inf"],
        ["ShellLib", "ShellPkg/Library/UefiShellLib/UefiShellLib.inf"],
        ["MemoryAllocationLib", "MdePkg/Library/UefiMemoryAllocationLib/UefiMemoryAllocationLib.inf",],
        ["DebugLib", "MdePkg/Library/BaseDebugLibNull/BaseDebugLibNull.inf",],
        #["DebugLib", "MdePkg/Library/UefiDebugLibStdErr/UefiDebugLibStdErr.inf",],
        ["HiiLib", "MdeModulePkg/Library/UefiHiiLib/UefiHiiLib.inf"],
        ["NetLib", "MdeModulePkg/Library/DxeNetLib/DxeNetLib.inf"],
        ["UefiLib", "MdePkg/Library/UefiLib/UefiLib.inf",],
        ["PrintLib", "MdePkg/Library/BasePrintLib/BasePrintLib.inf",],
        ["PcdLib", "MdePkg/Library/DxePcdLib/DxePcdLib.inf"],
        ["BaseLib", "MdePkg/Library/BaseLib/BaseLib.inf"],
        ["DevicePathLib", "MdePkg/Library/UefiDevicePathLib/UefiDevicePathLib.inf"],
        ["UefiRuntimeServicesTableLib", "MdePkg/Library/UefiRuntimeServicesTableLib/UefiRuntimeServicesTableLib.inf"],
        ["FileHandleLib", "MdePkg/Library/UefiFileHandleLib/UefiFileHandleLib.inf"],
        ["SortLib", "MdeModulePkg/Library/UefiSortLib/UefiSortLib.inf"],
    ]
}

# ShellPkg/Application/Shell/Shell.inf
Shell_INF_dir = "ShellPkg/Application/Shell/"
Shell_NO_SHELL_PROFILES = 0
Shell_INF = {
    "path" : WORKSPACE["tmp_dir"] + "/Shell.inf",
    "arch" : "X64",
    "update" : True,
    "Defines" : {
        "INF_VERSION" :     "0x00010006",
        "BASE_NAME" :       "Shell",
        "FILE_GUID" :       "7C04A583-9E3E-4f1c-AD65-E05268D0B4D1", # gUefiShellFileGuid
        "MODULE_TYPE" :     "UEFI_APPLICATION",
        "VERSION_STRING" :  "1.0",
        "ENTRY_POINT" :     "UefiMain",
    },
    "Sources" : [
        Shell_INF_dir  + "Shell.c",
        Shell_INF_dir  + "Shell.h",
        Shell_INF_dir  + "ShellParametersProtocol.c",
        Shell_INF_dir  + "ShellParametersProtocol.h",
        Shell_INF_dir  + "ShellProtocol.c",
        Shell_INF_dir  + "ShellProtocol.h",
        Shell_INF_dir  + "FileHandleWrappers.c",
        Shell_INF_dir  + "FileHandleWrappers.h",
        Shell_INF_dir  + "FileHandleInternal.h",
        Shell_INF_dir  + "ShellEnvVar.c",
        Shell_INF_dir  + "ShellEnvVar.h",
        Shell_INF_dir  + "ShellManParser.c",
        Shell_INF_dir  + "ShellManParser.h",
        #Shell_INF_dir  + "Shell.uni",
        os.path.basename(os.getcwd()) + "/Shell.uni",
        Shell_INF_dir  + "ConsoleLogger.c",
        Shell_INF_dir  + "ConsoleLogger.h",
        Shell_INF_dir  + "ConsoleWrappers.c",
        Shell_INF_dir  + "ConsoleWrappers.h",
    ],
    "Packages" : [
        "MdePkg/MdePkg.dec",
        "ShellPkg/ShellPkg.dec",
        "MdeModulePkg/MdeModulePkg.dec",
    ],
    "PcdsFixedAtBuild" : [
        ["gEfiShellPkgTokenSpaceGuid.PcdShellLibAutoInitialize", "FALSE"],
        ["gEfiShellPkgTokenSpaceGuid.PcdShellProfileMask", "0x00"] if Shell_NO_SHELL_PROFILES else [],
    ],
    "LibraryClasses" : [
        ["BaseLib", "MdePkg/Library/BaseLib/BaseLib.inf",],
        ["UefiApplicationEntryPoint", "MdePkg/Library/UefiApplicationEntryPoint/UefiApplicationEntryPoint.inf",],
        ["UefiLib", "MdePkg/Library/UefiLib/UefiLib.inf",],
        ["DebugLib", "MdePkg/Library/BaseDebugLibNull/BaseDebugLibNull.inf",],
        ["MemoryAllocationLib", "MdePkg/Library/UefiMemoryAllocationLib/UefiMemoryAllocationLib.inf",],
        ["ShellCommandLib", "ShellPkg/Library/UefiShellCommandLib/UefiShellCommandLib.inf"],
        ["UefiRuntimeServicesTableLib", "MdePkg/Library/UefiRuntimeServicesTableLib/UefiRuntimeServicesTableLib.inf"],
        ["UefiBootServicesTableLib", "MdePkg/Library/UefiBootServicesTableLib/UefiBootServicesTableLib.inf",],
        ["DevicePathLib", "MdePkg/Library/UefiDevicePathLibDevicePathProtocol/UefiDevicePathLibDevicePathProtocol.inf",],
        ["BaseMemoryLib", "MdePkg/Library/BaseMemoryLibRepStr/BaseMemoryLibRepStr.inf",],
        ["PcdLib", "MdePkg/Library/BasePcdLibNull/BasePcdLibNull.inf",],
        ["FileHandleLib", "MdePkg/Library/UefiFileHandleLib/UefiFileHandleLib.inf"],
        ["PrintLib", "MdePkg/Library/BasePrintLib/BasePrintLib.inf",],
        ["HiiLib", "MdeModulePkg/Library/UefiHiiLib/UefiHiiLib.inf"],
        ["SortLib", "MdeModulePkg/Library/UefiSortLib/UefiSortLib.inf"],
        ["HandleParsingLib", "ShellPkg/Library/UefiHandleParsingLib/UefiHandleParsingLib.inf"],
        ["UefiHiiServicesLib", "MdeModulePkg/Library/UefiHiiServicesLib/UefiHiiServicesLib.inf"],
        ["ShellLib", "ShellPkg/Library/UefiShellLib/UefiShellLib.inf"],
        ["PeCoffGetEntryPointLib", "MdePkg/Library/BasePeCoffGetEntryPointLib/BasePeCoffGetEntryPointLib.inf"],
        ["NULL", "ShellPkg/Library/UefiShellLevel2CommandsLib/UefiShellLevel2CommandsLib.inf"],
        ["NULL", "ShellPkg/Library/UefiShellLevel1CommandsLib/UefiShellLevel1CommandsLib.inf"],
        ["NULL", "ShellPkg/Library/UefiShellLevel3CommandsLib/UefiShellLevel3CommandsLib.inf"],

        ["IoLib", "MdePkg/Library/BaseIoLibIntrinsic/BaseIoLibIntrinsic.inf"],
        ["NetLib", "MdeModulePkg/Library/DxeNetLib/DxeNetLib.inf"],
        ["BcfgCommandLib", "ShellPkg/Library/UefiShellBcfgCommandLib/UefiShellBcfgCommandLib.inf"],
        ["UefiBootManagerLib", "MdeModulePkg/Library/UefiBootManagerLib/UefiBootManagerLib.inf"],
        ["HobLib", "MdePkg/Library/DxeHobLib/DxeHobLib.inf"],
        ["PerformanceLib", "MdePkg/Library/BasePerformanceLibNull/BasePerformanceLibNull.inf"],
        ["DxeServicesTableLib", "MdePkg/Library/DxeServicesTableLib/DxeServicesTableLib.inf"],
        ["DxeServicesLib", "MdePkg/Library/DxeServicesLib/DxeServicesLib.inf"],
        ["ReportStatusCodeLib", "MdePkg/Library/BaseReportStatusCodeLibNull/BaseReportStatusCodeLibNull.inf"],
    ],
    "Guids" : [
        "gShellVariableGuid",   ## SOMETIMES_CONSUMES ## GUID
        "gShellAliasGuid",      ## SOMETIMES_CONSUMES ## GUID
        "gShellAliasGuid",      ## SOMETIMES_PRODUCES ## GUID
    ],
    "Protocols" : [
        "gEfiShellProtocolGuid",                                   ## PRODUCES
                                                                   ## SOMETIMES_CONSUMES
        "gEfiShellParametersProtocolGuid",                         ## PRODUCES
                                                                   ## SOMETIMES_CONSUMES
        "gEfiSimpleTextInputExProtocolGuid",                       ## CONSUMES
        "gEfiSimpleTextInProtocolGuid",                            ## CONSUMES
        "gEfiSimpleTextOutProtocolGuid",                           ## CONSUMES
        "gEfiSimpleFileSystemProtocolGuid",                        ## SOMETIMES_CONSUMES
        "gEfiLoadedImageProtocolGuid",                             ## CONSUMES
        "gEfiComponentName2ProtocolGuid",                          ## SOMETIMES_CONSUMES
        "gEfiUnicodeCollation2ProtocolGuid",                       ## CONSUMES
        "gEfiDevicePathProtocolGuid",                              ## CONSUMES
        "gEfiHiiPackageListProtocolGuid",                          ## SOMETIMES_PRODUCES
    ],
    "Pcd" : [
        "gEfiShellPkgTokenSpaceGuid.PcdShellSupportLevel",           ## CONSUMES
        "gEfiShellPkgTokenSpaceGuid.PcdShellSupportOldProtocols",    ## CONSUMES
        "gEfiShellPkgTokenSpaceGuid.PcdShellRequireHiiPlatform",     ## CONSUMES
        "gEfiShellPkgTokenSpaceGuid.PcdShellSupportFrameworkHii",    ## CONSUMES
        "gEfiShellPkgTokenSpaceGuid.PcdShellPageBreakDefault",       ## CONSUMES
        "gEfiShellPkgTokenSpaceGuid.PcdShellInsertModeDefault",      ## CONSUMES
        "gEfiShellPkgTokenSpaceGuid.PcdShellScreenLogCount",         ## CONSUMES
        "gEfiShellPkgTokenSpaceGuid.PcdShellPrintBufferSize",        ## CONSUMES
        "gEfiShellPkgTokenSpaceGuid.PcdShellForceConsole",           ## CONSUMES
        "gEfiShellPkgTokenSpaceGuid.PcdShellSupplier",               ## CONSUMES
        "gEfiShellPkgTokenSpaceGuid.PcdShellMaxHistoryCommandCount", ## CONSUMES
    ]
}

# Ref. ShellPkg/Application/Shell/*.dsc
if not Shell_NO_SHELL_PROFILES:
    Shell_INF["LibraryClasses"] += [
        ["NULL", "ShellPkg/Library/UefiShellDriver1CommandsLib/UefiShellDriver1CommandsLib.inf"],
        ["NULL", "ShellPkg/Library/UefiShellInstall1CommandsLib/UefiShellInstall1CommandsLib.inf"],
        ["NULL", "ShellPkg/Library/UefiShellDebug1CommandsLib/UefiShellDebug1CommandsLib.inf"],
        ["NULL", "ShellPkg/Library/UefiShellNetwork1CommandsLib/UefiShellNetwork1CommandsLib.inf"],
        ["NULL", "ShellPkg/Library/UefiShellNetwork2CommandsLib/UefiShellNetwork2CommandsLib.inf"],
    ]


COMPONENTS = [
    ResetVector_INF,
    I2CProtocols_INF,
    Platform_INF,
    IpSecConfig_INF,
    Shell_INF,
]
