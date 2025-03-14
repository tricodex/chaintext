#!/bin/bash
set -e

echo "Deploying ChainContext vTPM changes"

# 1. Make sure we're in the right directory
cd ~/chaincontext/chaincontext-backend

# 2. Create backups of original files
cp app/services/tee.py app/services/tee.py.bak
cp app/core/config.py app/core/config.py.bak
echo "Created backups of original files"

# 3. Run the Python update scripts
python update_config.py
python update_tee.py
echo "Updated files with new vTPM implementation"

# 4. Run the test script
python test_vTPM.py

echo "Changes deployed successfully!"
