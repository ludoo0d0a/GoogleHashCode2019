#!/usr/bin/python3
 
import networkx as nx
import networkx.algorithms.matching as matching
import collections
import operator

DIR = "input/"
# fnames = ['a_example.txt', 'b_lovely_landscapes.txt', 'c_memorable_moments.txt', 'd_pet_pictures.txt', 'e_shiny_selfies.txt']
fnames = ['a_example.txt']
slides = []
G = None
h=[] # photo h
v=[] # photo v
slide = []  # type, photo1, photo2?
edges= dict()

def init():
	slides = []
	G = None
	h = []  # photo h
	v = []  # photo v
	slide = []  # type, photo1, photo2?
	edges = dict()

def read_all_files(fnames):
	total_score=0;
	for fname in fnames:
		total_score =+ read_file(fname)
	print(' ===== Total Score=',  total_score)

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

def log_slides(slides):
	print(" --- {} slides".format(len(slides)))
	for slide in slides:
		log_slide(slide)

def log_slide(slide):
	if slide['h']:
		print("Slide ", slide['i'], " with photo H:",
		      slide['photo'], slide['tags'])
	else:
		print("Slide ", slide['i'], " with photo V:",
		      slide['photo1'], "+", slide['photo2'], slide['tags'])

def read_file(fname):
	init()
	read_lines(fname)
	index_dual_vphotos()
	log_slides(slides)
	od_edges = compute_edges()
	final_edges = reduce_edges(od_edges)
	return compute_score(final_edges)

def reduce_edges(od_edges):
	print(" --- reduce edges")
	# kruskal’, ‘prim’, or ‘boruvka’
	#T = nx.maximum_spanning_tree(G, algorithm='prim')
	#final_edges = T.edges(data=True)
	e=0
	while e < len(od_edges):
		edge = od_edges[e]
		i=edge["i"]
		j=edge["j"]
		remove_edges(e, slides[i]["siblings"])
		remove_edges(e, slides[j]["siblings"])
		e =+ 1
	return final_edges

def remove_edges(e, siblings):
	for ie in siblings:
		if ie != e and ie in edges:
			del edges[ie]
			# TODO Remove intoOrderdList too...

def compute_edges():
	print (" --- compute edges")
	n = len(slides)
	for i in range(n):
		for j in range(i+1, n):
			add_edge(i, j, weight=get_weight(i, j))
	print (" --- sort edges")
	s_edges = sorted(edges.items(), key=lambda t: t[1]['w'])
	# s_edges = sorted(edges, key=operator.itemgetter('w'))
	return collections.OrderedDict(s_edges)

def add_edge(i,j,weight):	
	#global G
	#G.add_edge(i, j, weight=get_weight(i, j))
	ie=len(edges)
	edge = {
		"ie": ie,
		"i": i,
		"j": j,
		"w": get_weight(i, j)
	}
	# index relations into edge
	slides[i]["siblings"].append(ie)
	slides[j]["siblings"].append(ie)
	#edges.append(edge)
	edges[ie] = edge

def get_weight(i, j):
	s1 = slides[i]
	s2 = slides[j]
	c = s1["tags"].intersection(s2["tags"])
	l = len(c)
	return min(l, len(s1["tags"])-l, len(s2["tags"])-l)

def compute_score(edges):
	print(" --- compute score")
	# score=0
	for edge in edges:
		print(edge)
		slide1 = slides[edge[0]]
		slide2 = slides[edge[1]]
		log_slide(slide1)
		log_slide(slide2)
		# score += edge[2]['weight']

	score = sum((edge[2]['weight']) for edge in edges)
	print(' ===== Score=', fname,  score)
	print('end')
	return score


read_all_files(fnames)
