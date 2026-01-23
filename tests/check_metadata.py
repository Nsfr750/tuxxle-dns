#!/usr/bin/env python3
"""
Check Windows executable metadata
"""

import subprocess
import sys
from pathlib import Path

def check_exe_metadata():
    """Check executable metadata using PowerShell"""
    exe_path = Path("dist/Tuxxle-DNS-1.1.0/Tuxxle-DNS-1.1.0.exe")
    
    if not exe_path.exists():
        print("❌ Executable not found!")
        return False
    
    print(f"🔍 Checking metadata for: {exe_path}")
    print("=" * 60)
    
    # PowerShell script to get file version info
    ps_script = f'''
    $filePath = "{exe_path.absolute()}"
    
    if (Test-Path $filePath) {{
        # Get basic file info
        $fileInfo = Get-Item $filePath
        Write-Host "📁 File Information:"
        Write-Host "   Name: $($fileInfo.Name)"
        Write-Host "   Size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB"
        Write-Host "   Created: $($fileInfo.CreationTime)"
        Write-Host "   Modified: $($fileInfo.LastWriteTime)"
        Write-Host ""
        
        # Get version info
        try {{
            $versionInfo = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($filePath)
            Write-Host "📋 Version Information:"
            Write-Host "   File Version: $($versionInfo.FileVersion)"
            Write-Host "   Product Version: $($versionInfo.ProductVersion)"
            Write-Host "   File Description: $($versionInfo.FileDescription)"
            Write-Host "   Company Name: $($versionInfo.CompanyName)"
            Write-Host "   Product Name: $($versionInfo.ProductName)"
            Write-Host "   Internal Name: $($versionInfo.InternalName)"
            Write-Host "   Original Filename: $($versionInfo.OriginalFilename)"
            Write-Host "   Legal Copyright: $($versionInfo.LegalCopyright)"
            Write-Host "   Comments: $($versionInfo.Comments)"
            Write-Host "   Legal Trademarks: $($versionInfo.LegalTrademarks)"
            Write-Host "   Private Build: $($versionInfo.PrivateBuild)"
            Write-Host "   Special Build: $($versionInfo.SpecialBuild)"
            Write-Host ""
            
            # Get digital signature info
            try {{
                $signature = Get-AuthenticodeSignature $filePath
                Write-Host "🔐 Digital Signature:"
                Write-Host "   Status: $($signature.Status)"
                Write-Host "   Signer Certificate: $($signature.SignerCertificate.Subject)"
                if ($signature.TimeStamp) {{
                    Write-Host "   Time Stamp: $($signature.TimeStamp)"
                }}
            }} catch {{
                Write-Host "🔐 Digital Signature: Not signed"
            }}
        }} catch {{
            Write-Host "❌ Could not read version information"
        }}
    }} else {{
        Write-Host "❌ File not found: $filePath"
    }}
    '''
    
    try:
        # Run PowerShell script
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ PowerShell error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running PowerShell: {e}")
        return False

def check_file_properties():
    """Alternative method using file properties"""
    exe_path = Path("dist/Tuxxle-DNS-1.1.0/Tuxxle-DNS-1.1.0.exe")
    
    print(f"\n📊 Basic File Properties:")
    print(f"   Path: {exe_path.absolute()}")
    print(f"   Size: {exe_path.stat().st_size / (1024*1024):.2f} MB")
    print(f"   Modified: {exe_path.stat().st_mtime}")
    
    return True

if __name__ == "__main__":
    print("🔍 Checking Windows Executable Metadata")
    print("=" * 60)
    
    success = check_exe_metadata()
    check_file_properties()
    
    if success:
        print("\n✅ Metadata check completed!")
    else:
        print("\n❌ Metadata check failed!")
        sys.exit(1)
