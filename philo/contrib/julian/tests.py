import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from philo.contrib.julian.models import Event


def create_events(now):
	in_half = datetime.timedelta(minutes=30)
	half_before = datetime.timedelta(minutes=-30)
	in_three = datetime.timedelta(hours=3)
	three_before = datetime.timedelta(hours=-3)
	
	day_before = datetime.timedelta(days=-1)
	in_day = datetime.timedelta(days=1)
	
	user = User.objects.get(username="test")
	
	Event.objects.create(
		name="Event1",
		slug="event1",
		description="First event",
		owner=user,
		start_date = now + three_before,
		end_date = now + half_before
	)
	Event.objects.create(
		name="Event2",
		slug="event2",
		description="Second event",
		owner=user,
		start_date = now + in_half,
		end_date = now + in_three
	)
	Event.objects.create(
		name="Event3",
		slug="event3",
		description="Third event",
		owner=user,
		start_date = now + half_before,
		end_date = now + in_half
	)
	Event.objects.create(
		name="Event4",
		slug="event4",
		description="Fourth event",
		owner=user,
		start_date = now + day_before,
		end_date = now + day_before + in_three
	)


class EventTestCase(TestCase):
	fixtures = ["julian_test"]
	urls = 'philo.urls'
	
	def setUp(self):
		self.now = datetime.datetime.now()
		create_events(self.now)
	
	def test_timespan(self):
		day_start = self.now.replace(hour=0, minute=0, second=0, microsecond=0)
		day_end = datetime.datetime.max.replace(year=self.now.year, day=self.now.day, month=self.now.month)
		today_qs = Event.objects.all().timespan(start=day_start, end=day_end)
		self.assertQuerysetEqual(today_qs, ['<Event: Event1>', '<Event: Event2>', '<Event: Event3>'])


#class ClassifiedsViewTestCase(TestCase):
#	fixtures = ["julian_test"]
#	urls = 'philo.urls'