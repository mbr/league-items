#!/usr/bin/env python
# coding=utf8

import yaml

import networkx
import matplotlib.pyplot as plt

from scrape import item_file_name

class ItemGraph(networkx.DiGraph):
	def add_item(self, name, cost, built_from = []):
		self.add_node(name, cost = cost)
		for pq in built_from:
			self.add_edge(name, pq)

if '__main__' == __name__:
	items = yaml.load(file(item_file_name))
	G = ItemGraph()

	for name, attr in items.iteritems():
		G.add_item(name, **attr)

G.add_item('HokeyTokey', 50)
G.add_item('Piano', 0, ['HokeyTokey'])
G.add_item('Fubido', 100, ['HokeyTokey'])

networkx.write_dot(G, 'item-graph.dot')
