## @file
##

[Defines]
  BUILD_TARGETS                  = DEBUG|RELEASE|NOOPT
  PLATFORM_GUID                  = f54ef133-c2ec-441e-a105-7fc1f5fdfbac
  PLATFORM_NAME                  = FooBarPkg
  OUTPUT_DIRECTORY               = Build_FooBarPkg
  PLATFORM_VERSION               = 0.1  
  SKUID_IDENTIFIER               = DEFAULT
  DSC_SPECIFICATION              = 0x00010006
  SUPPORTED_ARCHITECTURES        = IA32|X64|ARM|AARCH64

[LibraryClasses]
  PcdLib | MdePkg/Library/BasePcdLibNull/BasePcdLibNull.inf
  BaseLib | MdePkg/Library/BaseLib/BaseLib.inf
  UefiLib | MdePkg/Library/UefiLib/UefiLib.inf
  DebugLib | MdePkg/Library/BaseDebugLibNull/BaseDebugLibNull.inf
  PrintLib | MdePkg/Library/BasePrintLib/BasePrintLib.inf
  BaseMemoryLib | MdePkg/Library/BaseMemoryLibRepStr/BaseMemoryLibRepStr.inf
  DevicePathLib | MdePkg/Library/UefiDevicePathLibDevicePathProtocol/UefiDevicePathLibDevicePathProtocol.inf
  ShellCEntryLib | ShellPkg/Library/UefiShellCEntryLib/UefiShellCEntryLib.inf
  MemoryAllocationLib | MdePkg/Library/UefiMemoryAllocationLib/UefiMemoryAllocationLib.inf
  UefiBootServicesTableLib | MdePkg/Library/UefiBootServicesTableLib/UefiBootServicesTableLib.inf
  UefiApplicationEntryPoint | MdePkg/Library/UefiApplicationEntryPoint/UefiApplicationEntryPoint.inf
  UefiRuntimeServicesTableLib | MdePkg/Library/UefiRuntimeServicesTableLib/UefiRuntimeServicesTableLib.inf

[Components]
  I2CProtocols.inf