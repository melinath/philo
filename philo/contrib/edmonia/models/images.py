import mimetypes
import os
import itertools

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage
from django.core.files.temp import NamedTemporaryFile
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import MinValueValidator
from django.db import models
from django.template.loader import render_to_string
from django.utils.encoding import smart_str, smart_unicode
import Image

from philo.models import Entity
from philo.contrib.edmonia.utils.images import crop, scale, crop_and_scale, clear_image_cache
from philo.contrib.edmonia.validators import FileTypeValidator
try:
	from philo.contrib.edmonia.utils.images import seam_carve
except ImportError:
	seam_carve = None


__all__ = ('Image', 'ProtectedArea', 'AdjustedImage', 'ImageGallery', 'ImageGalleryOrder', 'ImageMetadata')


class ImageSource(ResourceSource):
	source = models.ImageField(upload_to='edmonia/images/%Y/%m/%d', validators=[FileTypeValidator(['.jpg', '.gif', '.png'])], help_text="Allowed file types: .jpg, .gif, and .png", height_field='height', width_field='width')
	timestamp = models.DateTimeField(auto_now_add=True)
	
	height = models.PositiveIntegerField()
	width = models.PositiveIntegerField()
	
	def save(self, *args, **kwargs):
		super(Image, self).save(*args, **kwargs)
		clear_image_cache(self.slug)
	
	def delete(self, *args, **kwargs):
		super(Image, self).save(*args, **kwargs)
		clear_image_cache(self.slug)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		app_label = 'edmonia'


class ProtectedArea(models.Model):
	image = models.ForeignKey(ImageSource, related_name="protected_areas")
	
	x1 = models.PositiveIntegerField(validators=[MinValueValidator(0)])
	y1 = models.PositiveIntegerField(validators=[MinValueValidator(0)])
	x2 = models.PositiveIntegerField(validators=[MinValueValidator(1)])
	y2 = models.PositiveIntegerField(validators=[MinValueValidator(1)])
	
	priority = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=3)
	
	@property
	def area(self):
		if self.x1 is None or self.y1 is None or self.x2 is None or self.y2 is None:
			return None
		return self.width * self.height
	
	@property
	def width(self):
		return self.x2 - self.x1
	
	@property
	def height(self):
		return self.y2 - self.y1
	
	def clean_fields(self, exclude=None):
		errors = {}
		
		if exclude is None:
			exclude = []
		
		try:
			super(ProtectedArea, self).clean_fields(exclude)
		except ValidationError, e:
			errors.update(e.message_dict)
		
		if 'x2' not in exclude and self.x2 > self.image.width:
			errors.setdefault('x2', []).append(u"Ensure that this value is less than or equal to %d." % self.image.width)
		if 'y2' not in exclude and self.y2 > self.image.height:
			errors.setdefault('y2', []).append(u"Ensure that this value is less than or equal to %d." % self.image.height)
		
		if errors:
			raise ValidationError(errors)
	
	def clean(self):
		errors = []
		if self.x1 and self.x2 and self.x1 >= self.x2:
			errors.append("X1 must be less than X2.")
		if self.y1 and self.y2 and self.y1 >= self.y2:
			errors.append("Y1 must be less than Y2.")
		if errors:
			raise ValidationError(errors)
	
	def __unicode__(self):
		return u"Protected Area (%d, %d, %d, %d / %d) for %s" % (self.x1, self.y1, self.x2, self.y2, self.priority, self.image)
	
	class Meta:
		app_label = 'edmonia'
		ordering = ('priority',)


class TemporaryImageFile(UploadedFile):
	def __init__(self, name, image, format):
		if settings.FILE_UPLOAD_TEMP_DIR:
			file = NamedTemporaryFile(suffix='.upload', dir=settings.FILE_UPLOAD_TEMP_DIR)
		else:
			file = NamedTemporaryFile(suffix='.upload')
		image.save(file, format)
		content_type = "image/%s" % format.lower()
		# Should we even bother calculating the size?
		size = os.path.getsize(file.name)
		super(TemporaryImageFile, self).__init__(file, name, content_type, size)
	
	def temporary_file_path(self):
		return self.file.name
	
	def close(self):
		try:
			return self.file.close()
		except OSError, e:
			if e.errno != 2:
				# Means the file was moved or deleted before the tempfile
				# could unlink it. Still sets self.file.close_called and
				# calls self.file.file.close() before the exception
				raise


class AdjustedImageManager(models.Manager):
	def adjust_image(self, image, width=None, height=None, method=None):
		image.image.seek(0)
		im = PILImage.open(image.image)
		format = im.format
		
		if method == 'seam' and seam_carve:
			im = seam_carve(im, width, height)
		elif method == 'crop':
			im = crop(im, width, height, protected=image.protected_areas.all())
		elif method == 'scale':
			im = scale(im, width, height)
		else:
			im = crop_and_scale(im, width, height, protected=image.protected_areas.all())
		
		adjusted = self.model(image=image, requested_width=width, requested_height=height)
		f = adjusted._meta.get_field('adjusted')
		ext = mimetypes.guess_extension('image/%s' % format.lower())
		
		# dot is included in ext.
		filename = "%sx%s_%s%s" % (smart_str(width, 'ascii'), smart_str(height, 'ascii'), image.slug, ext)
		filename = f.generate_filename(adjusted, filename)
		
		temp = TemporaryImageFile(filename, im, format)
		
		adjusted.adjusted = temp
		# Try to handle race conditions gracefully.
		try:
			adjusted = self.get(image=image, requested_width=width, requested_height=height)
		except self.model.DoesNotExist:
			adjusted.save()
		else:
			temp.close()
		return adjusted


class AdjustedImage(models.Model):
	#SCALE = 'scale'
	#CROP = 'crop'
	#SEAM = 'seam'
	#SCALE_CROP = 'scale+crop'
	objects = AdjustedImageManager()
	
	image = models.ForeignKey(ImageSource)
	adjusted = models.ImageField(height_field='height', width_field='width', upload_to='edmonia/images/adjusted/%Y/%m/%d/', max_length=255)
	timestamp = models.DateTimeField(auto_now_add=True)
	
	width = models.PositiveIntegerField(db_index=True)
	height = models.PositiveIntegerField(db_index=True)
	
	requested_width = models.PositiveIntegerField(db_index=True, blank=True, null=True)
	requested_height = models.PositiveIntegerField(db_index=True, blank=True, null=True)
	
	def as_html(self):
		ctx = {'image': {
			'src': self.adjusted.url,
			'height': self.height,
			'width': self.width,
			'alt': self.image.name
		}}
		return render_to_string('assets/image_tag.html', ctx)
	as_html.short_description = 'image'
	as_html.allow_tags = True
	
	def delete(self, *args, **kwargs):
		super(AdjustedImage, self).delete(*args, **kwargs)
		clear_image_cache(self.image.slug, self.width, self.height)
	
	def __unicode__(self):
		return u"(%s, %s) adjustment for %s" % (smart_unicode(self.requested_width), smart_unicode(self.requested_height), self.image)
	
	class Meta:
		app_label = 'edmonia'
		unique_together = ('image', 'requested_width', 'requested_height')


class ImageMetadata(Entity):
	image = models.OneToOneField(ImageSource, related_name='metadata')
	caption = models.TextField(help_text='May contain HTML', blank=True)
	credit = models.CharField(max_length=100, blank=True)
	artist = models.ForeignKey(getattr(settings, 'PHILO_PERSON_MODULE', 'auth.User'), blank=True, null=True)
	creation_date = models.DateField(blank=True, null=True, help_text="The date that the image was created, not the date it was added to the system.")
	
	def __unicode__(self):
		return u"Metadata for %s" % self.image
	
	class Meta:
		app_label = 'edmonia'