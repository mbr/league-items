#!/usr/bin/env python
# coding=utf8

import yaml

import networkx
import matplotlib.pyplot as plt


class ItemGraph(networkx.DiGraph):
	def add_item(self, name, cost, built_from = []):
		self.add_node(name, cost = cost)
		for pq in built_from:
			self.add_edge(name, pq)

	@classmethod
	def from_item_file(cls, filename):
		items = yaml.load(file(filename))
		G = cls()

		for name, attr in items.iteritems():
			G.add_item(name, **attr)

		return G


if '__main__' == __name__:
	from scrape import item_file_name
	G = ItemGraph.from_item_file(item_file_name)
	networkx.write_dot(G, 'item-graph.dot')
