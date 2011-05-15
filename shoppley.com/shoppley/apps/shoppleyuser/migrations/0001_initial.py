# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Country'
        db.create_table('shoppleyuser_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('shoppleyuser', ['Country'])

        # Adding model 'Region'
        db.create_table('shoppleyuser_region', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shoppleyuser.Country'])),
        ))
        db.send_create_signal('shoppleyuser', ['Region'])

        # Adding model 'City'
        db.create_table('shoppleyuser_city', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shoppleyuser.Region'])),
        ))
        db.send_create_signal('shoppleyuser', ['City'])

        # Adding model 'ZipCode'
        db.create_table('shoppleyuser_zipcode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shoppleyuser.City'])),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('shoppleyuser', ['ZipCode'])

        # Adding model 'Category'
        db.create_table('shoppleyuser_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shoppleyuser.Category'])),
        ))
        db.send_create_signal('shoppleyuser', ['Category'])

        # Adding model 'ShoppleyUser'
        db.create_table('shoppleyuser_shoppleyuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('address_1', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('address_2', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shoppleyuser.ZipCode'])),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('balance', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('shoppleyuser', ['ShoppleyUser'])

        # Adding M2M table for field categories on 'ShoppleyUser'
        db.create_table('shoppleyuser_shoppleyuser_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('shoppleyuser', models.ForeignKey(orm['shoppleyuser.shoppleyuser'], null=False)),
            ('category', models.ForeignKey(orm['shoppleyuser.category'], null=False))
        ))
        db.create_unique('shoppleyuser_shoppleyuser_categories', ['shoppleyuser_id', 'category_id'])

        # Adding model 'Merchant'
        db.create_table('shoppleyuser_merchant', (
            ('shoppleyuser_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['shoppleyuser.ShoppleyUser'], unique=True, primary_key=True)),
            ('business_name', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('admin', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('shoppleyuser', ['Merchant'])

        # Adding model 'Customer'
        db.create_table('shoppleyuser_customer', (
            ('shoppleyuser_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['shoppleyuser.ShoppleyUser'], unique=True, primary_key=True)),
            ('frequency', self.gf('django.db.models.fields.IntegerField')(default=4)),
            ('weekdays_only', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('weekends_only', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('shoppleyuser', ['Customer'])

        # Adding M2M table for field merchant_likes on 'Customer'
        db.create_table('shoppleyuser_customer_merchant_likes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('customer', models.ForeignKey(orm['shoppleyuser.customer'], null=False)),
            ('merchant', models.ForeignKey(orm['shoppleyuser.merchant'], null=False))
        ))
        db.create_unique('shoppleyuser_customer_merchant_likes', ['customer_id', 'merchant_id'])

        # Adding M2M table for field merchant_dislikes on 'Customer'
        db.create_table('shoppleyuser_customer_merchant_dislikes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('customer', models.ForeignKey(orm['shoppleyuser.customer'], null=False)),
            ('merchant', models.ForeignKey(orm['shoppleyuser.merchant'], null=False))
        ))
        db.create_unique('shoppleyuser_customer_merchant_dislikes', ['customer_id', 'merchant_id'])

        # Adding model 'MerchantOfTheDay'
        db.create_table('shoppleyuser_merchantoftheday', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('merchant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shoppleyuser.Merchant'])),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('shoppleyuser', ['MerchantOfTheDay'])


    def backwards(self, orm):
        
        # Deleting model 'Country'
        db.delete_table('shoppleyuser_country')

        # Deleting model 'Region'
        db.delete_table('shoppleyuser_region')

        # Deleting model 'City'
        db.delete_table('shoppleyuser_city')

        # Deleting model 'ZipCode'
        db.delete_table('shoppleyuser_zipcode')

        # Deleting model 'Category'
        db.delete_table('shoppleyuser_category')

        # Deleting model 'ShoppleyUser'
        db.delete_table('shoppleyuser_shoppleyuser')

        # Removing M2M table for field categories on 'ShoppleyUser'
        db.delete_table('shoppleyuser_shoppleyuser_categories')

        # Deleting model 'Merchant'
        db.delete_table('shoppleyuser_merchant')

        # Deleting model 'Customer'
        db.delete_table('shoppleyuser_customer')

        # Removing M2M table for field merchant_likes on 'Customer'
        db.delete_table('shoppleyuser_customer_merchant_likes')

        # Removing M2M table for field merchant_dislikes on 'Customer'
        db.delete_table('shoppleyuser_customer_merchant_dislikes')

        # Deleting model 'MerchantOfTheDay'
        db.delete_table('shoppleyuser_merchantoftheday')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'shoppleyuser.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shoppleyuser.Category']"})
        },
        'shoppleyuser.city': {
            'Meta': {'object_name': 'City'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shoppleyuser.Region']"})
        },
        'shoppleyuser.country': {
            'Meta': {'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'shoppleyuser.customer': {
            'Meta': {'object_name': 'Customer', '_ormbases': ['shoppleyuser.ShoppleyUser']},
            'frequency': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'merchant_dislikes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'antifans'", 'to': "orm['shoppleyuser.Merchant']"}),
            'merchant_likes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'fans'", 'to': "orm['shoppleyuser.Merchant']"}),
            'shoppleyuser_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['shoppleyuser.ShoppleyUser']", 'unique': 'True', 'primary_key': 'True'}),
            'weekdays_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'weekends_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'shoppleyuser.merchant': {
            'Meta': {'object_name': 'Merchant', '_ormbases': ['shoppleyuser.ShoppleyUser']},
            'admin': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'business_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'shoppleyuser_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['shoppleyuser.ShoppleyUser']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'shoppleyuser.merchantoftheday': {
            'Meta': {'object_name': 'MerchantOfTheDay'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'merchant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shoppleyuser.Merchant']"})
        },
        'shoppleyuser.region': {
            'Meta': {'object_name': 'Region'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shoppleyuser.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'shoppleyuser.shoppleyuser': {
            'Meta': {'object_name': 'ShoppleyUser'},
            'address_1': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'address_2': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'balance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['shoppleyuser.Category']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'zipcode': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shoppleyuser.ZipCode']"})
        },
        'shoppleyuser.zipcode': {
            'Meta': {'object_name': 'ZipCode'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shoppleyuser.City']"}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['shoppleyuser']
