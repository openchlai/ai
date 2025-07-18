# core/utils/env.py

import os

def is_running_in_docker():
    # Common check for Docker containers
    return os.path.exists('/.dockerenv') or os.environ.get('RUNNING_IN_DOCKER') == '1'
