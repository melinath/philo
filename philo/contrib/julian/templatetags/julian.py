from datetime import date, datetime, timedelta

from django import template

from philo.contrib.julian.utils import DateRange


register = template.Library()
ONE_DAY = timedelta(days=1)

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