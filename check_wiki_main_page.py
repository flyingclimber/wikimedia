'''A simple script to find out what mobile home pages don't exist yet'''

from urllib2 import urlopen, URLError
from urlparse import urlparse
from xml.dom import minidom
from bs4 import BeautifulSoup

SITEMATRIX = 'http://en.wikipedia.org/w/api.php?action=sitematrix&format=xml'

def hasMobileHomePage(url): 
    '''Print out a string saying wether a page is missing/found'''
    try: 
        response = urlopen(url)
    except URLError, e:
        string = "Error %s" % e.code
    else:
        soup = BeautifulSoup(response)
        div = soup.find('div', id='mainpage')
        if len(str(div)) <= 25:
            string = 'Missing'
        else: 
            string = 'Found'
        print "%s : %s" % (url, string)

def buildMobileRequest(url):
    '''Given a url construct the .m version of it'''
    (sub, domain, tld) = urlparse(url).netloc.split('.')
    url = "http://%s.m.%s.%s" % (sub, domain, tld)
    return url

dom = minidom.parse(urlopen(SITEMATRIX))
languages = dom.getElementsByTagName("site")

for language in languages:
    rawurl = language.getAttribute('url')
    if rawurl != '':
        hasMobileHomePage(buildMobileRequest(rawurl))
