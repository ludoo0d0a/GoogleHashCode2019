#!/usr/bin/python3
import logging
import time
import core
from collections import *
from core import *

file = 'd'

DEBUG = False
V_LIMIT = 0
STEP = 10

#fnames = core.FILE_H_ONLY_100
if file=='a':
	fnames = core.FILE_A # =2
elif file == 'b':
	#fnames = core.FILE_B_H_ONLY_100
	fnames = core.FILE_B_H_ONLY  # 221127 in 43s  221433
elif file == 'c':
	fnames = core.FILE_C_HV_SHORT  # limit=5>16273  / l=50> 199055 in 28m / 
	V_LIMIT=30
	STEP = 10
	DEBUG = True
elif file == 'd':
	fnames = core.FILE_D_HV_LONG
	V_LIMIT = 2
	STEP = 1
	DEBUG = True
elif file == 'e':
	fnames = core.FILE_E_V_LONG
elif file == 'all2':
	fnames = core.ALL_FILES_2
else:
	fnames = core.ALL_FILES

tag_slides = defaultdict(lambda: set())
SCORE = 0
first_slide = -1
core.DEBUG = DEBUG

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
	core.index_dual_vphotos(slides, V_LIMIT)
	index_slides_by_tag(slides)
	iterate_slides(slides)
	return (SCORE, slides)
	#return compute_score(slides, fname)

def index_slides_by_tag(slides):
	for i, slide in enumerate(slides):
		for tag in slide['tags']:
			tag_slides[tag].add(i)
	logger.info("tag_slides = %s", len(tag_slides))

def iterate_slides(slides):
	core.reset_time() # re
	index_slide=0
	loop=0
	count_slides = len(slides)
	keys_slides = set(range(0, count_slides))
	logging.info(" iterate %s slides ", count_slides)
	while len(core.result) < count_slides:
		index_slide = iterate_slide(index_slide, slides, loop, count_slides, keys_slides)
		loop+=1

def find_after(i,slides):
	wmax = -1
	jmax = -1
	tags = slides[i]['tags']
	
	#Factorize
	js = set()
	for tag in tags:
		js.update(tag_slides[tag])
	js = js - core.visited_slides
	logging.debug(" find_after %s tags => %s slides , %s core.visited_slides, ", len(
		tags), len(js), len(core.visited_slides))

	for j in js:
		w = get_weight(i, j, slides)
		if (w > wmax):
			wmax = w
			jmax = j
	return (wmax, jmax)

def clean_tag_slides(i, slides):
	slide = slides[i]
	for tag in slide['tags']:
		tags = tag_slides[tag]
		if i in tags:
			tags.remove(i)

def visit_all_paired_slides(i, slides):
	slide = slides[i]
	if slide['h']:
		core.visited_slides.add(i)
		#visit_v_paired_slides(slides[i]['photo'])
	else:
		visit_v_paired_slides(slide['photo1'])
		visit_v_paired_slides(slide['photo2'])
	clean_tag_slides(i, slides)

def visit_v_paired_slides(index_photo):
	# visited TWICE...
	core.visited_slides.update(core.index_slides_by_photo_v[index_photo])

def iterate_slide(i, slides, loop, count_slides, keys_slides):
	global SCORE

	core.result.append(i)  # ordered list for output file
	visit_all_paired_slides(i, slides)
	wmax, jmax=find_after(i,slides)

	if jmax < 0:
		logger.debug("Find a 0 transition")
		for i in keys_slides - core.visited_slides:
			wmax, jmax  = find_after(i, slides)
			if (jmax >= 0):
				break

	if jmax < 0:
		logger.error("Impossible or END")

	if wmax > 0:
		SCORE += wmax
		if loop % STEP ==0:
			logging.debug(" pair %s>%s // +%s = %s", i, jmax, wmax, SCORE)
			print_eta(loop, count_slides)
	elif loop % STEP == 0:
			logging.debug("    Add ZERO pair %s>%s // +%s = %s", i, jmax, wmax, SCORE)
	return jmax

core.read_all_files(fnames, read_file)
