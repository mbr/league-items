#!/usr/bin/env python
# coding=utf8

import re
import urllib2

from BeautifulSoup import BeautifulSoup

_num_re = re.compile(r'(\d+)')
def _num_from_link(a):
	return int(_num_re.search(a['href']).group(1))


def scrape_items():
	page = urllib2.urlopen('http://www.leagueoflegends.com/items').read()
	soup = BeautifulSoup(page)
	for tbl in soup.findAll('table', {'class': 'champion_item'}):
		num = _num_from_link(tbl.find('a', {'class': 'lol_item'}))
		name = unicode(tbl.find('span', {'class': 'highlight'}).string)
		cost = int(tbl.find('td', {'class': 'cost highlight'}).find('span', {'class': 'big'}).contents[0])

		built_from_nums = []
		for t in tbl.findAll('div'):
			if t.string == 'Built From':
				ul = t.next.next.next

				for built_from_link in ul.findAll('a'):
					built_from_nums.append(_num_from_link(built_from_link))

		if not num: raise Exception('Failed to scrape number out of %r' % tbl)
		if not name: raise Exception('Failed to scrape name out of %r' % tbl)
		if None == cost: raise Exception('Failed to scrape cost out of %r' % tbl)

		yield num, name, cost, built_from_nums


def parse_items():
	items_by_num = {}
	for num, name, cost, built_from_nums in scrape_items():
		items_by_num[num] = (name, cost, built_from_nums)

	items = {}
	for num in items_by_num:
		name, cost, built_from_nums = items_by_num[num]
		items[name] = {
			'cost': cost,
			'built_from': [items_by_num[n][0] for n in built_from_nums],
		}

	return items
