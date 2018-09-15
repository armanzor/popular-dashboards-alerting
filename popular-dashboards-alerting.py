#!/usr/bin/env python3
from elasticsearch import Elasticsearch
from datetime import date
import json

es = Elasticsearch ()
today = date.today().strftime("%Y.%m.%d")
error_message = 'NO DATA'
dash_panels = {}
dashboard_alert = []

def dashPanelsAppend (result):
    for item in result['hits']['hits']:
        if dash_panels.get(item['_source']['dashboard_title']) is None:
            dash_panels[item['_source']['dashboard_title']] = []
            dash_panels[item['_source']['dashboard_title']].append(item['_source']['panel_title'])
        else:
            if dash_panels[item['_source']['dashboard_title']].__contains__(item['_source']['panel_title']):
                continue
            else:
                dash_panels[item['_source']['dashboard_title']].append(item['_source']['panel_title'])


result = es.search(index = 'grafana-check-{date}'.format(date = today), #returns dict
    scroll = '1m',
    from_ = 0,
    size = 100,
    body = {
        "sort": [
            {
                "dashboard_title": "asc"
            },
            {
                "panel_title": "asc"
            }
        ],
        "query": {
            "term": {
                "error": "{message}".format(message = error_message)
            }
        }
    })

scroll_id = result['_scroll_id']

dashPanelsAppend(result)

while len(result['hits']['hits']) != 0:
    result = es.scroll(scroll_id = scroll_id, scroll = '1m')
    dashPanelsAppend(result)

es.clear_scroll(scroll_id = scroll_id)

for line in open('dashboards.list'):
    if line[-1] == '\n':
        line = line[:-1]
    if line in dash_panels.keys():
        dashboard_alert.append(line)

print (dashboard_alert)
