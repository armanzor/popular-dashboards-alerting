#!/usr/bin/env python3
from elasticsearch import Elasticsearch
from datetime import date
import json

es = Elasticsearch ()
today = date.today().strftime("%Y.%m.%d")
error_message = 'NO DATA'
dash_panels = {}

result = es.search(index = 'grafana-check-{date}'.format(date = today), #returns dict
    body={
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

# print(json.dumps(result, sort_keys=True, indent=4))
# json_result = json.loads(result)
# print(type(result))

# for item in result['hits']['hits']:
#     print (item['_source']['dashboard_title'], '\t', item['_source']['panel_title'])

for item in result['hits']['hits']:
    if dash_panels.get(item['_source']['dashboard_title']) is None:
        dash_panels[item['_source']['dashboard_title']] = []
        dash_panels[item['_source']['dashboard_title']].append(item['_source']['panel_title'])
    else:
        if dash_panels[item['_source']['dashboard_title']].__contains__(item['_source']['panel_title']):
            continue
        else:
            dash_panels[item['_source']['dashboard_title']].append(item['_source']['panel_title'])

print (dash_panels)

# $.hits.hits..["dashboard_title","panel_title"] # JSONPath
