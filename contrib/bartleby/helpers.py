class Row(object):
	def __init__(self, row, form):
		self.form = form
		self.row = row
		if row.user is not None:
			self.user = row.user.get_full_name() or row.user.username
		else:
			self.user = row.ip_address
		self.submitted = row.submitted
		self.values = dict([(value.field.key, value.value) for value in row.values.filter(field__key__in=form.fields).select_related('field')])
	
	def __iter__(self):
		for key in self.form.fields:
			yield self.values.get(key, "")


class Form(object):
	def __init__(self, form, order_dir=None, order_column=None):
		self.form = form
		self.fields = dict(form.fields.values_list('key', 'label'))
		#if order_dir is not None and order_column is not None:
		#	if order_dir == 'asc':
		#		sign = ""
		#	else:
		#		sign = "-"
		#	if order_column == "1":
		#		arg = 'user__first_name'
		#	elif order_column == "2":
		#		arg = 'submitted'
		#	if order_column in ["1","2"]:
		#		self.results = [Row(result_row, self) for result_row in form.result_rows.order_by("%s%s" % (sign, arg))]
		#		return
		self.results = [Row(result_row, self) for result_row in form.result_rows.all()]
	
	def __iter__(self):
		for key, label in self.fields.items():
			yield "#", label