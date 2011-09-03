import os, sys
from paste.deploy import loadapp
current_dir = os.path.dirname(__file__)

path = "/home/dotcloud/code/liondine/secret.py"
if not os.path.exists(path):
    os.symlink("/home/dotcloud/secret.py", path)
application = loadapp('config:production.ini', relative_to = current_dir)
