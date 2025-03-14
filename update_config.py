#!/usr/bin/env python3
# Simple script to add GOTPM_PATH to config.py

with open('app/core/config.py', 'r') as f:
    content = f.read()

# Add GOTPM_PATH right after TPM_DEVICE
if 'GOTPM_PATH' not in content:
    content = content.replace(
        '    TPM_DEVICE: str = os.getenv("TPM_DEVICE", "/dev/tpm0")',
        '    TPM_DEVICE: str = os.getenv("TPM_DEVICE", "/dev/tpm0")\n    GOTPM_PATH: str = os.getenv("GOTPM_PATH", "/home/pc/chaincontext/tools/go-tpm-tools/cmd/gotpm/gotpm")'
    )

    with open('app/core/config.py', 'w') as f:
        f.write(content)
    
    print("Added GOTPM_PATH to config.py")
else:
    print("GOTPM_PATH already exists in config.py")
