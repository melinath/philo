from django.template import TemplateDoesNotExist
from django.template.loader import BaseLoader
from django.utils.encoding import smart_unicode


class Loader(BaseLoader):
	is_usable=True
	
	def load_template_source(self, template_name, template_dirs=None):
		if hasattr(template_name, "origin"):
			return (template_name, smart_unicode(template_name.origin))
		raise TemplateDoesNotExist(template_name)