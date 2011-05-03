# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Form.email_template'
        db.delete_column('bartleby_form', 'email_template_id')

        # Deleting field 'Form.allow_changes'
        db.delete_column('bartleby_form', 'allow_changes')

        # Deleting field 'Form.save_to_database'
        db.delete_column('bartleby_form', 'save_to_database')

        # Deleting field 'Form.login_required'
        db.delete_column('bartleby_form', 'login_required')

        # Deleting field 'Form.record'
        db.delete_column('bartleby_form', 'record')

        # Deleting field 'Form.max_submissions'
        db.delete_column('bartleby_form', 'max_submissions')

        # Deleting field 'Form.email_from'
        db.delete_column('bartleby_form', 'email_from')

        # Removing M2M table for field email_users on 'Form'
        db.delete_table('bartleby_form_email_users')

        # Removing M2M table for field email_groups on 'Form'
        db.delete_table('bartleby_form_email_groups')

        # Removing M2M table for field pages on 'Form'
        db.delete_table('bartleby_form_pages')

        # Adding field 'FormView.results_email_page'
        db.add_column('bartleby_formview', 'results_email_page', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='form_results_email_related', null=True, to=orm['philo.Page']), keep_default=False)

        # Adding field 'FormView.results_email_sender'
        db.add_column('bartleby_formview', 'results_email_sender', self.gf('django.db.models.fields.CharField')(default=u'noreply@example.com', max_length=200, blank=True), keep_default=False)

        # Adding field 'FormView.save_to_database'
        db.add_column('bartleby_formview', 'save_to_database', self.gf('django.db.models.fields.BooleanField')(default=True), keep_default=False)

        # Adding field 'FormView.record'
        db.add_column('bartleby_formview', 'record', self.gf('django.db.models.fields.CharField')(default='u', max_length=1), keep_default=False)

        # Adding field 'FormView.login_required'
        db.add_column('bartleby_formview', 'login_required', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'FormView.allow_changes'
        db.add_column('bartleby_formview', 'allow_changes', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'FormView.max_submissions'
        db.add_column('bartleby_formview', 'max_submissions', self.gf('django.db.models.fields.SmallIntegerField')(default=1), keep_default=False)

        # Adding M2M table for field email_users on 'FormView'
        db.create_table('bartleby_formview_email_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('formview', models.ForeignKey(orm['bartleby.formview'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('bartleby_formview_email_users', ['formview_id', 'user_id'])

        # Adding M2M table for field email_groups on 'FormView'
        db.create_table('bartleby_formview_email_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('formview', models.ForeignKey(orm['bartleby.formview'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('bartleby_formview_email_groups', ['formview_id', 'group_id'])

    def backwards(self, orm):
        
        # Adding field 'Form.email_template'
        db.add_column('bartleby_form', 'email_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['philo.Template'], null=True, blank=True), keep_default=False)

        # Adding field 'Form.allow_changes'
        db.add_column('bartleby_form', 'allow_changes', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Form.save_to_database'
        db.add_column('bartleby_form', 'save_to_database', self.gf('django.db.models.fields.BooleanField')(default=True), keep_default=False)

        # Adding field 'Form.login_required'
        db.add_column('bartleby_form', 'login_required', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Form.record'
        db.add_column('bartleby_form', 'record', self.gf('django.db.models.fields.CharField')(default='u', max_length=1), keep_default=False)

        # Adding field 'Form.max_submissions'
        db.add_column('bartleby_form', 'max_submissions', self.gf('django.db.models.fields.SmallIntegerField')(default=1), keep_default=False)

        # Adding field 'Form.email_from'
        db.add_column('bartleby_form', 'email_from', self.gf('django.db.models.fields.CharField')(default=u'noreply@127.0.0.1:8000', max_length=200, blank=True), keep_default=False)

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

        # Adding M2M table for field pages on 'Form'
        db.create_table('bartleby_form_pages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('form', models.ForeignKey(orm['bartleby.form'], null=False)),
            ('page', models.ForeignKey(orm['philo.page'], null=False))
        ))
        db.create_unique('bartleby_form_pages', ['form_id', 'page_id'])

        # Deleting field 'FormView.results_email_page'
        db.delete_column('bartleby_formview', 'results_email_page_id')

        # Deleting field 'FormView.results_email_sender'
        db.delete_column('bartleby_formview', 'results_email_sender')

        # Deleting field 'FormView.save_to_database'
        db.delete_column('bartleby_formview', 'save_to_database')

        # Deleting field 'FormView.record'
        db.delete_column('bartleby_formview', 'record')

        # Deleting field 'FormView.login_required'
        db.delete_column('bartleby_formview', 'login_required')

        # Deleting field 'FormView.allow_changes'
        db.delete_column('bartleby_formview', 'allow_changes')

        # Deleting field 'FormView.max_submissions'
        db.delete_column('bartleby_formview', 'max_submissions')

        # Removing M2M table for field email_users on 'FormView'
        db.delete_table('bartleby_formview_email_users')

        # Removing M2M table for field email_groups on 'FormView'
        db.delete_table('bartleby_formview_email_groups')

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
            'help_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '150'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'bartleby.formstep': {
            'Meta': {'ordering': "('order',)", 'unique_together': "(('form', 'multiview'),)", 'object_name': 'FormStep'},
            'form': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bartleby.Form']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'multiview': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'steps'", 'to': "orm['bartleby.FormView']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'bartleby.formview': {
            'Meta': {'object_name': 'FormView'},
            'allow_changes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email_groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'email_users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'form_complete_page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'form_complete_related'", 'to': "orm['philo.Page']"}),
            'form_display_page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'form_display_related'", 'to': "orm['philo.Page']"}),
            'forms': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['bartleby.Form']", 'through': "orm['bartleby.FormStep']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'login_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_submissions': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'record': ('django.db.models.fields.CharField', [], {'default': "'u'", 'max_length': '1'}),
            'results_email_page': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'form_results_email_related'", 'null': 'True', 'to': "orm['philo.Page']"}),
            'results_email_sender': ('django.db.models.fields.CharField', [], {'default': "u'noreply@example.com'", 'max_length': '200', 'blank': 'True'}),
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
