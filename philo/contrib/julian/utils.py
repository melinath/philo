from datetime import date, datetime, timedelta

from django.conf import settings
from django.http import QueryDict


DAY_START = timedelta(hours=getattr(settings, 'JULIAN_DAY_START', 6))


DAY = timedelta(days=1)
WEEK = timedelta(days=7)
MONTH = timedelta(days=28)

START_GET_KEY = 's'
END_GET_KEY = 'e'
TIMESPAN_GET_KEY = 't'
TIMESPAN_GET_PARAMS = {
	'day': DAY,
	'week': WEEK,
	'month': MONTH
}

QUERYSTRING_FORMAT = '%s=%%s&%s=%%s' % (START_GET_KEY, END_GET_KEY)
DATE_FORMAT = '%Y-%m-%d'


def get_request_daterange(request, default_timespan):
	"""Returns a :class:`DateRange` instance for the given request."""
	start = request.GET.get(START_GET_KEY)
	end = request.GET.get(END_GET_KEY)
	timespan = request.GET.get(TIMESPAN_GET_KEY)
	
	if start is not None:
		try:
			start = datetime.strptime(start, DATE_FORMAT)
		except ValueError:
			start = None
	
	if end is not None:
		try:
			end = datetime.strptime(end, DATE_FORMAT)
		except ValueError:
			end = None
	
	if timespan is not None:
		timespan = TIMESPAN_GET_PARAMS.get(timespan)
	
	if timespan is None:
		timespan = default_timespan
	
	return DateRange(start, end, timespan)


def force_start(start):
	return datetime.min.replace(year=start.year, month=start.month, day=start.day)


def force_end(end):
	return datetime.max.replace(year=end.year, month=end.month, day=end.day)


class DateRange(object):
	"""Represents a datetime range from the beginning of one day to the end of another."""
	
	URL_FORMAT = '?%s'

	def __init__(self, start=None, end=None, timespan=None):
		if start is None:
			start = datetime.now()
		self.start = force_start(start) + DAY_START
		
		if end is None or end <= start:
			if timespan is None:
				timespan = WEEK
			timespan = timespan - timedelta(microseconds=1)
			end = self.start + timespan
		
		self.end = force_end(end) + DAY_START
	
	# Is this right? Maybe it should return a text rendering of the range rather than the URL?
	def __unicode__(self):
		return self.url()
	
	def delta(self):
		return (self.end - self.start) + timedelta(microseconds=1)
		
	def url(self):
		qd = QueryDict('', mutable=True)
		qd.update({
			START_GET_KEY: self.start.strftime(DATE_FORMAT),
			END_GET_KEY: self.end.strftime(DATE_FORMAT)
		})
		return self.URL_FORMAT % qd.urlencode()
		
	def next_range(self):
		range_delta = self.end - self.start
		future_start = self.end + timedelta(microseconds=1)
		future_end = future_start + range_delta
		return DateRange(future_start, future_end)
		
	def prev_range(self):
		range_delta = self.end - self.start
		past_end = self.start - timedelta(microseconds=1)
		past_start = past_end - range_delta
		return DateRange(past_start, past_end)