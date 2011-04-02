#!/usr/bin/env python
# coding=utf8

from cStringIO import StringIO
import re
import yaml

import networkx

from dameraulevenshtein import dameraulevenshtein
from fuzzy_substring_match import fuzzy_substring

class LeagueOfLegendsException(Exception): pass

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


class Inventory(object):
	def __init__(self, db, items = []):
		self.db = db
		self.items = items

	def purchase(self, item):
		cost = 0
		for need in self.db.successors(item):
			# we need these items before we can buy our desired item
			if not need in self.items:
				cost += self.purchase(need)

			self.items.remove(need)

		# got all the requirements, now purchase real item
		self.buy(item)
		self.items.append(item)

		return cost + self.db.node[item]['cost']

	def buy(self, name):
		print "Buying %s for %r" % (name, self.db.node[name]['cost'])

	def __repr__(self):
		return "Inventory(%r)" % self.items


class TrackingInventory(Inventory):
	def __init__(self, *args, **kwargs):
		super(TrackingInventory, self).__init__(*args, **kwargs)
		self.recently_bought = []

	def buy(self, name):
		self.recently_bought.append(name)


class Build(object):
	def __init__(self, db, fuzzy_item_list):
		self.db = db

		self.items = []
		for nick in fuzzy_item_list:
			candidates = self.db.find_item_by_fuzzy_nick(nick)
			results = []
			score = candidates[0][0]
			while candidates and candidates[0][0] == score:
				s, n = candidates.pop(0)
				results.append(n)

			if len(results) > 1:
				raise LeagueOfLegendsException('Cannot decide what you mean by %r. Candidates: %r' % (nick, results))

			self.items.append(results[0])

	@classmethod
	def from_build_file(cls, db, filename):
		return cls.from_yaml(db, file(filename, 'r').read())

	@classmethod
	def from_yaml(cls, db, s):
		# perform nickname guessing
		fuzzy_item_list = yaml.safe_load(s)
		return cls(db, fuzzy_item_list)

	def to_purchase_yaml(self):
		inv = TrackingInventory(self.db)

		sbuf = StringIO()
		for item, total, prereqs in self.purchase_iter():
			cost = str(total)
			if inv.recently_bought:
				cost += ' (=%s)' % "+".join((str(self.db.node[n]['cost']) for n in prereqs))
			inv.recently_bought = []
			sbuf.write("- %s # %s\n" % (item, cost))

		return sbuf.getvalue()

	def purchase_iter(self):
		inv = TrackingInventory(self.db)

		for item in self.items:
			total = inv.purchase(item) # total price
			yield item, total, inv.recently_bought
