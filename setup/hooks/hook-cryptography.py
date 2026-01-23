"""
PyInstaller hook for cryptography library v1.2.0
Fixes compatibility issues with PyInstaller 5.13.2+
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, is_module_satisfies

# Collect all cryptography submodules
hiddenimports = collect_submodules('cryptography')

# Add specific cryptography modules that might be missed
hiddenimports.extend([
    'cryptography.hazmat',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.backends',
    'cryptography.hazmat.primitives.ciphers',
    'cryptography.hazmat.primitives.hashes',
    'cryptography.hazmat.primitives.kdf',
    'cryptography.hazmat.primitives.serialization',
    'cryptography.hazmat.primitives.asymmetric',
    'cryptography.hazmat.primitives.asymmetric.rsa',
    'cryptography.hazmat.primitives.asymmetric.ec',
    'cryptography.hazmat.primitives.asymmetric.ed25519',
    'cryptography.hazmat.primitives.asymmetric.dsa',
    'cryptography.hazmat.primitives.asymmetric.padding',
    'cryptography.hazmat.primitives.kdf.hkdf',
    'cryptography.hazmat.primitives.kdf.pbkdf2hmac',
    'cryptography.hazmat.primitives.kdf.scrypt',
    'cryptography.hazmat.primitives.ciphers.modes',
    'cryptography.hazmat.primitives.ciphers.algorithms',
    'cryptography.hazmat.primitives.ciphers.base',
    'cryptography.hazmat.bindings',
    'cryptography.hazmat.bindings.openssl',
    'cryptography.hazmat.bindings._openssl',
])

# Collect data files
datas = collect_data_files('cryptography')

# Exclude problematic modules that might cause import issues
excludedimports = [
    'cryptography.utils',
    'cryptography.fernet',
    'cryptography.fernet.InvalidToken',
]

# Binary files that might be needed
binaries = []

# Try to collect OpenSSL libraries if available
try:
    from PyInstaller.utils.hooks import get_module_file_attribute
    import cryptography
    crypto_path = get_module_file_attribute('cryptography')
    if crypto_path:
        # This might help with OpenSSL library detection
        pass
except:
    pass
