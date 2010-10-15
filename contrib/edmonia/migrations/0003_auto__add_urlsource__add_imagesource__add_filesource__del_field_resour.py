# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'URLSource'
        db.create_table('edmonia_urlsource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal('edmonia', ['URLSource'])

        # Adding model 'ImageSource'
        db.create_table('edmonia_imagesource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal('edmonia', ['ImageSource'])

        # Adding model 'FileSource'
        db.create_table('edmonia_filesource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('edmonia', ['FileSource'])

        # Deleting field 'Resource.timestamp'
        db.delete_column('edmonia_resource', 'timestamp')

        # Adding field 'Resource.timestamp_added'
        db.add_column('edmonia_resource', 'timestamp_added', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2010, 10, 15, 15, 4, 48, 94213)), keep_default=False)

        # Adding field 'Resource.timestamp_modified'
        db.add_column('edmonia_resource', 'timestamp_modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2010, 10, 15, 15, 4, 55, 721726)), keep_default=False)

        # Adding field 'Resource.source_content_type'
        db.add_column('edmonia_resource', 'source_content_type', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['contenttypes.ContentType']), keep_default=False)

        # Adding field 'Resource.source_object_id'
        db.add_column('edmonia_resource', 'source_object_id', self.gf('django.db.models.fields.PositiveIntegerField')(default=0), keep_default=False)

        # Adding M2M table for field related_resources on 'Resource'
        db.create_table('edmonia_resource_related_resources', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_resource', models.ForeignKey(orm['edmonia.resource'], null=False)),
            ('to_resource', models.ForeignKey(orm['edmonia.resource'], null=False))
        ))
        db.create_unique('edmonia_resource_related_resources', ['from_resource_id', 'to_resource_id'])


    def backwards(self, orm):
        
        # Deleting model 'URLSource'
        db.delete_table('edmonia_urlsource')

        # Deleting model 'ImageSource'
        db.delete_table('edmonia_imagesource')

        # Deleting model 'FileSource'
        db.delete_table('edmonia_filesource')

        # Adding field 'Resource.timestamp'
        db.add_column('edmonia_resource', 'timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2010, 10, 15, 15, 4, 36, 754299)), keep_default=False)

        # Deleting field 'Resource.timestamp_added'
        db.delete_column('edmonia_resource', 'timestamp_added')

        # Deleting field 'Resource.timestamp_modified'
        db.delete_column('edmonia_resource', 'timestamp_modified')

        # Deleting field 'Resource.source_content_type'
        db.delete_column('edmonia_resource', 'source_content_type_id')

        # Deleting field 'Resource.source_object_id'
        db.delete_column('edmonia_resource', 'source_object_id')

        # Removing M2M table for field related_resources on 'Resource'
        db.delete_table('edmonia_resource_related_resources')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'edmonia.filesource': {
            'Meta': {'object_name': 'FileSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'edmonia.imagesource': {
            'Meta': {'object_name': 'ImageSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'})
        },
        'edmonia.resource': {
            'Meta': {'object_name': 'Resource'},
            'creation_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'creation_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'related_resources': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'related_resources_rel_+'", 'null': 'True', 'to': "orm['edmonia.Resource']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'source_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'source_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'timestamp_added': ('django.db.models.fields.DateTimeField', [], {}),
            'timestamp_modified': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'edmonia.resourcerelated': {
            'Meta': {'object_name': 'ResourceRelated'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'related_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'related_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'related'", 'to': "orm['edmonia.Resource']"})
        },
        'edmonia.urlsource': {
            'Meta': {'object_name': 'URLSource'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.URLField', [], {'max_length': '200'})
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
