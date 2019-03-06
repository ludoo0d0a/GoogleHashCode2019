#!/usr/bin/python3
import logging
import time
from core import *

fnames = FILE_HV_SHORT
#fnames = FILE_A

def sort_slides(slides):
	logging.info(" sort slides ")
	#sorted(slides, key=lambda t: (t['ntags'], t['h'], t['i']), reverse=True)
	shuffle(slides)

def read_file(fname):
	slides = read_lines(fname)
	sort_slides(slides)
	return compute_score(slides, fname)

read_all_files(fnames, read_file)
logging.info("--- %s seconds --- ", time.time() - start_time)
