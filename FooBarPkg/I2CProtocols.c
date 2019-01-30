/** @file

A protocol instance counter.


** Ref: dh -p <protocol_name>

**/
#include <Uefi.h>
#include <Library/UefiLib.h>
#include <Library/ShellCEntryLib.h>
#include <Library/UefiBootServicesTableLib.h>
#include <Library/UefiRuntimeServicesTableLib.h>
#include <Library/BaseMemoryLib.h>
#include <Library/MemoryAllocationLib.h>
#include <Library/BaseLib.h>


#include <Include/Protocol/DriverBinding.h>
#include <Include/Protocol/ComponentName2.h>
#include <Include/Protocol/PciRootBridgeIo.h>
#include <Include/Protocol/PciIo.h>
#include <Include/Protocol/Usb2HostController.h>
#include <Include/Protocol/UsbHostController.h>
#include <Include/Protocol/UsbIo.h>
#include <Include/Protocol/UsbFunctionIo.h>


// Protocols defined in PI 1.3.
#include <Include/Protocol/I2cMaster.h>
#include <Include/Protocol/I2cIo.h>
#include <Include/Protocol/I2cEnumerate.h>
#include <Include/Protocol/I2cHost.h>
#include <Include/Protocol/I2cBusConfigurationManagement.h>


VOID FreeHandleBuffer(EFI_HANDLE **h)
{
    if (*h) {
        FreePool(*h);
        *h = NULL;
    }
}


VOID DumpHandle(VOID)
{
    EFI_STATUS Status = EFI_NOT_FOUND;
    UINTN HandleCount = 0;
    EFI_HANDLE *HandleBuffer = NULL;
    int i;
    struct {
        EFI_GUID *guid;
        CHAR16 *cname;
    } guid_cname[] = {
        // These basic protocols are for sanity checks.
        {&gEfiDriverBindingProtocolGuid, L"gEfiDriverBindingProtocolGuid"},
        {&gEfiComponentName2ProtocolGuid, L"gEfiComponentName2ProtocolGuid"},
        {&gEfiPciRootBridgeIoProtocolGuid, L"gEfiPciRootBridgeIoProtocolGuid"},
        {&gEfiPciIoProtocolGuid, L"gEfiPciIoProtocolGuid"},
        {&gEfiUsb2HcProtocolGuid, L"gEfiUsb2HcProtocolGuid"},
        {&gEfiUsbHcProtocolGuid, L"gEfiUsbHcProtocolGuid"},
        {&gEfiUsbIoProtocolGuid, L"gEfiUsbIoProtocolGuid"},
        {&gEfiUsbFunctionIoProtocolGuid, L"gEfiUsbFunctionIoProtocolGuid"},
        {NULL, L"\n"},

        //I2C protocols in PI 1.3
        {&gEfiI2cMasterProtocolGuid, L"gEfiI2cMasterProtocolGuid"},
        {&gEfiI2cIoProtocolGuid, L"gEfiI2cIoProtocolGuid"},
        {&gEfiI2cEnumerateProtocolGuid, L"gEfiI2cEnumerateProtocolGuid"},
        {&gEfiI2cHostProtocolGuid, L"gEfiI2cHostProtocolGuid"},
        {&gEfiI2cBusConfigurationManagementProtocolGuid, L"gEfiI2cBusConfigurationManagementProtocolGuid"},
        {NULL, NULL},
    };

    for (i=0; guid_cname[i].cname; i++) {
        Print(L"%s\n", guid_cname[i].cname);
        if (guid_cname[i].cname[0] == '\n')
            continue;
        Status = gBS->LocateHandleBuffer(ByProtocol, guid_cname[i].guid, NULL, &HandleCount, &HandleBuffer);
        if (EFI_ERROR(Status))
            Print(L"  Status: %r\n", Status);
        else
            Print(L"  Instances: %d\n", HandleCount);
        FreeHandleBuffer(&HandleBuffer);
    }
}

INTN
EFIAPI
ShellAppMain (
    IN UINTN Argc,
    IN CHAR16 **Argv
)
{
    DumpHandle();
    return 0;
}
