#! /usr/bin/env python
'''A simple script to find out what mobile home pages don't exist yet'''

from urllib2 import urlopen, URLError
from urlparse import urlparse
from xml.dom import minidom
from bs4 import BeautifulSoup
from optparse import OptionParser

class Site:
	def __init__(self, url, opts=None):
		self.opts = opts
		self.url = url
		parsedProjectUrl = self.parseProjectUrl(self.url)
		self.lang = parsedProjectUrl[0]
		self.project = parsedProjectUrl[1]
		self.mobileUrl = self.getMobileUrl(parsedProjectUrl)
		self.hasMobileHomePage = self.hasMobileHomePage(self.mobileUrl)

	def getMobileUrl(self, urlTuple):
		'''Given a url construct the .m version of it'''
		url = "http://%s.m.%s.%s" % (urlTuple[0], urlTuple[1], urlTuple[2])
		return url

	def parseProjectUrl(self, url):
		'''Return tuple containing subdomain, domain, tld'''
		(sub, domain, tld) = urlparse(url).netloc.split('.')
		t = sub, domain, tld
		return t

	def hasMobileHomePage(self, mobileUrl):
		'''Return whether or not a given URL has a configured main page'''
		try: 
			response = urlopen(mobileUrl)
		except URLError, e:
			string = "Error %s" % e.code
			hasHomePage = None
		else:
			soup = BeautifulSoup(response)
			div = soup.find('div', id='mainpage')
			if len(str(div)) <= 25:
				string = 'Missing'
				hasHomePage = False
			else: 
				string = 'Found'
				hasHomePage = True
		if self.opts.debug:
			print "%s : %s" % (mobileUrl, string)
		return hasHomePage

def printWikiTextProjectStatus(sites, sectionWrapper):
	'''Print a wikitext table of results, ordered by project'''
	for project in sites:
		print "%s%s%s" % (sectionWrapper, project, sectionWrapper)
		print "{|  class='wikitable sortable collapsible collapsed'"
		print "! Language !! Mobile URL !! Has main page?"
		print "|-"
		for lang, siteStatus in sites[project].iteritems():
			siteUrl = siteStatus[0]
			if siteStatus[1]:
				bgcolor = 'green'
			else:
				bgcolor = 'red'
			print "| %s || [%s %s] || bgcolor='%s' | %s" % (lang, siteUrl, siteUrl, bgcolor, siteStatus[1])
			print "|-"
		print "|}"

def main():
	'''Handle command line options'''
	usage = "usage: %prog [options]"
	parser = OptionParser(usage=usage)
	parser.add_option("-d", "--debug", action="store_true", dest="debug",
						default=False, help="Enable debug output")
	parser.add_option("-w", "--section-wrapper", action="store",
						dest="sectionWrapper", default="=",
						help="The wikitext section heading level to use (eg '==' \
						for ==Section==)")
	parser.add_option("-s", "--site-matrix", action="store", dest="siteMatrix",
						default="http://en.wikipedia.org/w/api.php?action=sitematrix&format=xml",
						help="The location of the site matrix to parse")
	(options, args) = parser.parse_args()

	'''Parse the siteMatrix'''
	dom = minidom.parse(urlopen(options.siteMatrix))

	'''Grab the site elements'''
	languages = dom.getElementsByTagName("site")
	sites = {}
	
	'''Loop through sites and determine whether or not they have a mobile main page'''
	for language in languages:
		rawurl = language.getAttribute('url')
		if rawurl != '':
			site = Site(rawurl, options)
			siteStatus = site.mobileUrl, site.hasMobileHomePage
			if site.project not in sites:
				sites[site.project] = {}
			sites[site.project][site.lang] = siteStatus

	'''Pring wikitext table of projects and their statuses'''
	printWikiTextProjectStatus(sites, options.sectionWrapper)

if __name__ == "__main__":
	main()