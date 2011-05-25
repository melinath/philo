from django import template
from django.conf import settings
from django.template.defaulttags import kwarg_re
from philo.contrib.edmonia.models.images import Image, AdjustedImage


register = template.Library()


class ImageResizeNode(template.Node):
	def __init__(self, image, width=None, height=None, asvar=None):
		self.image = image
		self.width = width
		self.height = height
		self.asvar = asvar
	
	def render(self, context):
		image = self.image.resolve(context)
		width = self.width.resolve(context) if self.width else None
		height = self.height.resolve(context) if self.height else None
		
		if (width == image.width and height == image.height) or (width is height is None):
			return image.source.url
		
		try:
			adjusted = image.adjustedimage_set.get(requested_width=width, requested_height=height)
		except AdjustedImage.DoesNotExist:
			adjusted = AdjustedImage.objects.adjust_image(image, width=width, height=height)
		
		return adjusted.adjusted.url


@register.tag
def resize(parser, token):
	"""
	To be used in a template for image resizing and cropping.
	
	Syntax::
	
		{% resize <image> [width=<int/var>] [height=<int/var>] [as <varname>] %}
	
	If only one of width/height is supplied, the proportions are automatically constrained.
	Cropping and resizing will each only take place if the relevant variables are defined.
	
	"""
	params = token.split_contents()
	
	if len(params) < 2:
		raise template.TemplateSyntaxError('"%s" template tag requires at least two arguments' % tag)
	
	tag = params[0]
	image = parser.compile_filter(params[1])
	params = params[2:]
	asvar = None
	
	if len(params) > 1:
		if params[-2] == 'as':
			asvar = params[-1]
			params = params[:-2]
	
	valid_kwargs = ('width', 'height')
	kwargs = {'asvar': asvar}
	
	for param in params:
		match = kwarg_re.match(param)
		if not match:
			raise template.TemplateSyntaxError("Malformed arguments to `%s` tag" % tag)
		name, value = match.groups()
		if name not in valid_kwargs:
			raise template.TemplateSyntaxError("Invalid argument to `%s` tag: %s" % (tag, name))
		kwargs[str(name)] = parser.compile_filter(value)
	
	return ImageResizeNode(image, **kwargs)