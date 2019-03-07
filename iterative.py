#!/usr/bin/python3
import logging
import time
from core import *

SCORE=0
#fnames = FILE_H_ONLY_100
# fnames = FILE_A # =2
#fnames = FILE_H_ONLY_100
fnames = FILE_H_ONLY

def sort_slides(slides):
	logging.info(" sort slides ")
	sorted(slides, key=lambda t: (t['ntags'], t['h'], t['i']), reverse=True)

def read_file(fname):
	slides = read_lines(fname)
	count_tags(slides)
	count_unique_tags(slides)
	count_distribution_tags(slides)
	
	sort_slides(slides)
	index_dual_vphotos(slides)
	iterate_slides(slides)
	return SCORE
	#return compute_score(slides, fname)

def iterate_slides( slides):
	i=0
	loop=0
	count_slides = len(slides)
	logging.info(" iterate %s slides ", count_slides)
	while count_slides > len(visited):
		i = iterate_slide(i, slides, loop, count_slides)
		loop+=1

def find_after(i,start,visited,slides):
	wmax = -1
	jmax = -1
	for j in range(start, len(slides)):
		if j not in visited:
			w = get_weight(i, j, slides)
			if (w > wmax):
				wmax = w
				jmax = j
	return (wmax, jmax)


def iterate_slide(i, slides, loop, count_slides):
	global SCORE
	# r=find_after(i,i+1,visited,slides)
	r=find_after(i,0,visited,slides)
	wmax = r[0]
	jmax = r[1]

	if jmax < 0:
		logger.debug("Reach end, try from start")
		r = find_after(i, 0, visited, slides)
		wmax = r[0]
		jmax = r[1]

	if jmax < 0:
		logger.error("Should not happend this time")

	visited[i] = jmax
	if wmax > 0:
		SCORE += wmax
		if loop % STEP ==0:
			logging.info(" pair %s>%s // +%s = %s", i, jmax, wmax, SCORE)
			print_eta(loop, count_slides)
	else:
		if loop % STEP == 0:
			logging.info("    ___pair %s>%s // +%s = %s", i, jmax, wmax, SCORE)
	return jmax

read_all_files(fnames, read_file)
