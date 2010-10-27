# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Form'
        db.create_table('bartleby_form', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('help_text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('save_to_database', self.gf('django.db.models.fields.BooleanField')(default=True, blank=True)),
        ))
        db.send_create_signal('bartleby', ['Form'])

        # Adding M2M table for field email_users on 'Form'
        db.create_table('bartleby_form_email_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('form', models.ForeignKey(orm['bartleby.form'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('bartleby_form_email_users', ['form_id', 'user_id'])

        # Adding M2M table for field email_groups on 'Form'
        db.create_table('bartleby_form_email_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('form', models.ForeignKey(orm['bartleby.form'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('bartleby_form_email_groups', ['form_id', 'group_id'])

        # Adding model 'Field'
        db.create_table('bartleby_field', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.SlugField')(max_length=100, db_index=True)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', to=orm['bartleby.Form'])),
            ('order', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('help_text', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('multiple', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('bartleby', ['Field'])

        # Adding model 'FieldChoice'
        db.create_table('bartleby_fieldchoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='choices', to=orm['bartleby.Field'])),
            ('key', self.gf('django.db.models.fields.SlugField')(max_length=20, db_index=True)),
            ('verbose_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('bartleby', ['FieldChoice'])

        # Adding model 'ResultRow'
        db.create_table('bartleby_resultrow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='result_rows', to=orm['bartleby.Form'])),
            ('submitted', self.gf('django.db.models.fields.DateTimeField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal('bartleby', ['ResultRow'])

        # Adding model 'FieldValue'
        db.create_table('bartleby_fieldvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bartleby.Field'])),
            ('value', self.gf('philo.models.fields.JSONField')()),
            ('row', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bartleby.ResultRow'])),
        ))
        db.send_create_signal('bartleby', ['FieldValue'])

        # Adding unique constraint on 'FieldValue', fields ['field', 'row']
        db.create_unique('bartleby_fieldvalue', ['field_id', 'row_id'])


    def backwards(self, orm):
        
        # Deleting model 'Form'
        db.delete_table('bartleby_form')

        # Removing M2M table for field email_users on 'Form'
        db.delete_table('bartleby_form_email_users')

        # Removing M2M table for field email_groups on 'Form'
        db.delete_table('bartleby_form_email_groups')

        # Deleting model 'Field'
        db.delete_table('bartleby_field')

        # Deleting model 'FieldChoice'
        db.delete_table('bartleby_fieldchoice')

        # Deleting model 'ResultRow'
        db.delete_table('bartleby_resultrow')

        # Deleting model 'FieldValue'
        db.delete_table('bartleby_fieldvalue')

        # Removing unique constraint on 'FieldValue', fields ['field', 'row']
        db.delete_unique('bartleby_fieldvalue', ['field_id', 'row_id'])


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
            'Meta': {'object_name': 'Field'},
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
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'bartleby.fieldvalue': {
            'Meta': {'unique_together': "(('field', 'row'),)", 'object_name': 'FieldValue'},
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bartleby.Field']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'row': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bartleby.ResultRow']"}),
            'value': ('philo.models.fields.JSONField', [], {})
        },
        'bartleby.form': {
            'Meta': {'object_name': 'Form'},
            'email_groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'email_users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'save_to_database': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'bartleby.resultrow': {
            'Meta': {'object_name': 'ResultRow'},
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'result_rows'", 'to': "orm['bartleby.Form']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'submitted': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['bartleby']
