import time
import os
from pathlib import Path

def get_format_time(t):
	if t == "1":
		return time.strftime("%Y%m%d%H%M%S", time.localtime())

def get_abspath(p1):
	r = Path(get_curpath()) / p1
	return str(os.path.abspath(r))

def get_relpath(p, startpath = ""):
	startpath = get_curpath() if startpath == "" else startpath
	return os.path.relpath(p, startpath = "")

def get_curpath():
	return str(Path.cwd())