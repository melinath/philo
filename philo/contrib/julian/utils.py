from datetime import date, datetime, timedelta

ONE_DAY = timedelta(days=1)

START_GET_KEY = 's'
END_GET_KEY = 'e'
QUERYSTRING_FORMAT = '%s=%%s&%s=%%s' % (START_GET_KEY, END_GET_KEY)
DATE_FORMAT = '%04d-%02d-%02d'

class DateRange(object):
	"""Represents a Julian date range."""
	
	URL_FORMAT = '?%s'

	def __init__(self, start, end):
		if (isinstance(start, datetime) or isinstance(start, date)) and (isinstance(end, datetime) or isinstance(end, date)):
			self.start = start
			self.end = end
		else:
			raise TypeError('start and end must be date or datetime objects')
	
	# Is this right? Maybe it should return a text rendering of the range rather than the URL?
	def __unicode__(self):
		return self.url()
		
	def url(self):
		start_string = DATE_FORMAT % (self.start.year, self.start.month, self.start.day)
		end_string = DATE_FORMAT % (self.end.year, self.end.month, self.end.day)
		querystring = QUERYSTRING_FORMAT % (start_string, end_string)
		return self.URL_FORMAT % (querystring,)
		
	def next_range(self):
		range_delta = self.end - self.start + ONE_DAY
		future_start = self.end
		future_end = self.end + range_delta
		return DateRange(future_start, future_end)
		
	def prev_range(self):
		range_delta = self.end - self.start
		past_start = self.start - range_delta - ONE_DAY
		past_end = self.start - ONE_DAY
		return DateRange(past_start, past_end)