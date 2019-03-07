import networkx as nx
import networkx.algorithms.matching as matching
import operator
import logging
import time
from random import shuffle
from collections import *

start_time = time.time()
logger = logging.getLogger(__name__)
#set your log level
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logging.debug('Start solver random')

DIR = "input/"

ALL_FILES = ['a_example.txt', 'b_lovely_landscapes.txt',
          'c_memorable_moments.txt', 'd_pet_pictures.txt', 'e_shiny_selfies.txt']
FILE_A = ['a_example.txt']
FILE_H_ONLY = ['b_lovely_landscapes.txt']
FILE_H_ONLY_100 = ['b2_100.txt']
FILE_HV_SHORT = ['c_memorable_moments.txt']
FILE_V_ONLY = ['e_shiny_selfies.txt']

STEP = 2000
#STEP = 1

edges = dict()
visited = set()
result = list()
start = dict()
v = []  # photo v

def init():
	global edges, visited, start, v
	edges = dict()
	visited = set()
	result = list()
	start = dict()
	v = []

def read_all_files(fnames, read_file):
	total_score = 0
	for fname in fnames:
		init()
		score = read_file(fname)
		total_score += score
		save_output(fname, score)
	logging.info(' ===== Total Score=%s',  total_score)
	
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
			i = +1
	return slides


def save_output(fname, score):
	path = 'output/'+fname+'.out'
	logging.info(' ===== Save file in %s with score = ',  path, score)
	f = open(path, 'w')
	f.write(''+len(visited)+'\n')
	for i in visited:
		f.write(i+'\n')

def process(i, line, slides):
	segments = line.split(' ')
	photo = {
		"h": (segments.pop(0) == 'H'),
		"ntags": int(segments.pop(0)),
		"tags": set(segments)
	}
	if (photo["h"]):
		tags = photo["tags"]
		slide = {
			"h": True,
			#"visited": 0,
			"i": len(slides),
			"photo": i,
			"ntags": len(tags),
			"tags": tags,
			"sibling§s": []
		}
		slides.append(slide)  # direct add
	else:
		# defer add
		photo["iv"] = len(v)
		v.append(photo)

# Create all slides with 2 V photos


def index_dual_vphotos(slides):
	for i in range(len(v)):
		for j in range(i+1, len(v)):
			tags = sum_tags(v[i], v[j])
			slide = {
				"h": False,
				#"visited": 0,
				"i": len(slides),
				"photo1": i,
				"photo2": j,
				"ntags": len(tags),
				"tags": tags,
				"siblings": []
			}
			slides.append(slide)  # add an array

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

def print_eta(current, total):
	t = (time.time() - start_time)
	eta = 0
	percent = 0
	if current>0:
		eta = t * total / current
		percent = round(100*current / total)
	logging.info("--- %s%%  ETA: %s minutes --- ", percent, round(eta/60,2))
