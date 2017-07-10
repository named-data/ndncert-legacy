import os
import sys

BASEDIR = os.path.abspath(os.path.dirname(__file__))

if BASEDIR not in sys.path:
   sys.path.append(BASEDIR)

from www import server

application = server.app

