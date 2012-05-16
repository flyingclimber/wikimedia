#! /usr/bin/env python
'''A simple script to find out what mobile home pages don't exist yet'''

from urllib2 import urlopen, URLError
from urlparse import urlparse
from xml.dom import minidom
from bs4 import BeautifulSoup

SITEMATRIX = 'http://en.wikipedia.org/w/api.php?action=sitematrix&format=xml'

class Site:
	def __init__(self, url):
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
		(sub, domain, tld) = urlparse(url).netloc.split('.')
		t = sub, domain, tld
		return t

	def hasMobileHomePage(self, mobileUrl):
		'''Print out a string saying wether a page is missing/found'''
		try: 
			response = urlopen(mobileUrl)
		except URLError, e:
			string = "Error %s" % e.code
		else:
			soup = BeautifulSoup(response)
			div = soup.find('div', id='mainpage')
			if len(str(div)) <= 25:
				string = 'Missing'
				hasHomePage = False
			else: 
				string = 'Found'
				hasHomePage = True
			print "%s : %s" % (mobileUrl, string)
			return hasHomePage

dom = minidom.parse(urlopen(SITEMATRIX))
languages = dom.getElementsByTagName("site")
sites = {}
for language in languages:
	rawurl = language.getAttribute('url')
	if rawurl != '':
		site = Site(rawurl)
		siteStatus = site.url, site.hasMobileHomePage
		if site.project not in sites:
			sites[site.project] = {}
		sites[site.project][site.lang] = siteStatus

'''print results, ordered by project, then lang'''
for project in sites:
	print "=%s=" % (project)
	for lang, siteStatus in sites[project].iteritems():
		siteUrl = siteStatus[0]
		print "==%s==\n[%s %s] : %s" % (lang, siteUrl, siteUrl, siteStatus[1])
