#!/usr/bin/env python3
import re

# Create a backup of the tee.py file
import os
import shutil

tee_file_path = "app/services/tee.py"
backup_path = f"{tee_file_path}.verify_backup"
shutil.copy2(tee_file_path, backup_path)
print(f"Created backup at {backup_path}")

with open(tee_file_path, 'r') as f:
    content = f.read()

# Look for the problematic code using asyncio.to_thread
to_thread_pattern = r"await asyncio\.to_thread\(\s*self\.flare_vtpm_contract\.functions\.verifyAndAttest\(\s*header,\s*payload,\s*signature\s*\)\.call\s*\)"

# Replace with a compatible version for Python 3.8
replacement = """loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, 
                    lambda: self.flare_vtpm_contract.functions.verifyAndAttest(
                        header,
                        payload,
                        signature
                    ).call()
                )"""

# Perform the replacement
updated_content = re.sub(to_thread_pattern, replacement, content)

# Save the updated content back to the file
with open(tee_file_path, 'w') as f:
    f.write(updated_content)

print(f"Updated verify_attestation method in {tee_file_path}")
