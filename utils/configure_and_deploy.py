# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2025 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------
"""The script combines the setup scripts for ease of use"""

# Silence checks for
# B404: Consider possible security implications associated with the subprocess module.
#       - The scripts combines the 2 startup scripts
# B603: subprocess call - check for execution of untrusted input.
#       - sys.executable will be the virtual env
#       - utils/setup.py or utils/update_metadata.py is static


import subprocess  # nosec B404
import sys


subprocess.run([sys.executable, "utils/setup.py"], check=True)  # nosec B603
subprocess.run([sys.executable, "utils/update_metadata.py"], check=True)  # nosec B603
