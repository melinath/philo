# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    depends_on = (
        ("philo", "0007_auto__del_relationship__del_field_attribute_value"),
    )
    def forwards(self, orm):
        
        # Adding model 'Resource'
        db.create_table('edmonia_resource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, db_index=True)),
            ('creation_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('creation_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('edmonia', ['Resource'])

        # Adding model 'ResourceRelated'
        db.create_table('edmonia_resourcerelated', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rel_content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('rel_object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('resource', self.gf('django.db.models.fields.related.ForeignKey')(related_name='related', to=orm['edmonia.Resource'])),
        ))
        db.send_create_signal('edmonia', ['ResourceRelated'])


    def backwards(self, orm):
        
        # Deleting model 'Resource'
        db.delete_table('edmonia_resource')

        # Deleting model 'ResourceRelated'
        db.delete_table('edmonia_resourcerelated')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'edmonia.resource': {
            'Meta': {'object_name': 'Resource'},
            'creation_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'creation_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'edmonia.resourcerelated': {
            'Meta': {'object_name': 'ResourceRelated'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rel_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'rel_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'related'", 'to': "orm['edmonia.Resource']"})
        },
        'philo.attribute': {
            'Meta': {'unique_together': "(('key', 'entity_content_type', 'entity_object_id'), ('value_content_type', 'value_object_id'))", 'object_name': 'Attribute'},
            'entity_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attribute_entity_set'", 'to': "orm['contenttypes.ContentType']"}),
            'entity_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'attribute_value_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'value_object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['edmonia']
