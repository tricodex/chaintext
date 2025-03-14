#!/usr/bin/env python3
import re

with open('app/core/config.py', 'r') as f:
    content = f.read()

# Create a backup
with open('app/core/config.py.bak5', 'w') as f:
    f.write(content)
print("Created backup of config.py")

# Remove GOTPM_PATH defined outside the class
content = re.sub(r'^GOTPM_PATH:.*$', '', content, flags=re.MULTILINE)

# Add GOTPM_PATH inside the Settings class
tpm_device_pattern = r'(\s+TPM_DEVICE: str = os\.getenv\([^)]+\))'
content = re.sub(
    tpm_device_pattern,
    r'\1\n    GOTPM_PATH: str = os.getenv("GOTPM_PATH", "/home/pc/chaincontext/tools/go-tpm-tools/cmd/gotpm/gotpm")',
    content
)

with open('app/core/config.py', 'w') as f:
    f.write(content)

print("Updated config.py")