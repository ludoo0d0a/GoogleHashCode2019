#!/usr/bin/python3
 
import networkx as nx
import networkx.algorithms.matching as matching
import collections
import operator
import logging
import time

start_time = time.time()
logger = logging.getLogger(__name__)
#set your log level
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logging.debug('Start solver')

DIR = "input/"
# fnames = ['a_example.txt', 'b_lovely_landscapes.txt', 'c_memorable_moments.txt', 'd_pet_pictures.txt', 'e_shiny_selfies.txt']
# fnames = ['a_example.txt']
fnames = ['b_lovely_landscapes.txt']
slides = []
G = None
STEP = 10
h=[] # photo h
v=[] # photo v
slide = []  # type, photo1, photo2?
edges= dict()
visited = dict() 
start = dict() 

def init():
	#TODO global...
	slides = []
	G = None
	h = []  # photo h
	v = []  # photo v
	slide = []  # type, photo1, photo2?
	edges = dict()
	visited = dict()
	start = dict()

def read_all_files(fnames):
	total_score=0;
	for fname in fnames:
		total_score +=read_file(fname)
	logging.info(' ===== Total Score=%s',  total_score)

def sum_tags(p1, p2):
	tags = set()
	tags.update(p1["tags"])
	tags.update(p2["tags"])
	return tags

# Create all slides with 2 V photos 
def index_dual_vphotos():
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

# File should ends with EOL
def read_lines(fname):
	global DIR;
	with open(DIR+fname) as f:
		count = int(next(f)[:-1])  # skip line
		global G
		i=0
		G = nx.cycle_graph(count)
		for line in f:
			process(i, line[:-1])
			i=+1

def process(i, line):
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
			"siblings": []
        }
		slides.append(slide)  # direct add
	else:
		# defer add 
		photo["iv"] = len(v)
		v.append(photo)


def sort_slides():
	sorted(slides, key=lambda t: t['ntags'], reverse=True)

def read_file(fname):
	init()
	read_lines(fname)
	sort_slides()
	index_dual_vphotos()
	print_slides(slides)
	od_edges = compute_edges()
	print_slides(slides)
	print_edges(od_edges)
	reduce_edges(od_edges, slides)
	print_edges(od_edges)
	print_slides(slides)
	return compute_score(od_edges, fname)

def reduce_edges(od_edges, slides):
	global visited
	logging.info(" --- reduce edges")
	index_edge=0
	slides_count = len(slides)
	edges_count = len(od_edges)
	logging.info(" === %s slides for %s edges ===", slides_count, edges_count)
	for index_edge, edge in od_edges.items():
		logging.debug("  ")
		logging.debug("  ___ index_edge=", index_edge)
		print_edge(edge, ">> reduce")
		remove_sibling_edges(index_edge, edge["i"], slides, od_edges)
		remove_sibling_edges(index_edge, edge["j"], slides, od_edges)
		index_edge +=1
		logging.debug("Visited=", len(visited), "/", len(slides), "slides")
		if (len(visited) >= slides_count):
			logging.info("Starting points are : %s", start.keys())
			break

# Remove all relations if slides has already 2 visited edges
def remove_sibling_edges(index_edge, index_slide, slides, od_edges):
	global visited, start
	slide = slides[index_slide]
	if index_slide in visited:
		# restore previous edge touching this same slide
		prev_index_edge = visited[index_slide]
		del start[index_slide]
		logging.debug(" ++ Slide", index_slide, "visited TWICE from edges", index_edge, prev_index_edge)
		# 2 relations means delete all others relations
		remove_extra_siblings(index_edge, prev_index_edge, od_edges, slide)
	else:
		# first time store edge touching the node/slide
		visited[index_slide] = index_edge
		start[index_slide] = True
		logging.debug(" + Slide", index_slide, "visited ONCE from edge", index_edge)

def remove_extra_siblings(index_edge, prev_index_edge, od_edges, slide):
	siblings=slide["siblings"]
	siblings.remove(index_edge)
	if prev_index_edge >= 0:
		siblings.remove(prev_index_edge)
	logging.debug("  * remove extra siblings edges", siblings)
	for ie in siblings:
		print_edge(od_edges[ie], "   > delete")
		del od_edges[ie]

def compute_edges():
	logging.info(" --- compute edges")
	n = len(slides)
	ie=0
	for i in range(n):
		if (i % 100) ==0:
			logging.info("...%s / %s = %s %%", i, n, round(100*i/n))
			t = (time.time() - start_time)
			#logging.info("--- %s seconds --- ", t)
			eta = t * n / (i+1)
			logging.info("--- ETA: %s minutes --- ", eta/60)
		start = i+1 #max(0, i-step)
		end = min(i+STEP, n)
		#for j in range(i+1, n):
		for j in range(start, end):
			add_edge(ie, i, j, get_weight(i, j))
			ie+=1
			
	logging.info(" --- sort edges")
	s_edges = sorted(edges.items(), key=lambda t: t[1]['w'], reverse=True)
	# s_edges = sorted(edges, key=operator.itemgetter('w'))
	return collections.OrderedDict(s_edges)

def add_edge(ie,i,j,w):	
	if(w > 0):
		edge = {
			"ie": ie,
			"i": i,
			"j": j,
			"w": w
		}
		# index relations into edge
		slides[i]["siblings"].append(ie)
		slides[j]["siblings"].append(ie)
		#edges.append(edge)
		edges[ie] = edge
		print_edge(edge)

def get_weight(i, j):
	s1 = slides[i]
	s2 = slides[j]
	c = s1["tags"].intersection(s2["tags"])
	l = len(c)
	return min(l, len(s1["tags"])-l, len(s2["tags"])-l)

def compute_score(edges, fname):
	logging.info(" ")
	logging.info(" --- compute score on %s edges", len(edges))
	score=0
	for i, edge in edges.items():
		logging.debug("edge: %s",edge)
		slide1 = slides[edge["i"]]
		slide2 = slides[edge["j"]]
		print_slide(slide1)
		print_slide(slide2)
		score +=edge['w']

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
			logging.debug("Slide %s with photo H:%s %s %s", slide['i'], slide['photo'], slide['tags'], slide["siblings"])
		else:
			logging.debug("Slide %s with photo V:%s %s %s", slide['i'],	slide['photo1'], "+", slide['photo2'], slide['tags'], slide["siblings"])

def print_edge(edge, prefix=''):
	logging.debug("%s edge[%s] slide %s->%s, weight=%s", prefix, edge["ie"], edge["i"], edge["j"], edge["w"])

def print_edges(edges):
	if logger.isEnabledFor(logging.DEBUG):
		for i, edge in edges.items():
			print_edge(edge)

read_all_files(fnames)
logging.info("--- %s seconds --- ", time.time() - start_time)
