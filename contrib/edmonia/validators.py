import mimetypes
import os


class FileTypeValidator(object):
	"""
	This validator makes sure that a file's mimetype is in a certain list. The mimetype check uses
	the built-in mimetype library. TODO: it would be great to use python-magic, if it's available.
	"""
	def __init__(self, allowed=None, disallowed=None):
		self.disallowed = set([self.convert(ftype) for ftype in disallowed or []])
		self.allowed = set([self.convert(ftype) for ftype in allowed or []]) - self.disallowed
	
	def __call__(self, value):
		try:
			mimetype = self.convert(os.path.splitext(value.name)[1])
		except Exception, e:
			raise ValidationError(e.message)
		
		if self.allowed and mimetype not in self.allowed:
			raise ValidationError(_(u"Only the following mime types may be uploaded: %s" % ', '.join(self.allowed)))
		if self.disallowed and mimetype not in self.disallowed:
			raise ValidationError(_(u"The following mime types may not be uploaded: %s" % ', '.join(self.disallowed)))
	
	def convert(self, ftype):
		if '.' in ftype:
			try:
				return mimetypes.types_map[ftype]
			except KeyError:
				return mimetypes.common_types[ftype]
		elif '/' in ftype:
			if ftype in mimetypes.types_map.values() or ftype in mimetypes.common_types.values():
				return ftype
			else:
				raise ValueError(_(u'Unknown MIME-type: %s' % ftype))
		else:
			raise ValueError(_('Invalid MIME-type: %s' % ftype))