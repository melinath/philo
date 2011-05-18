from datetime import date, datetime, timedelta
from django import template


register = template.Library()


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
		
	def _get_url(self, context, start_date, end_date):
		start_string = self._date_string(start_date)
		end_string = self._date_string(end_date)
		absolute_url = context['node'].get_absolute_url()
		return u'%s?s=%s&e=%s' % (absolute_url, start_string, end_string,)
		
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
		url = self._get_url(context, start_date, end_date)
		return self._render_or_ctx(context, url)


class ConstantDateRangeNode(BaseDateRangeNode):
	def render(self, context):
		start_date = self.start_date
		end_date = self.end_date
		url = self._get_url(context, start_date, end_date)
		return self._render_or_ctx(context, url)


class NextDateRangeNode(ImpliedDateRangeNode):
	def render(self, context):
		start_date = context['start']
		end_date = context['end']
		range_delta = end_date - start_date
		future_start = end_date
		future_end = end_date + range_delta
		url = self._get_url(context, future_start, future_end)
		return self._render_or_ctx(context, url)


class PrevDateRangeNode(ImpliedDateRangeNode):
	def render(self, context):
		start_date = context['start']
		end_date = context['end']
		range_delta = end_date - start_date
		past_start = start_date - range_delta
		past_end = start_date
		url = self._get_url(context, past_start, past_end)
		return self._render_or_ctx(context, url)


@register.tag(name='range_url')
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


@register.tag(name='next_range_url')
def get_next_date_range_url(parser, token):
	"""
	{% next_range_url [as <var>] %}
	
	Only works on pages with ``start`` and ``end`` in the context (i.e., date range views).
	"""
	
	params = token.split_contents()
	tag = params[0]
	as_var = None
	
	if len(params) >= 3 and params[-2] == 'as':
		as_var = params[-1]
		params = params[:-2]
		
	return NextDateRangeNode(as_var)


@register.tag(name='prev_range_url')
def get_prev_date_range_url(parser, token):
	"""
	{% prev_range_url [as <var>] %}
	
	Only works on pages with ``start`` and ``end`` in the context (i.e., date range views).
	"""
	
	params = token.split_contents()
	tag = params[0]
	as_var = None
	
	if len(params) >= 3 and params[-2] == 'as':
		as_var = params[-1]
		params = params[:-2]
		
	return PrevDateRangeNode(as_var)


@register.filter(name='add_days')
def add_days(value, arg):
	"""Takes a date or datetime object and adds arg days to it."""
	try:
		num = int(arg)
	except:
		return ''
	return value + timedelta(days=num)