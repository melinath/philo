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
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=150)),
            ('help_text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('email_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['philo.Template'], null=True, blank=True)),
            ('email_from', self.gf('django.db.models.fields.CharField')(default=u'noreply@127.0.0.1:8000', max_length=200, blank=True)),
            ('save_to_database', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('record', self.gf('django.db.models.fields.CharField')(default='u', max_length=1)),
            ('login_required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('allow_changes', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('max_submissions', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
        ))
        db.send_create_signal('bartleby', ['Form'])

        # Adding M2M table for field pages on 'Form'
        db.create_table('bartleby_form_pages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('form', models.ForeignKey(orm['bartleby.form'], null=False)),
            ('page', models.ForeignKey(orm['philo.page'], null=False))
        ))
        db.create_unique('bartleby_form_pages', ['form_id', 'page_id'])

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
            ('key', self.gf('django.db.models.fields.SlugField')(max_length=100)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='fields', to=orm['bartleby.Form'])),
            ('order', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('help_text', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('multiple', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('bartleby', ['Field'])

        # Adding unique constraint on 'Field', fields ['key', 'form']
        db.create_unique('bartleby_field', ['key', 'form_id'])

        # Adding model 'FieldChoice'
        db.create_table('bartleby_fieldchoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(related_name='choices', to=orm['bartleby.Field'])),
            ('key', self.gf('django.db.models.fields.SlugField')(max_length=20)),
            ('verbose_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('order', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal('bartleby', ['FieldChoice'])

        # Adding model 'ResultRow'
        db.create_table('bartleby_resultrow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(related_name='result_rows', to=orm['bartleby.Form'])),
            ('submitted', self.gf('django.db.models.fields.DateTimeField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('cookie', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
        ))
        db.send_create_signal('bartleby', ['ResultRow'])

        # Adding model 'FieldValue'
        db.create_table('bartleby_fieldvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('field', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bartleby.Field'])),
            ('value', self.gf('philo.models.fields.JSONField')()),
            ('row', self.gf('django.db.models.fields.related.ForeignKey')(related_name='values', to=orm['bartleby.ResultRow'])),
        ))
        db.send_create_signal('bartleby', ['FieldValue'])

        # Adding unique constraint on 'FieldValue', fields ['field', 'row']
        db.create_unique('bartleby_fieldvalue', ['field_id', 'row_id'])

    def backwards(self, orm):
        
        # Removing unique constraint on 'FieldValue', fields ['field', 'row']
        db.delete_unique('bartleby_fieldvalue', ['field_id', 'row_id'])

        # Removing unique constraint on 'Field', fields ['key', 'form']
        db.delete_unique('bartleby_field', ['key', 'form_id'])

        # Deleting model 'Form'
        db.delete_table('bartleby_form')

        # Removing M2M table for field pages on 'Form'
        db.delete_table('bartleby_form_pages')

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
        'bartleby.field': {
            'Meta': {'ordering': "['order']", 'unique_together': "(('key', 'form'),)", 'object_name': 'Field'},
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': "orm['bartleby.Form']"}),
            'help_text': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'max_length': '100'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'multiple': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'bartleby.fieldchoice': {
            'Meta': {'ordering': "['order']", 'object_name': 'FieldChoice'},
            'field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'choices'", 'to': "orm['bartleby.Field']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.SlugField', [], {'max_length': '20'}),
            'order': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'bartleby.fieldvalue': {
            'Meta': {'ordering': "['field__order']", 'unique_together': "(('field', 'row'),)", 'object_name': 'FieldValue'},
            'field': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bartleby.Field']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'row': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'values'", 'to': "orm['bartleby.ResultRow']"}),
            'value': ('philo.models.fields.JSONField', [], {})
        },
        'bartleby.form': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Form'},
            'allow_changes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email_from': ('django.db.models.fields.CharField', [], {'default': "u'noreply@127.0.0.1:8000'", 'max_length': '200', 'blank': 'True'}),
            'email_groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'email_template': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['philo.Template']", 'null': 'True', 'blank': 'True'}),
            'email_users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_submissions': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'pages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['philo.Page']", 'symmetrical': 'False'}),
            'record': ('django.db.models.fields.CharField', [], {'default': "'u'", 'max_length': '1'}),
            'save_to_database': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'bartleby.resultrow': {
            'Meta': {'ordering': "['-submitted']", 'object_name': 'ResultRow'},
            'cookie': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'result_rows'", 'to': "orm['bartleby.Form']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'submitted': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
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
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['bartleby']
