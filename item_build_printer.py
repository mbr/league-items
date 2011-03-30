#!/usr/bin/env python
# coding=utf8

import sys
import yaml

import networkx

from lolitems import ItemGraph
from scrape import item_file_name

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


if 2 != len(sys.argv):
	print "usage: %s itembuild.yaml" % (sys.argv[0])
	sys.exit(1)

db = ItemGraph.from_item_file(item_file_name)
build_inp = yaml.load(file(sys.argv[1]))

build = []
for nick in build_inp:
	candidates = db.find_item_by_fuzzy_nick(nick)
	results = []
	score = candidates[0][0]
	while candidates and candidates[0][0] == score:
		s, n = candidates.pop(0)
		results.append(n)

	if len(results) > 1:
		raise Exception('Cannot decide what you mean by %r. Candidates: %r' % (nick, results))

	build.append(results[0])

inv = TrackingInventory(db)

for item in build:
	cost = str(inv.purchase(item))
	if inv.recently_bought:
		cost += ' (=%s)' % "+".join((str(db.node[n]['cost']) for n in inv.recently_bought))
	inv.recently_bought = []
	print "- %s # %s" % (item, cost)
