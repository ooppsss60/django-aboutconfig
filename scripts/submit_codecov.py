#!/bin/env/python

import os
import sys
from subprocess import call


if __name__ == '__main__':
    if 'CI' in os.environ:
        sys.exit(call('codecov'))
