#!/usr/bin/env python
# dash_panels contains dashboards with list of panels, it can be used in future
from elasticsearch import Elasticsearch
from datetime import date
from smtplib import SMTP
from email.mime.text import MIMEText

es = Elasticsearch ()
today = date.today().strftime("%Y.%m.%d")
error_message = 'NO DATA'
dash_panels = {}
dashboard_alert = []
msg_body = ''
max_len_dash = 0    # for rows align

def dashPanelsAppend (result):
    for item in result['hits']['hits']:
        if dash_panels.get(item['_source']['dashboard_title']) is None:
            dash_panels[item['_source']['dashboard_title']] = []
            dash_panels[item['_source']['dashboard_title']].append({'dashboard_url' : item['_source']['dashboard_url'].split('?')[0]})
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

for dashboard_title in open('dashboards.list'):
    if dashboard_title[-1] == '\n':
        dashboard_title = dashboard_title[:-1]
    if dashboard_title in dash_panels.keys():
        dashboard_alert.append((dashboard_title, dash_panels[dashboard_title][0]['dashboard_url']))
        if len(dashboard_title) > max_len_dash:
            max_len_dash = len(dashboard_title)

for item in dashboard_alert:
    space_multiply = max_len_dash - len(item[0]) + 8
    msg_body = msg_body + item[0] + ' ' * space_multiply + item[1] + '\n'

if len(dashboard_alert) > 0:
    msg = MIMEText(msg_body)
    msg['From'] = 'test@example.com'
    msg['To'] = 'test@example.com'
    msg['Subject'] = 'Grafana dashboard no data alert'

    s = SMTP('localhost')
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()
