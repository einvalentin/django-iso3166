# Copyright (c) 2009-2010 Co-Capacity.
# See LICENSE for details.

# Ensure the user is running the version of python we require.
import sys
if not hasattr(sys, "version_info") or sys.version_info < (2, 4):
    raise RuntimeError("iso3166 requires Python 2.4 or later.")
del sys

VERSION = (10, 1, 1)
__version__ = '.'.join(map(str, VERSION))
