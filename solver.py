#!/usr/bin/python3
 
import networkx as nx
import networkx.algorithms.matching as matching

fname='inputfile.txt'
slides = []
G = None

def get_weight(i, j):
	s1 = slides[i]
	s2 = slides[j]
	c = s1["tags"].intersection(s2["tags"])
	l = len(c)
	return min(l, len(s1["tags"])-l, len(s2["tags"])-l)

def process(line):
	segments = line.split(' ')
	photo = {
		"h": (segments.pop(0)=='H'),
		"i": segments.pop(0),
		"tags": set(segments)
	}
	#For now only H
	if photo['h']:
		slide = photo
		slides.append(slide)

# File should ends with EOL
def read_lines():
	with open(fname) as f:
		count = int(next(f)[:-1])  # skip line
		global G
		G = nx.cycle_graph(count)
		for line in f:
			process(line[:-1])

read_lines()

n = len(slides)
print(n, 'slides')

for slide in slides:
	print("Slide with photo ", slide['i'], "-", (slide['h'] and "H" or "V"), "=", slide['tags'])

for i in range(n):
	for j in range(i,n):
		G.add_edge(i,j,weight = -get_weight(i,j))

T = nx.minimum_spanning_tree(G)
edges = T.edges(data=True)

for edge in edges:
    print(edge)
