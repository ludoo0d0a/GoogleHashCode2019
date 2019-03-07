#!/usr/bin/python3
import logging
import time
from core import *

fnames = FILE_HV_SHORT

def read_file(fname):
	slides = read_lines(fname)
	sort_slides(slides)
	index_dual_vphotos(slides)
	print_slides(slides)
	od_edges = compute_edges(slides)
	print_slides(slides)
	print_edges(od_edges)
	reduce_edges(od_edges, slides)
	print_edges(od_edges)
	print_slides(slides)
	return compute_score(od_edges, fname)

def sort_slides(slides):
	sorted(slides, key=lambda t: t['ntags'], reverse=True)

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


def compute_edges(slides):
	logging.info(" --- compute edges")
	n = len(slides)
	ie=0
	for i in range(n):
		if (i % 100) ==0:
			logging.info("...%s / %s = %s %%", i, n, round(100*i/n))
			print_eta(i, n)
		start = i+1 #max(0, i-step)
		end = min(i+STEP, n)
		#for j in range(i+1, n):
		for j in range(start, end):
			add_edge(ie, i, j, slides)
			ie+=1
			
	logging.info(" --- sort edges")
	s_edges = sorted(edges.items(), key=lambda t: t[1]['w'], reverse=True)
	# s_edges = sorted(edges, key=operator.itemgetter('w'))
	return collections.OrderedDict(s_edges)


def add_edge(ie, i, j, slides):
	w = get_weight(i, j, slides)
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


read_all_files(fnames, read_file)
