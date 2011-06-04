from django.utils.datastructures import SortedDict


class Row(object):
	def __init__(self, row, formview):
		self.formview = formview
		self.row = row
		if row.user is not None:
			self.user = row.user.get_full_name() or row.user.username
		else:
			self.user = row.ip_address
		self.submitted = row.submitted
		
		values = row.values.filter(field__form__in=formview.form_steps.keys()).select_related('field', 'field__form')
		self.values = {}
		for value in values:
			step = formview.form_steps[value.field.form]
			self.values[(step.order, step.name, value.field.key)] = value.value
	
	def __iter__(self):
		for key in self.formview.fields:
			yield self.values.get(key, "")


class Header(object):
	def __init__(self, form, label, index):
		self.label = label
		self.index = index
		self.form = form
		
		if index < 3:
			direction = 'asc'
			if form.order_column == index and form.order_dir == 'asc':
				direction = 'desc'
			qdict = form.request.GET.copy()
			qdict['ot%d' % form.index] = direction
			qdict['o%d' % form.index] = index
			self.url = "?%s" % qdict.urlencode()
		else:
			self.url = None
	
	def classes(self):
		if self.index > 2:
			return
		
		if self.form.order_column == self.index:
			if self.form.order_dir == 'asc':
				return "sorted ascending sortable"
			elif self.form.order_dir == 'desc':
				return "sorted descending sortable"
		
		return "sortable"


class FormView(object):
	def __init__(self, formview, index, request):
		self.formview = formview
		self.fields = SortedDict()
		self.steps = formview.steps.select_related('form')
		self.form_steps = {}
		
		for step in self.steps:
			self.form_steps[step.form] = step
			for key, label in step.form.fields.values_list('key', 'label'):
				self.fields[(step.order, step.name, key)] = label
		
		self.index = index
		self.request = request
		
		try:
			order_dir, order_column = request.GET['ot%d' % index], int(request.GET['o%d' % index])
		except KeyError, ValueError:
			order_dir = order_column = None
		self.order_dir, self.order_column = order_dir, order_column
		
		self.headers = [Header(self, label, index + 1) for index, label in enumerate(['Submitter', 'Submit time'] + self.fields.values())]
		
		if order_dir is not None and order_column is not None:
			if order_column == 1:
				if order_dir == 'asc':
					args = ['user', 'ip_address', 'cookie']
				else:
					args = ['-user', '-ip_address', '-cookie']
			elif order_column == 2:
				if order_dir == 'asc':
					args = ['submitted']
				else:
					args = ['-submitted']
			
			if order_column in [1,2]:
				self.results = [Row(result_row, self) for result_row in formview.result_rows.order_by(*args)]
				return
		self.results = [Row(result_row, self) for result_row in formview.result_rows.all()]
	
	def __iter__(self):
		for label in self.fields.values():
			yield label