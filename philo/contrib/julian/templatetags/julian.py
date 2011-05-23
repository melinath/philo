from datetime import date, datetime, timedelta
from math import floor

from django import template
from django.contrib.humanize.templatetags.humanize import apnumber

from philo.contrib.julian.utils import DateRange


register = template.Library()


ONE_DAY = timedelta(days=1)
MONTH_LENGTH = 30.436875 # http://en.wikipedia.org/wiki/Month#Julian_and_Gregorian_calendars


class BaseDateRangeNode(template.Node):
	DATE_FORMAT = '%04d-%02d-%02d'
	
	def __init__(self, start_date, end_date, as_var):
		"start_date and end_date must be datetime or date objects"
		self.as_var = as_var
		self.start_date = start_date
		self.end_date = end_date
		
	def _date_string(self, date_):
		string = self.DATE_FORMAT % (date_.year, date_.month, date_.day,)
		return string
		
	def _get_range_object(self, context, start_date, end_date):
		return DateRange(start_date, end_date)
		
	def _render_or_ctx(self, context, value):
		if self.as_var is not None:
			context[self.as_var] = value
			return ''
		else:
			return value


class ImpliedDateRangeNode(BaseDateRangeNode):
	def __init__(self, as_var):
		self.as_var = as_var


class DateRangeNode(BaseDateRangeNode):
	def render(self, context):
		start_date = self.start_date.resolve(context)
		end_date = self.end_date.resolve(context)
		url = self._get_range_object(context, start_date, end_date)
		return self._render_or_ctx(context, url)


class ConstantDateRangeNode(BaseDateRangeNode):
	def render(self, context):
		start_date = self.start_date
		end_date = self.end_date
		url = self._get_range_object(context, start_date, end_date)
		return self._render_or_ctx(context, url)


@register.tag(name='date_range')
def get_date_range_url(parser, token):
	"""
	{% range_url start_date end_date [as <var>] %}
	{% range_url "yyyy-mm-dd" "yyyy-mm-dd" [as <var>] %}
	"""
	params = token.split_contents()
	tag = params[0]
	start_date = params[1]
	end_date = params[2]
	as_var = None
	params = params[1:]
	
	if len(params) >= 3 and params[-2] == 'as':
		as_var = params[-1]
		params = params[:-2]
	
	if start_date[0] in ('"',"'") and start_date[-1] == start_date[0] and start_date[0] in ('"',"'") and start_date[-1] == start_date[0]:
		start_date = date(*start_date.split('-'))
		end_date = date(*start_date.split('-'))
	else:
		start_date = parser.compile_filter(start_date)
		end_date = parser.compile_filter(end_date)
	
	return DateRangeNode(start_date, end_date, as_var)


@register.filter(name='add_days')
def add_days(value, arg):
	"""Takes a date or datetime object and adds arg days to it."""
	try:
		num = int(arg)
	except:
		return ''
	return value + timedelta(days=num)


@register.filter(name='add_minutes')
def add_minutes(value, arg):
	"""Takes a date or datetime object and adds arg days to it."""
	try:
		num = int(arg)
	except:
		return ''
	return value + timedelta(minutes=num)
	
@register.filter(name='naturaldelta')
def naturaldelta(value, arg=2):
	"""
	Takes a timedelta and returns it as a string of counts and units, rounding off insignificant units.
	Argument is the number of units of specificity.
	"""
	try:
		days = value.days
		seconds = value.seconds
		microseconds = value.microseconds
	except:
		return ''
	
	units = {}
	unit_count = int(arg)
	
	# day portion parsing
	units['years'] = floor(days / 365)
	rdays = days % 365
	units['months'] = floor(rdays / MONTH_LENGTH)
	rdays = rdays % MONTH_LENGTH
	units['weeks'] = floor(rdays / 7)
	units['days'] = round(rdays % 7)
	
	# second portion parsing
	units['hours'] = floor(seconds / 3600)
	rsecs = seconds % 3600
	units['minutes'] = floor(rsecs / 60)
	units['seconds'] = round(rsecs % 60)
	
	# microsecond parsing
	milleseconds = floor(microseconds / 1000)
	microseconds = round(microseconds % 1000)
	
	bits = []
	
	for unit, count in units.items():
		if count > 0:
			unit_name = unit if count > 1 else unit[:-1] # depluralize if necessary
			bits.append('%s %s' % (apnumber(count), unit_name))
		
	return " ".join(bits[:unit_count])