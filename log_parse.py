# -*- encoding: utf-8 -*-

import re
from collections import Counter
from datetime import datetime


def create_pattern(ignore_files, request_type, ignore_www, slow_queries):

	pattern = '{date} "{req_type} {request} {protocol}" {response_code} {response_time}'

	date = '\[(?P<date>\d+/\w+/\d+ \d+:\d+:\d+)\]'

	if(request_type is None):
		req_type = '\w+'
	else:
		req_type = request_type
    
	if(ignore_files):
		request = '\w+://{}(?P<request>[\w.]+[^ \t\n\r.]*)'
	else:
		request = '\w+://{}(?P<request>[\w.]+[^ \t\n\r]*)'

	if(ignore_www):
		request = request.format("(?:www\.)?")
	else:
		request = request.format("")

	protocol = '\S*'

	response_code = '\d+'

	if(slow_queries):
		response_time = '(?P<response_time>\d+)'
	else:
		response_time = '\d+'

	fields = {'date': date, 'req_type': req_type, 'request': request, 'protocol': protocol, 'response_code': response_code, 'response_time': response_time}

	pattern = pattern.format(**fields)
	return pattern



def parse(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type=None,
    ignore_www=False,
    slow_queries=False):

	file = open("log.log")

	pattern = create_pattern(ignore_files, request_type, ignore_www, slow_queries)
	pattern = re.compile(pattern)
	count = Counter()

	if slow_queries:
		response_time = Counter()

	if start_at:
		start_at = datetime.strptime(start_at, '%d/%m/%Y %X')

	if stop_at:
		stop_at = datetime.strptime(stop_at, '%d/%m/%Y %X')

	for line in file:
		search = pattern.search(line)

		if search:
			search = search.groupdict()
			count[search['request']] += 1
			log = datetime.strptime(search['date'], '%d/%b/%Y %X')

			if start_at:
				if log < start_at:
					continue

			if stop_at:
				if log > stop_at:
					break

			if slow_queries:
				response_time[search['request']] += int(search['response_time'])

	if slow_queries:
		for i in count:
			count[i] = response_time[i] // count[i]
                
	file.close()

	return [out[1] for out in count.most_common(5)]
