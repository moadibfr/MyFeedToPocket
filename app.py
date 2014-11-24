#!/usr/bin/env python

import yaml
import feedparser
import config
import pocket
from pocket import Pocket
import dbm

# Open database, creating it if necessary.
db = dbm.open('cache', 'c')
if not "access_token" in db :
	request_token = Pocket.get_request_token(consumer_key=config.consumer_key, redirect_uri=config.redirect_uri)
	db["request_token"] = request_token
	print 'request_token ' + db["request_token"]

	# URL to redirect user to, to authorize your app
	auth_url = Pocket.get_auth_url(code=db["request_token"], redirect_uri=config.redirect_uri)
	print 'Go to ' + auth_url + " to authorize the script on your pocket account"
	i = raw_input("Press Enter to continue...")

	try:
		user_credentials = Pocket.get_credentials(consumer_key=config.consumer_key, code=db["request_token"])
	except pocket.RateLimitException, e:
		print "Unable to auth..." + str(e)
		db.close()
		exit(1)
	db["access_token"] = user_credentials["access_token"]

print 'access_token ' + db["access_token"]
pocket_instance = pocket.Pocket(config.consumer_key, db["access_token"])


stream = open('feeds.yaml', 'r')
feeds = yaml.load(stream)

for feed in feeds['feeds']:
    print feed;
    content = feedparser.parse(feed['url'])
    for entry in content['entries']:
    	print entry['title'] 
    	print entry['link']
    	pocket_instance.bulk_add(url=entry['link'], title=entry['title'], tags=','.join(feed["tags"]),wait=False)

db.close();
