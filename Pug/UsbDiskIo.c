/** @file

Dump every USB disk's MBR (LBA block 0)

This is a demonstration source file using PUG.
Timothy Lin Dec/19/2019, BSD 3-Clause License.

**/


/*--PUG--INF--
[Defines]
    VERSION_STRING = 0.1
    BASE_NAME      = UsbDiskIo
    INF_VERSION    = 0x00010006
    ENTRY_POINT    = ShellCEntryLib
    MODULE_TYPE    = UEFI_APPLICATION
    FILE_GUID      = 13ADEDF5-EA5D-4ADE-BA4D-263B0645ECF2

[Sources]
    UsbDiskIo.c

[Packages]
    MdePkg/MdePkg.dec
    ShellPkg/ShellPkg.dec

[Protocols]
    gEfiPciIoProtocolGuid

[LibraryClasses]
    MdePkg/Library/BaseLib/BaseLib.inf
    MdePkg/Library/UefiLib/UefiLib.inf
    MdePkg/Library/BasePrintLib/BasePrintLib.inf
    MdePkg/Library/BasePcdLibNull/BasePcdLibNull.inf
    MdePkg/Library/BaseDebugLibNull/BaseDebugLibNull.inf
    MdePkg/Library/BaseMemoryLibRepStr/BaseMemoryLibRepStr.inf
    ShellPkg/Library/UefiShellCEntryLib/UefiShellCEntryLib.inf
    MdePkg/Library/UefiMemoryAllocationLib/UefiMemoryAllocationLib.inf
    MdePkg/Library/UefiBootServicesTableLib/UefiBootServicesTableLib.inf
    MdePkg/Library/UefiApplicationEntryPoint/UefiApplicationEntryPoint.inf
    MdePkg/Library/UefiRuntimeServicesTableLib/UefiRuntimeServicesTableLib.in
    MdePkg/Library/UefiDevicePathLibDevicePathProtocol/UefiDevicePathLibDevicePathProtocol.inf
*/


#include <Library/BaseLib.h>                        // MdePkg/Library/BaseLib/BaseLib.inf
#include <Library/UefiLib.h>                        // MdePkg/Library/UefiLib/UefiLib.inf
                                                    // MdePkg/Library/BasePrintLib/BasePrintLib.inf
                                                    // MdePkg/Library/UefiDevicePathLibDevicePathProtocol/UefiDevicePathLibDevicePathProtocol.inf
                                                    // MdePkg/Library/BasePcdLibNull/BasePcdLibNull.inf
                                                    // MdePkg/Library/BaseDebugLibNull/BaseDebugLibNull.inf
#include <Library/BaseMemoryLib.h>                  // MdePkg/Library/BaseMemoryLibRepStr/BaseMemoryLibRepStr.inf
#include <Library/ShellCEntryLib.h>                 // ShellPkg/Library/UefiShellCEntryLib/UefiShellCEntryLib.inf
                                                    // MdePkg/Library/UefiApplicationEntryPoint/UefiApplicationEntryPoint.inf
#include <Library/MemoryAllocationLib.h>            // MdePkg/Library/UefiMemoryAllocationLib/UefiMemoryAllocationLib.inf
#include <Library/UefiBootServicesTableLib.h>       // MdePkg/Library/UefiBootServicesTableLib/UefiBootServicesTableLib.inf
#include <Library/UefiRuntimeServicesTableLib.h>    // MdePkg/Library/UefiRuntimeServicesTableLib/UefiRuntimeServicesTableLib.inf

#include <Protocol/UsbIo.h>
#include <Protocol/DiskIo.h>
#include <Protocol/BlockIo.h>
#include <IndustryStandard/Mbr.h>



VOID FreeHandleBuffer(EFI_HANDLE **h)
{
    if (*h) {
        FreePool(*h);
        *h = NULL;
    }
}


void HexDump(UINT8 *buffer, int len)
{
    int i;

    for (i=0; i<len; i++) {
        Print(L"%02X ", buffer[i]);
        if (i%16 == 15) {
            Print(L"\n");
        }
    }
}


void UsbDiskIo(void)
{
    int i;
    UINTN HandleCount = 0;
    EFI_HANDLE *HandleBuffer = NULL;
    EFI_STATUS Status = EFI_NOT_FOUND;

    Status = gBS->LocateHandleBuffer(ByProtocol, &gEfiUsbIoProtocolGuid, NULL, &HandleCount, &HandleBuffer);
    if (EFI_ERROR(Status)) {
        Print(L" Status: %r\n", Status);
        FreeHandleBuffer(&HandleBuffer);
        return;
    }
    Print(L"USB IO Handle count: %d\n", HandleCount);
    for (i=0; i<HandleCount; i++) {
        EFI_USB_IO_PROTOCOL *UsbIo;
        EFI_DISK_IO_PROTOCOL *DiskIo;
        EFI_BLOCK_IO_PROTOCOL *BlockIo;
        MASTER_BOOT_RECORD Mbr;

        Status = gBS->HandleProtocol(HandleBuffer[i], &gEfiUsbIoProtocolGuid, (void**)&UsbIo);
        if (EFI_ERROR(Status)) {
            Print(L"Handle: %X, Status: %r\n", HandleBuffer[i], Status);
            continue;
        }
        Status = gBS->HandleProtocol(HandleBuffer[i], &gEfiDiskIoProtocolGuid, (void**)&DiskIo);
        if (EFI_ERROR(Status)) {
            continue;
        }
       Status = gBS->HandleProtocol(HandleBuffer[i], &gEfiBlockIoProtocolGuid, (void**)&BlockIo);
        if (EFI_ERROR(Status)) {
            continue;
        }
        Print(L"UsbIo/DiskIO/BlockIo Handle: %X\n", HandleBuffer[i]);

        DiskIo->ReadDisk(DiskIo, BlockIo->Media->MediaId, 0, sizeof(Mbr), (void*)&Mbr);
        HexDump((void*)&Mbr, sizeof(Mbr));

        Print(L"\n");
    }
    FreeHandleBuffer(&HandleBuffer);
}


INTN EFIAPI ShellAppMain(
    IN UINTN Argc,
    IN CHAR16 **Argv)
{
    AsciiPrint(
        "UsbDiskIo - Dump USB disk's MBR.\n"    \
        "Built: " __TIME__ " " __DATE__ "\n"                        \
        "https://github.com/timotheuslin\n\n"
    );
    UsbDiskIo();
    return 0;
}
