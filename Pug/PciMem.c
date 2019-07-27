/** @file

Dump the PCI Configuration Space

**/
#include <Uefi.h>
#include <Library/UefiLib.h>
#include <Library/ShellCEntryLib.h>
#include <Library/UefiBootServicesTableLib.h>
#include <Library/UefiRuntimeServicesTableLib.h>
#include <Library/BaseMemoryLib.h>
#include <Library/MemoryAllocationLib.h>
#include <Library/BaseLib.h>


#include <Include/Protocol/ComponentName2.h>
#include <Include/Protocol/PciRootBridgeIo.h>
#include <Include/Protocol/PciIo.h>


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

void DumpPPB(UINT8 *cfg){
    Print(L"BAR0: %08X\n", *(UINT32*)(cfg+0x10));
    Print(L"BAR1: %08X\n", *(UINT32*)(cfg+0x14));
    Print(L"Pri/Sec/Sub BUS: %02x/%02X/%02X\n", *(cfg+0x18), *(cfg+0x19), *(cfg+0x1a));
    Print(L"I/O Base : %02X00\n", *(UINT16*)(cfg+0x1c));
    Print(L"I/O LImit: %02XFF\n", *(UINT16*)(cfg+0x1c));
}

void DumpPci(void)
{
    EFI_STATUS Status = EFI_NOT_FOUND;
    UINTN HandleCount = 0;
    EFI_HANDLE *HandleBuffer = NULL;
    int i;

    Status = gBS->LocateHandleBuffer(ByProtocol, &gEfiPciIoProtocolGuid, NULL, &HandleCount, &HandleBuffer);
    if (EFI_ERROR(Status)) {
        Print(L" Status: %r\n", Status);
        FreeHandleBuffer(&HandleBuffer);
        return;
    }
    Print (L"PCI IO Handle count: %d\n", HandleCount);
    for (i=0; i<HandleCount; i++) {
        EFI_PCI_IO_PROTOCOL *PciIo;
        UINTN Seg, Bus, Dev, Func;
        UINT32 VidDid;
        UINT8 Cfg[256];
        UINT16 *ClassName=L"";

        Status = gBS->HandleProtocol(HandleBuffer[i], &gEfiPciIoProtocolGuid, (void**)&PciIo);
	    if (EFI_ERROR (Status)) {
            Print(L"Handle: %X, Status: %r\n", HandleBuffer[i], Status);
	        continue;
	    }
        PciIo->GetLocation (PciIo, &Seg, &Bus, &Dev, &Func);
        PciIo->Pci.Read (PciIo, EfiPciIoWidthUint32, 0, 1, &VidDid);
        Print(L"%X:%02X.%02X.%X - ", Seg, Bus, Dev, Func);
        If (VidDid == 0xFFFFFFFF) {
            Print(L"FFFF:FFFF\n");
            continue
        }
        PciRead256(PciIo, Cfg);

        //Dump256(Cfg);
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

}

INTN
EFIAPI
ShellAppMain (
    IN UINTN Argc,
    IN CHAR16 **Argv
)
{
    DumpPci();
    return 0;
}
