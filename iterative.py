#!/usr/bin/python3
import logging
import time
from core import *

tag_slides = defaultdict(lambda: set())
SCORE=0
#fnames = FILE_H_ONLY_100
#fnames = FILE_A # =2
#fnames = FILE_B_H_ONLY_100
#fnames = FILE_B_H_ONLY  # 205248 ETA: 1.14 minutes  205625
fnames = FILE_C_HV_SHORT  # limit=5>16273  / l=50> 199055 in 28m / 
#fnames = FILE_D_HV_LONG
#fnames = FILE_E_V_LONG
#fnames = ALL_FILES
#fnames = ALL_FILES_2

first_slide = -1

def sort_slides(slides):
	logging.info(" sort slides ")
	sorted(slides, key=lambda t: (t['ntags'], t['h'], t['i']), reverse=True)
	log_time()

def read_file(fname):
	slides = read_lines(fname)
	# count_tags(slides)
	# count_unique_tags(slides)
	# count_distribution_tags(slides)
	sort_slides(slides)
	index_dual_vphotos(slides)
	index_slides_by_tag(slides)
	iterate_slides(slides)
	return SCORE
	#return compute_score(slides, fname)

def index_slides_by_tag(slides):
	global tag_slides
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
	while count_slides > len(visited):
		i = iterate_slide(i, slides, loop, count_slides, keys_slides)
		loop+=1

def find_after(i,visited,slides):
	global tag_slides
	wmax = -1
	jmax = -1
	for tag in slides[i]['tags']:
		js = tag_slides[tag]-visited
		for j in js:
			w = get_weight(i, j, slides)
			if (w > wmax):
				wmax = w
				jmax = j
	return (wmax, jmax)

def visit_v_paired_slides(index_photo):
	# for j in index_slides_by_photo_v[index_photo]:
	# 	visited.add(j)
	visited.update(index_slides_by_photo_v[index_photo])
		
def iterate_slide(i, slides, loop, count_slides, keys_slides):
	global SCORE, first_slide
	r=find_after(i,visited,slides)
	wmax = r[0]
	jmax = r[1]

	if jmax < 0:
		logger.debug("Find a 0 transition")
		for i in keys_slides - visited:
			r = find_after(i, visited, slides)
			if (r[1] > 0):
				jmax = r[1]
				wmax = r[0]
				break

	elif first_slide < 0:
		first_slide = jmax

	if jmax < 0:
		logger.error("Impossible")

	visited.add(i) # set for indexing
	result.append(i) #ordered list for output file

	# slide i visited
	#visite also all paired for V slides
	if not slides[i]['h']:
		visit_v_paired_slides(slides[i]['photo1'])
		visit_v_paired_slides(slides[i]['photo2'])

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
