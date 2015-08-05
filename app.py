#!/usr/bin/env python

import yaml
import feedparser
import config
import pocket
from pocket import Pocket
import dbm
from time import mktime
from datetime import datetime

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

pocket_instance = pocket.Pocket(config.consumer_key, db["access_token"])


stream = open('feeds.yaml', 'r')
feeds = yaml.load(stream)

for feed in feeds['feeds']:
    if not 'url' in feed:
        print str(feed) + " Seems to have no url..."
        continue

    feed_date = 0
    if feed['url'] in db:
    	feed_date = float(db[feed['url']])
    new_feed_date = feed_date

    content = feedparser.parse(feed['url'])
    for entry in content['entries']:
        if (not 'link' in entry):
            continue
    	struct = None
    	if hasattr(entry, 'updated_parsed'):
    		struct = entry.updated_parsed
    	elif hasattr(entry, 'published_parsed'):
    		struct = entry.published_parsed
    	elif hasattr(entry, 'created_parsed'):
    		struct = entry.created_parsed
    	else:
    		#print "Entry has no date, ignore..."
    		continue
    	date = mktime(struct)
    	if feed_date < date:
                entry_tags = ""
                if 'tags' in feed:
                    entry_tags = ','.join(feed["tags"])

                if 'title' in entry and entry['title']:
                    pocket_instance.add(url=entry['link'], title=entry['title'], tags=entry_tags, wait=False)
                else :
                    pocket_instance.add(url=entry['link'], tags=entry_tags, wait=False)

    		if (new_feed_date < date):
    			new_feed_date = date
    db[feed['url']] = str(new_feed_date)

db.close();
