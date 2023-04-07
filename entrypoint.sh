#!/bin/bash --login
# The --login ensures the bash configuration is loaded,
# enabling Conda.

# Enable strict mode.
set -euo pipefail
# ... Run whatever commands ...

# Temporarily disable strict mode and activate conda:
set +euo pipefail
conda activate myenv

# Re-enable strict mode:
set -euo pipefail

# exec the final command:
python manage.py wait_for_db
python manage.py migrate
python manage.py runserver 0.0.0.0:8000