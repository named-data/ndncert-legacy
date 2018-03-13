#!/usr/bin/env python3

import os
import sys

BASEDIR = os.path.abspath(os.path.dirname(__file__))

if BASEDIR not in sys.path:
   sys.path.append(BASEDIR)

from www import server

application = server.app

application.run(debug = True, host='0.0.0.0')
