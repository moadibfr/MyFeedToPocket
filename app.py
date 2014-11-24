#!/usr/bin/env python

import yaml
import feedparser

stream = open('feeds.yaml', 'r')
feeds = yaml.load(stream)

for feed in feeds['feeds']:
    print feed;
    content = feedparser.parse(feed['url'])
    for entry in content['entries']:
    	print entry['title'] 
    	print entry['link']
    	date = None;
    	try:
    		date = entry.updated_parsed
    	except AttributeError:
    		try:
    			date = entry.published_parsed
    		except AttributeError:
    			try:
    				date = entry.created_parsed
    			except AttributeError:
    				date = None
    	print date
