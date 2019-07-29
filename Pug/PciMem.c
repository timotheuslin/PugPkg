/** @file

Dump the PCI Configuration Space of all PCI devices.


This is a demonstration source file using PUG.
Timothy Lin Jul/29/2019, BSD 3-Clause License.

**/


/*--PUG--INF--
[Defines]
    VERSION_STRING = 0.1
    BASE_NAME      = PciMem
    INF_VERSION    = 0x00010006
    ENTRY_POINT    = ShellCEntryLib
    MODULE_TYPE    = UEFI_APPLICATION
    FILE_GUID      = B532FD24-BA45-47E5-8C7D-1F3456DCF5B4

[Sources]
    PciMem.c

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
#include <Include/Protocol/PciIo.h>                 // gEfiPciIoProtocolGuid



VOID FreeHandleBuffer(EFI_HANDLE **h)
{
    if (*h) {
        FreePool(*h);
        *h = NULL;
    }
}


UINT8* PciRead256(EFI_PCI_IO_PROTOCOL *PciIo, UINT8 *buffer)
{
    int i;

    for (i=0; i<256; i++) {
        PciIo->Pci.Read (PciIo, EfiPciIoWidthUint8, i, 1, buffer+i);
    }
    return buffer;
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


void DumpPci(void)
{
    int i;
    UINTN HandleCount = 0;
    EFI_HANDLE *HandleBuffer = NULL;
    EFI_STATUS Status = EFI_NOT_FOUND;

    Status = gBS->LocateHandleBuffer(ByProtocol, &gEfiPciIoProtocolGuid, NULL, &HandleCount, &HandleBuffer);
    if (EFI_ERROR(Status)) {
        Print(L" Status: %r\n", Status);
        FreeHandleBuffer(&HandleBuffer);
        return;
    }
    Print(L"PCI IO Handle count: %d\n", HandleCount);
    for (i=0; i<HandleCount; i++) {
        UINT32 VidDid;
        UINT8 Cfg[256];
        UINT16 *ClassName=L"";
        UINTN Seg, Bus, Dev, Func;
        EFI_PCI_IO_PROTOCOL *PciIo;

        Status = gBS->HandleProtocol(HandleBuffer[i], &gEfiPciIoProtocolGuid, (void**)&PciIo);
	    if (EFI_ERROR(Status)) {
            Print(L"Handle: %X, Status: %r\n", HandleBuffer[i], Status);
	        continue;
	    }
        PciIo->GetLocation(PciIo, &Seg, &Bus, &Dev, &Func);
        PciIo->Pci.Read(PciIo, EfiPciIoWidthUint32, 0, 1, &VidDid);
        Print(L"%X:%02X.%02X.%X - ", Seg, Bus, Dev, Func);
        if (VidDid == 0xFFFFFFFF) {
            Print(L"FFFF:FFFF\n");
            continue;
        }
        PciRead256(PciIo, Cfg);

        Print(L"%04X:%04X - ", *(UINT16*)(Cfg), *(UINT16*)(Cfg+2));
        if (Cfg[0xB] == 6) {
            if (Cfg[0xA] == 4) {
                ClassName = L"P2P Bridge";
            }
            else {
                ClassName = L"Bridge";
            }
        }
        else {
            ClassName = L"Generic Device";
        }
        Print(L"%s\n", ClassName);
        HexDump(Cfg, 0x40);
        Print(L"\n");
    }
    FreeHandleBuffer(&HandleBuffer);
}


INTN EFIAPI ShellAppMain(
    IN UINTN Argc,
    IN CHAR16 **Argv)
{
    AsciiPrint(
        "PciCfgMem - Dump the PCI configuration space memory.\n"    \
        "Built: " __TIME__ " " __DATE__ "\n"                        \
        "https://github.com/timotheuslin\n\n"
    );
    DumpPci();
    return 0;
}
