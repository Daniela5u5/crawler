# -*- coding: utf-8 -*-
import sys, os
from pyquery import PyQuery as pyq
import requests
import json
import time

## simple example can export suverymonkey data free
## just  change the SHARE_URL to your own
SHARE_URL = 'https://zh.surveymonkey.com/results/SM-BXFYSDZV/'

def parse_responses(p_response):
    _r_data = p_response.get('data').get('respondents')
    _all_survey = {}
    for _ids in _r_data.get('ids'):
        _survey_data = {}
        _dtl = _r_data.get('details').get(_ids)
        _survey_data['id'] = _dtl.get('id')
        _survey_data['ip_address'] = _dtl.get('ip_address')
        _survey_data['email'] = _dtl.get('email')
        _survey_data['first_name'] = _dtl.get('first_name')

        _survey_data['responses'] = {}
        for _qid in _r_data.get('responses').get(_ids).keys():
            rows = [x.get('row') for x in _r_data.get('responses').get(_ids).get(_qid)]
            text = [x.get('text') for x in _r_data.get('responses').get(_ids).get(_qid)]
            _survey_data['responses'][_qid] = [rows, text]

        _all_survey[_survey_data['id']] = _survey_data

    return _all_survey

ts = int(time.time()*1000)
survey_key = SHARE_URL.split('/')[-2]
f_url = SHARE_URL + 'browse/data.js?utc_offset=28800000&_={}'.format(ts)

header = { 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate, br',
           'Content-Type': 'application/x-www-form-urlencoded',
           'Connection': 'keep-alive',
           'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'
        }

session = requests.session()
response = session.get(url=f_url, headers=header, verify=False, timeout=60)
print response.status_code

_result = json.loads(response.content)
_result.get('data').get('respondent_data').get('data').get('respondents').get('ids')
_r_data = _result.get('data').get('respondent_data').get('data').get('respondents')
_p_survey_id = _result.get('data').get('survey_id')
_p_view_id = _result.get('data').get('shared_view').get('sharable_view')
_p_selected_view_id = _result.get('data').get('shared_view').get('default_view_id')
_p_question_id = _result.get('data').get('survey_data').get('questions').keys()
_p_total_responsed_count = _result.get('data').get('respondent_data').get('data').get('respondent_counts').get('total')
_question_list = []
for _qid in _p_question_id:
    _tmp = _result.get('data').get('survey_data').get('questions').get(_qid).get('headings')[0].get('heading')
    _question = pyq(_tmp).text()
    _question_list.append([_qid, _question])
_question_list.sort()
r1 = parse_responses(_result.get('data').get('respondent_data'))

share_view_ajax_url = 'https://zh.surveymonkey.com/results/ajax/shared-view/{}/respondents/responses'.format(survey_key)

post_data = {u'offset': _p_total_responsed_count,
             u'include_openended': True,
             u'prev_neighbors': 5,
             u'questions': _p_question_id,
             u'view_data': {u'name': u'Current View',
                            u'show': {u'selected': False, u'pages': None, u'questions': None},
                            u'view_id': _p_view_id,
                            u'selected_view_id': _p_selected_view_id,
                            u'is_default': False,
                            u'is_current': True,
                            u'survey_id': _p_survey_id,
                            u'type': u'shared',
                            u'page': None,
                            u'metadata': []},
             u'survey_id': _p_survey_id,
             u'next_neighbors': 0}

export_result = {}
for _off in xrange(_p_total_responsed_count-1, -1, -5):
    # print _off
    post_data[u'offset'] = _off
    response = session.post(url=share_view_ajax_url, data=json.dumps(post_data), headers=header, verify=False)
    response.status_code
    _result = json.loads(response.content)
    _result.get('data')
    export_result.update(parse_responses(_result))

suvery_user_list = export_result.keys()
suvery_user_list.sort()
for _erk in suvery_user_list:
    print "\n****************" , export_result.get(_erk).get('ip_address')
    for _q in _question_list:
        print _q[1]
        for idx, val in enumerate(export_result.get(_erk).get('responses').get(_q[0])[1]):
            print "\t", idx+1, val

