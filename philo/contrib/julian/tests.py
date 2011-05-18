import datetime

from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.test import TestCase
from django.test.client import RequestFactory

from philo.contrib.julian.models import Event, CalendarView


def create_event(name, description, user, start, end, start_null=False, end_null=False):
	if start_null:
		start_time = None
	else:
		start_time = start
	
	if end_null:
		end_time = None
	else:
		end_time = end
	
	Event.objects.create(
		name=name,
		slug=slugify(name),
		description=description,
		owner=user,
		start_date=start,
		start_time=start_time,
		end_date=end,
		end_time=end_time
	)


def create_events(now):
	in_half = datetime.timedelta(minutes=30)
	half_before = datetime.timedelta(minutes=-30)
	in_three = datetime.timedelta(hours=3)
	three_before = datetime.timedelta(hours=-3)
	
	day_before = datetime.timedelta(days=-1)
	in_day = datetime.timedelta(days=1)
	
	user = User.objects.get(username="test")
	
	create_event("Event1", "First event", user, now + three_before, now + half_before)
	
	create_event("Event2", "Second event", user, now + in_half, now + in_three)
	
	create_event("Event3", "Third event", user, now + half_before, now + in_half)
	
	create_event("Event4", "Fourth event", user, now + day_before, now + day_before + in_three)
	
	create_event("Multiday1", "First multiday", user, now + day_before, now + in_day)


class EventTestCase(TestCase):
	fixtures = ["julian_test"]
	urls = 'philo.urls'
	
	def setUp(self):
		self.now = datetime.datetime.now()
		create_events(self.now)
	
	def test_timespan(self):
		four_before = datetime.timedelta(hours=-4)
		in_four = datetime.timedelta(hours=4)
		one_before = datetime.timedelta(hours=-1)
		
		qs = Event.objects.timespan(start=self.now + four_before, end=self.now + in_four)
		self.assertQuerysetEqual(qs, ['<Event: Event1>', '<Event: Event2>', '<Event: Event3>', '<Event: Multiday1>'])
		
		qs = Event.objects.timespan(start=self.now + four_before, end=self.now + one_before)
		self.assertQuerysetEqual(qs, ['<Event: Event1>', '<Event: Multiday1>'])
	
	def test_current(self):
		qs = Event.objects.current(now=self.now)
		self.assertQuerysetEqual(qs, ['<Event: Event3>', '<Event: Multiday1>'])
	
	def test_single_day(self):
		qs = Event.objects.single_day()
		self.assertQuerysetEqual(qs, ['<Event: Event1>', '<Event: Event2>', '<Event: Event3>', '<Event: Event4>'])
	
	def test_multiday(self):
		qs = Event.objects.multiday()
		self.assertQuerysetEqual(qs, ['<Event: Multiday1>'])
	
	def test_upcoming(self):
		qs = Event.objects.upcoming(now=self.now)
		self.assertQuerysetEqual(qs, ['<Event: Event2>'])


class CalendarViewTestCase(TestCase):
	fixtures = ["julian_test"]
	urls = 'philo.urls'
	
	def setUp(self):
		self.factory = RequestFactory()
	
	def test_request_timespan(self):
		view = CalendarView.objects.all()[0]
		request = self.factory.get('?s=2011-05-02')
		qs, c = view.get_request_timespan(request)
		self.assertEqual(c['start'], datetime.datetime(year=2011, month=5, day=2))
		self.assertEqual(c['end'], datetime.datetime(year=2011, month=5, day=2 + view.default_timespan))
		
		request = self.factory.get('?s=2011-05-02&e=2011-06-04')
		qs, c = view.get_request_timespan(request)
		self.assertEqual(c['start'], datetime.datetime(year=2011, month=5, day=2))
		self.assertEqual(c['end'], datetime.datetime(year=2011, month=6, day=4))
		
		request = self.factory.get('?s=2011-05-02&e=2011-06-04&t=day')
		qs, c = view.get_request_timespan(request)
		self.assertEqual(c['start'], datetime.datetime(year=2011, month=5, day=2))
		self.assertEqual(c['end'], datetime.datetime(year=2011, month=6, day=4))
		
		request = self.factory.get('?s=2011-05-02&t=day')
		qs, c = view.get_request_timespan(request)
		self.assertEqual(c['start'], datetime.datetime(year=2011, month=5, day=2))
		self.assertEqual(c['end'], datetime.datetime(year=2011, month=5, day=3))