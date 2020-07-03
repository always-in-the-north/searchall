import time

def get_format_time(t):
	if t == "1":
		return time.strftime("%Y%m%d%H%M%S", time.localtime())
