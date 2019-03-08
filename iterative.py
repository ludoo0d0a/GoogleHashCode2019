#!/usr/bin/python3
import logging
import time
import core
from collections import *
from core import *

#fnames = core.FILE_H_ONLY_100
#fnames = core.FILE_A # =2
#fnames = core.FILE_B_H_ONLY_100
fnames = core.FILE_B_H_ONLY  # 221127 ETA: 1.14 minutes  205625

#fnames = core.FILE_C_HV_SHORT  # limit=5>16273  / l=50> 199055 in 28m / 
#core.V_LIMIT=80

#fnames = core.FILE_D_HV_LONG
#fnames = core.FILE_E_V_LONG
#fnames = core.ALL_FILES
#fnames = core.ALL_FILES_2

tag_slides = defaultdict(lambda: set())
SCORE = 0
first_slide = -1

def sort_slides(slides):
	logging.info(" sort slides ")
	sorted(slides, key=lambda t: (t['ntags'], t['h'], t['i']), reverse=True)
	core.log_time()

def read_file(fname):
	slides = core.read_lines(fname)
	# count_tags(slides)
	# count_unique_tags(slides)
	# count_distribution_tags(slides)
	sort_slides(slides)
	core.index_dual_vphotos(slides)
	index_slides_by_tag(slides)
	iterate_slides(slides)
	logger.info("core.visited=%s", len(core.visited))
	logger.info("core.result=%s", len(core.result))
	return (SCORE, slides)
	#return compute_score(slides, fname)

def index_slides_by_tag(slides):
	for i, slide in enumerate(slides):
		for tag in slide['tags']:
			tag_slides[tag].add(i)
	logger.info("tag_slides = %s", len(tag_slides))

def iterate_slides(slides):
	i=0
	loop=0
	count_slides = len(slides)
	keys_slides = set(range(0, count_slides))
	logging.info(" iterate %s slides ", count_slides)
	while len(core.visited) < count_slides:
		i = iterate_slide(i, slides, loop, count_slides, keys_slides)
		loop+=1

def find_after(i,slides):
	wmax = -1
	jmax = -1
	tags = slides[i]['tags']
	
	#Factorize
	js = set()
	for tag in tags:
		js.update(tag_slides[tag])
	js = js - core.visited
	logging.debug(" find_after %s tags => %s slides , %s core.visited, ", len(tags), len(js), len(core.visited))

	for j in js:
		w = get_weight(i, j, slides)
		if (w > wmax):
			wmax = w
			jmax = j
	return (wmax, jmax)

def clean_tag_slides(i, slides):
	slide = slides[i]
	for tag in slide['tags']:
		tag_slides[tag].remove(i)

def visit_all_v_paired_slides(i, slides):
	if not slides[i]['h']:
		visit_v_paired_slides(slides[i]['photo1'])
		visit_v_paired_slides(slides[i]['photo2'])

def visit_v_paired_slides(index_photo):
	core.visited.update(core.index_slides_by_photo_v[index_photo])
		
def iterate_slide(i, slides, loop, count_slides, keys_slides):
	global SCORE

	core.visited.add(i)  # set for indexing
	core.result.append(i)  # ordered list for output file
	clean_tag_slides(i, slides)
	visit_all_v_paired_slides(i, slides)

	wmax, jmax=find_after(i,slides)

	if jmax < 0:
		logger.debug("Find a 0 transition")
		for i in keys_slides - core.visited:
			wmax, jmax  = find_after(i, slides)
			if (jmax > 0):
				break

	if jmax < 0:
		logger.error("Impossible or END")

	if wmax > 0:
		SCORE += wmax
		if loop % STEP ==0:
			logging.info(" pair %s>%s // +%s = %s", i, jmax, wmax, SCORE)
			print_eta(loop, count_slides)
	elif loop % STEP == 0:
			logging.info("    Add ZERO pair %s>%s // +%s = %s", i, jmax, wmax, SCORE)
	return jmax

core.read_all_files(fnames, read_file)
