# -*- coding: utf-8 -*-


import os.path
import warnings


HOME_DIR = os.path.expanduser("~")
DEFAULT_RC = os.path.join(HOME_DIR, ".conciergerc")
DEFAULT_SSHCONFIG = os.path.join(HOME_DIR, ".ssh", "config")


warnings.simplefilter("always", DeprecationWarning)
