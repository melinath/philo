from django.core.validators import ValidationError
from django.db.models.options import get_verbose_name as convert_camelcase
from datetime import datetime, date

# These should have some way of specifying a widget/formfield to get their data...

class UsageLimitation(object):
	title = None
	
	@property
	def verbose_name(self):
		if self.title is None:
			self.title = convert_camelcase(self.__class__.__name__)
		return self.title
	
	def clean(self, value):
		raise NotImplementedError


class BooleanUsageLimitation(UsageLimitation):
	def clean(self, value):
		if value not in (True, False):
			raise ValidationError("`%s` is not a valid choice for usage limitation %s" % (value, self.verbose_name))
		return value


class PrintOnly(BooleanUsageLimitation):
	pass


class BeforeDate(UsageLimitation):
	def clean(self, value):
		if not isinstance(value, (datetime, date)):
			raise ValidationError("`%s` must be an instance of date or datetime." % value)
		return value


class Resolution(UsageLimitation):
	def clean(self, value):
		try:
			x, y = value
			if not isinstance(x, int) or not isinstance(y, int):
				raise TypeError
		except TypeError:
			raise ValidationError("`%s` must be a pair of integer values" % value)
		return value


class Other(UsageLimitation):
	def clean(self, value):
		if not value:
			raise ValidationError("This field cannot be blank.")
		return value