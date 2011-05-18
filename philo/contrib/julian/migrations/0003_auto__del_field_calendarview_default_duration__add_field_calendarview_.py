# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'CalendarView.default_duration'
        db.delete_column('julian_calendarview', 'default_duration')

        # Adding field 'CalendarView.default_timespan'
        db.add_column('julian_calendarview', 'default_timespan', self.gf('django.db.models.fields.PositiveIntegerField')(default=7, max_length=5), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'CalendarView.default_duration'
        db.add_column('julian_calendarview', 'default_duration', self.gf('django.db.models.fields.PositiveIntegerField')(default=7, max_length=5), keep_default=False)

        # Deleting field 'CalendarView.default_timespan'
        db.delete_column('julian_calendarview', 'default_timespan')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'julian.calendar': {
            'Meta': {'unique_together': "(('name', 'site', 'language'),)", 'object_name': 'Calendar'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'events': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'calendars'", 'blank': 'True', 'to': "orm['julian.Event']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '5'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'})
        },
        'julian.calendarview': {
            'Meta': {'object_name': 'CalendarView'},
            'calendar': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['julian.Calendar']"}),
            'default_timespan': ('django.db.models.fields.PositiveIntegerField', [], {'default': '7', 'max_length': '5'}),
            'event_detail_page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'calendar_detail_related'", 'to': "orm['philo.Page']"}),
            'events_per_page': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'feed_length': ('django.db.models.fields.PositiveIntegerField', [], {'default': '15', 'null': 'True', 'blank': 'True'}),
            'feed_suffix': ('django.db.models.fields.CharField', [], {'default': "'feed'", 'max_length': '255'}),
            'feed_type': ('django.db.models.fields.CharField', [], {'default': "'text/calendar'", 'max_length': '50'}),
            'feeds_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index_page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'calendar_index_related'", 'to': "orm['philo.Page']"}),
            'item_description_template': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'julian_calendarview_description_related'", 'null': 'True', 'to': "orm['philo.Template']"}),
            'item_title_template': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'julian_calendarview_title_related'", 'null': 'True', 'to': "orm['philo.Template']"}),
            'location_archive_page': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'calendar_location_archive_related'", 'null': 'True', 'to': "orm['philo.Page']"}),
            'location_page': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'calendar_location_related'", 'null': 'True', 'to': "orm['philo.Page']"}),
            'location_permalink_base': ('django.db.models.fields.CharField', [], {'default': "'locations'", 'max_length': '30'}),
            'owner_archive_page': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'calendar_owner_archive_related'", 'null': 'True', 'to': "orm['philo.Page']"}),
            'owner_page': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'calendar_owner_related'", 'null': 'True', 'to': "orm['philo.Page']"}),
            'owner_permalink_base': ('django.db.models.fields.CharField', [], {'default': "'owners'", 'max_length': '30'}),
            'tag_archive_page': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'calendar_tag_archive_related'", 'null': 'True', 'to': "orm['philo.Page']"}),
            'tag_page': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'calendar_tag_related'", 'null': 'True', 'to': "orm['philo.Page']"}),
            'tag_permalink_base': ('django.db.models.fields.CharField', [], {'default': "'tags'", 'max_length': '30'})
        },
        'julian.event': {
            'Meta': {'unique_together': "(('site', 'created'),)", 'object_name': 'Event'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('philo.models.fields.TemplateField', [], {}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            'end_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'location_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'location_pk': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_events'", 'to': "orm['auth.User']"}),
            'parent_event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['julian.Event']", 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'start_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'events'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['philo.Tag']"})
        },
        'julian.location': {
            'Meta': {'object_name': 'Location'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'})
        },
        'philo.attribute': {
            'Meta': {'unique_together': "(('key', 'entity_content_type', 'entity_object_id'), ('value_content_type', 'value_object_id'))", 'object_name': 'Attribute'},
            'entity_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attribute_entity_set'", 'to': "orm['contenttypes.ContentType']"}),
            'entity_object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'value_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'attribute_value_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'value_object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'philo.node': {
            'Meta': {'object_name': 'Node'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['philo.Node']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'view_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'node_view_set'", 'to': "orm['contenttypes.ContentType']"}),
            'view_object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'philo.page': {
            'Meta': {'object_name': 'Page'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pages'", 'to': "orm['philo.Template']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'philo.tag': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'})
        },
        'philo.template': {
            'Meta': {'object_name': 'Template'},
            'code': ('philo.models.fields.TemplateField', [], {}),
            'documentation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'default': "'text/html'", 'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['philo.Template']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'root_node': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sites'", 'null': 'True', 'to': "orm['philo.Node']"})
        }
    }

    complete_apps = ['julian']
