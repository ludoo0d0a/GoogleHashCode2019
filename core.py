import networkx as nx
import networkx.algorithms.matching as matching
import operator
import logging
import time
from random import shuffle
from collections import *

start_time = time.time()

def reset_time():
	global start_time
	start_time = time.time()

reset_time()
logger = logging.getLogger(__name__)
#set your log level
logging.basicConfig(level=logging.INFO)
logging.info('Start solver random')

DIR = "input/"

ALL_FILES = ['a_example.txt', 'b_lovely_landscapes.txt',
             'c_memorable_moments.txt', 'd_pet_pictures.txt', 'e_shiny_selfies.txt']
ALL_FILES_2 = ['a_example.txt', 'b_lovely_landscapes.txt',
            	 'd_pet_pictures.txt', 'e_shiny_selfies.txt']
FILE_A = ['a_example.txt']
FILE_B_H_ONLY = ['b_lovely_landscapes.txt'] # 80000 H only
FILE_B_H_ONLY_100 = ['b2_100.txt']
FILE_C_HV_SHORT = ['c_memorable_moments.txt']  # 1000 H+V
FILE_D_HV_LONG = ['d_pet_pictures.txt'] # 90000 H+V
FILE_E_V_LONG = ['e_shiny_selfies.txt'] # 80000 V

edges = dict()
visited_slides = set()
result = list()
start = dict()
v = []  # all vertical photos
index_slides_by_photo_v = defaultdict(lambda: set())

def init():
	global edges, visited_slides, start, v, index_slides_by_photo_v
	edges = dict()
	visited_slides = set()
	result = list()
	start = dict()
	v = []
	index_slides_by_photo_v = defaultdict(lambda: set())

def read_all_files(fnames, read_file):
	if DEBUG:
		logging.basicConfig(level=logging.DEBUG)
	r = []
	total_score=0
	for fname in fnames:
		logging.info(' ')
		logging.info(' =====Start % s', fname)
		f_start_time = time.time()
		init()
		score, slides = read_file(fname)
		logger.info("_visited_slides=%s", len(visited_slides))
		logger.info("_result=%s", len(result))
		logger.info("_slides=%s", len(slides))
		total_score += score
		save_output(fname, score, slides)
		r.append({
			"fname": fname,
			"score": score,
			"time": time.time() - f_start_time
		})
		log_time()
	logging.info(' ===== Total Score = %s for %s', total_score, r)
	log_time()

def sum_tags(p1, p2):
	tags = set()
	tags.update(p1["tags"])
	tags.update(p2["tags"])
	return tags

# File should ends with EOL
def read_lines(fname):
	global DIR
	slides=[]
	with open(DIR+fname) as f:
		count = int(next(f)[:-1])  # skip line
		i = 0
		for line in f:
			process(i, line[:-1], slides)
			i += 1
	return slides

def save_output(fname, score, slides):
	path = 'output/'+fname+'.out'
	logging.info(' ===== Save file in %s with score = %s',  path, score)
	f = open(path, 'w')
	f.write(str(len(result))+'\n')
	for i in result:
		slide = slides[i]
		if slide['h']:
			f.write("{}\n".format(slide['photo']))
		else:
			f.write("{} {}\n".format(slide['photo1'], slide['photo2']))

def process(index_line, line, slides):
	segments = line.split(' ')
	photo = {
		"h": (segments.pop(0) == 'H'),
		"line": index_line,
		"ntags": int(segments.pop(0)),
		"tags": set(segments)
	}
	if (photo["h"]):
		tags = photo["tags"]
		slide = {
			"h": True,
			"i": index_line,
			"photo": index_line,
			"ntags": len(tags),
			"tags": tags,
			"siblings": []
		}
		slides.append(slide)  # direct add
	else:
		# defer add
		v.append(photo)

# Create all slides with 2 V photos


def index_dual_vphotos(slides, V_LIMIT):
	index_slide = len(slides)
	count_v = len(v)
	logging.info(' ===== index %s vertical photos / max limit=%s', count_v, V_LIMIT)
	for iv in range(count_v):
		# Limit sibling depth
		if V_LIMIT>0:
			imax = min(count_v, iv+V_LIMIT)
		else:
			imax = count_v
		for jv in range(iv+1, imax):
			tags = sum_tags(v[iv], v[jv])
			i1 = v[iv]['line']
			i2 = v[jv]['line']
			slide = {
				"h": False,
				"i": index_slide,
				"photo1": i1,
				"photo2": i2,
				"ntags": len(tags),
				"tags": tags,
				"siblings": []
			}
			slides.append(slide)  # add an array
			# index references once slide with a V is visited_slides, remove all slides with this V
			#
			index_slides_by_photo_v[i1].add(index_slide)
			index_slides_by_photo_v[i2].add(index_slide)
			index_slide += 1

def get_weight(i, j, slides):
	s1 = slides[i]
	s2 = slides[j]
	return get_weight_slide(s1,s2)

def get_weight_slide(s1, s2):
	c = s1["tags"].intersection(s2["tags"])
	l = len(c)
	return min(l, len(s1["tags"])-l, len(s2["tags"])-l)

def compute_score(slides, fname):
	logging.info(" ")
	logging.info(" --- compute score on %s slides", len(slides))
	score = 0
	prev_slide = None
	for slide in slides:
		if prev_slide != None:
			logging.debug("slide: %s", slide)
			score += get_weight_slide(slide, prev_slide)
		prev_slide = slide

	# score = sum((edge['w']) for edge in edges)
	logging.info(' ===== Score= %s %s', fname,  score)
	logging.info('end')
	return score


def print_slides(slides):
	if logger.isEnabledFor(logging.DEBUG):
		logging.info(" --- %s slides", len(slides))
		for slide in slides:
			print_slide(slide)

def print_slide(slide):
	if logger.isEnabledFor(logging.DEBUG):
		if slide['h']:
			logging.debug("Slide %s with photo H:%s %s %s",
			              slide['i'], slide['photo'], slide['tags'], slide["siblings"])
		else:
			logging.debug("Slide %s with photo V:%s %s %s",
			              slide['i'],	slide['photo1'], "+", slide['photo2'], slide['tags'], slide["siblings"])


def print_edge(edge, prefix=''):
	logging.debug("%s edge[%s] slide %s->%s, weight=%s",
	              prefix, edge["ie"], edge["i"], edge["j"], edge["w"])


def print_edges(edges):
	if logger.isEnabledFor(logging.DEBUG):
		for i, edge in edges.items():
			print_edge(edge)

def count_tags(slides):
	count = 0
	for slide in slides:
		count += len(slide['tags'])
	logging.info("--- %s tags --- ", count)

def count_unique_tags(slides):
	all = set()
	for slide in slides:
		all.update(slide['tags'])
	logging.info("--- %s unique tags --- ", len(all))

def count_distribution_tags(slides):
	all_tags = Counter()
	for slide in slides:
		for tag in slide['tags']:
			all_tags[tag]+=1

	MAX=10
	sorted_tags = sorted(all_tags.items(), key=operator.itemgetter(1), reverse=True)

	distrib = Counter()
	for k, v in sorted_tags:
		distrib[v] += 1
	logging.info("--- Distribution %s", distrib)

	logging.info("--- %s first most used tags --- ", MAX)
	for i, value in enumerate(sorted_tags):
		logging.info("%s: %s", i, value)
		if i >= MAX:
			break

def log_time():
	duration = time.time() - start_time
	hours, remains = divmod(duration, 3600)
	minutes, seconds = divmod(remains, 60)
	logging.info("---  Done in %sh%sm%ss --- ", round(hours), round(minutes), round(seconds))

def log_eta(eta, percent):
	hours, remains = divmod(eta, 3600)
	minutes, seconds = divmod(remains, 60)
	logging.info("--- %s%%  ETA: %sh%sm%ss --- ",
	             percent, round(hours), round(minutes), round(seconds))

def print_eta(current, total):
	duration = time.time() - start_time
	eta = 0
	percent = 0
	if current > 0:
		eta = duration * total / current
		percent = round(100*current / total)
	log_eta(eta, percent)
