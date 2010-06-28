from django.http import HttpResponse
from philo.contrib.bartleby.models import FormModel, FormItem
from django import forms, template
from philo.contrib.bartleby.forms import modelmultiformset_factory
from django.utils.html import escape
import re


def test_forms(request):
	formset = modelmultiformset_factory(FormItem.plugins, extra=3)
	
	if request.POST:
		regex = re.compile('form-(\d+)-(.*)')
		initial = []
		for field in request.POST:
			search = regex.match(field)
			if search:
				form, fieldname = search.groups()
				form = int(form)
				try:
					initial[form][fieldname] = request.POST[field]
				except IndexError:
					while len(initial) <= form:
						initial.append({})
					
					initial[form][fieldname] = request.POST[field]
		formset = formset(initial=initial)
	else:
		formset = formset()
	
	debug = [request.POST, formset.data, formset.initial]
	debug = '<br />'.join([escape(string) for string in debug])
	
	t = template.Template("<html><body><form method='post'>{% csrf_token %}<table>{{ formset.as_table }}</table><input type='submit' value='Submit' /></form><div id='debug'>" + debug + "</div></body></html>")
	
	context = template.RequestContext(request, {'formset': formset, 'debug': debug})
	
	return HttpResponse(t.render(context))


def test_view(request, formmodel_id):
	form = FormModel.objects.get(id=formmodel_id).form()
	html = '<html><body><table>%s</table></body></html>' % form.as_table()
	return HttpResponse(html)