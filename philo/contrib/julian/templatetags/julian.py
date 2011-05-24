from datetime import date, datetime, timedelta
from itertools import groupby
from math import floor

from django import template
from django.contrib.humanize.templatetags.humanize import apnumber

from philo.contrib.julian.utils import DateRange, DAY_START


register = template.Library()


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


@register.tag
def date_range(parser, token):
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


class RegroupEventsNode(template.Node):
	def __init__(self, events, as_var):
		self.events = events
		self.as_var = as_var
	
	def key(self, event):
		key = event.get_start() - DAY_START
		if isinstance(key, datetime):
			key = key.date()
		return key
	
	def render(self, context):
		events = self.events.resolve(context, True)
		
		if events is None:
			context[self.as_var] = []
			return ''
		
		context[self.as_var] = [
			{
				'grouper': key,
				'list': list(val)
			}
			for key, val in groupby(events, self.key)
		]
		return ''


@register.tag
def regroup_events(parser, token):
	"""
	Regroups events based on the adjusted day on which they start.
	
	Example::
	
		{% regroup_events events as events %}
	
	"""
	bits = token.split_contents()
	tag = bits[0]
	bits = bits[1:]
	
	if len(bits) > 3 or bits[1] != 'as':
		raise template.TemplateSyntaxError("%s tag expects the syntax {% regroup_events <events> as <events> %}" % tag)
	
	events = parser.compile_filter(bits[0])
	as_var = bits[-1]
	return RegroupEventsNode(events, as_var)


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