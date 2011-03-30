#!/usr/bin/env python
# coding=utf8

import re
import yaml

import networkx

from dameraulevenshtein import dameraulevenshtein
from fuzzy_substring_match import fuzzy_substring

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

	def find_item_by_dl(self, search):
		results = [(dameraulevenshtein(search, name), name) for name in self.nodes_iter()]
		results.sort()
		return results

	def find_item_by_fuzzy_nick(self, search):
		cleanup_regex = re.compile('[^a-z0-9 ]')
		def cleanup(s):
			s = s.lower()
			return cleanup_regex.sub('', s)

		csearch = cleanup(search)

		results = []

		for name in self.nodes_iter():
			cname = cleanup(name)
			full_sim = fuzzy_substring(csearch, cname)
			word_min = min(fuzzy_substring(csearch, word) for word in cname.split(' '))
			results.append( (min(full_sim, word_min), name) )

		results.sort()
		return results
