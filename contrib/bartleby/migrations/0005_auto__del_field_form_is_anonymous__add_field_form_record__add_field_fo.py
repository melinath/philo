# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Form.is_anonymous'
        db.delete_column('bartleby_form', 'is_anonymous')

        # Adding field 'Form.record'
        db.add_column('bartleby_form', 'record', self.gf('django.db.models.fields.CharField')(default='u', max_length=1), keep_default=False)

        # Adding field 'Form.login_required'
        db.add_column('bartleby_form', 'login_required', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'Form.allow_changes'
        db.add_column('bartleby_form', 'allow_changes', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'Form.max_submissions'
        db.add_column('bartleby_form', 'max_submissions', self.gf('django.db.models.fields.SmallIntegerField')(default=1), keep_default=False)

        # Changing field 'Form.email_from'
        db.alter_column('bartleby_form', 'email_from', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True))

        # Adding field 'ResultRow.cookie'
        db.add_column('bartleby_resultrow', 'cookie', self.gf('django.db.models.fields.CharField')(default='', max_length=20, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Form.is_anonymous'
        db.add_column('bartleby_form', 'is_anonymous', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Deleting field 'Form.record'
        db.delete_column('bartleby_form', 'record')

        # Deleting field 'Form.login_required'
        db.delete_column('bartleby_form', 'login_required')

        # Deleting field 'Form.allow_changes'
        db.delete_column('bartleby_form', 'allow_changes')

        # Deleting field 'Form.max_submissions'
        db.delete_column('bartleby_form', 'max_submissions')

        # Changing field 'Form.email_from'
        db.alter_column('bartleby_form', 'email_from', self.gf('django.db.models.fields.CharField')(max_length=200))

        # Deleting field 'ResultRow.cookie'
        db.delete_column('bartleby_resultrow', 'cookie')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'bartleby.field': {
            'Meta': {'unique_together': "(('key', 'form'),)", 'object_name': 'Field'},
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': "orm['bartleby.Form']"}),
            'help_text': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'multiple': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'bartleby.fieldchoice': {
            'Meta': {'object_name': 'FieldChoice'},
            'field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'choices'", 'to': "orm['bartleby.Field']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'max_length': '20', 'db_index': 'True'}),
            'order': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'bartleby.fieldvalue': {
            'Meta': {'unique_together': "(('field', 'row'),)", 'object_name': 'FieldValue'},
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bartleby.Field']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'row': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': "orm['bartleby.ResultRow']"}),
            'value': ('philo.models.fields.JSONField', [], {})
        },
        'bartleby.form': {
            'Meta': {'object_name': 'Form'},
            'allow_changes': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'email_from': ('django.db.models.fields.CharField', [], {'default': "u'noreply@example.com'", 'max_length': '200', 'blank': 'True'}),
            'email_groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'email_template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['philo.Template']", 'null': 'True', 'blank': 'True'}),
            'email_users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'max_submissions': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'record': ('django.db.models.fields.CharField', [], {'default': "'u'", 'max_length': '1'}),
            'save_to_database': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'bartleby.resultrow': {
            'Meta': {'object_name': 'ResultRow'},
            'cookie': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'result_rows'", 'to': "orm['bartleby.Form']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'submitted': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'philo.attribute': {
            'Meta': {'unique_together': "(('key', 'entity_content_type', 'entity_object_id'), ('value_content_type', 'value_object_id'))", 'object_name': 'Attribute'},
            'entity_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attribute_entity_set'", 'to': "orm['contenttypes.ContentType']"}),
            'entity_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'value_content_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'attribute_value_set'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'value_object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'philo.foreignkeyvalue': {
            'Meta': {'object_name': 'ForeignKeyValue'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'philo.template': {
            'Meta': {'object_name': 'Template'},
            'code': ('philo.models.fields.TemplateField', [], {}),
            'documentation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'default': "'text/html'", 'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['philo.Template']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['bartleby']
