# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from django.db    import transaction
from decimal    import Decimal

registry_data = {
    "ARIN": "ftp://ftp.arin.net/pub/stats/arin/delegated-arin-latest",
    "RIPE": "ftp://ftp.ripe.net/ripe/stats/delegated-ripencc-latest",
    "AfriNIC": "ftp://ftp.afrinic.net/pub/stats/afrinic/delegated-afrinic-latest",
    "APNIC": "ftp://ftp.apnic.net/pub/stats/apnic/delegated-apnic-latest",
    "LACNIC": "ftp://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest",
}


@transaction.commit_manually
class Migration(DataMigration):

    def forwards(self, orm):
        all_rirs = {}
        for rir in ["ARIN", "RIPE", "AfriNIC", "APNIC", "LACNIC"]:
            try:
                all_rirs[rir] = orm.RIR.objects.get(name=rir)
            except:
                obj = orm.RIR.objects.create(
                    name=rir,
                    whois=registry_data[rir]
                )
                obj.save()
                all_rirs[rir] = orm.RIR.objects.get(name=rir)

        subnet_to_rir = {}
        for line in open("blacklist/migrations/data/subnet-to-rir.txt", "r").readlines():
            line = line.strip()
            t = line.split("|")
            subnet_to_rir[Decimal(t[0])] = all_rirs[t[1]]

        for subnet in orm.Subnet.objects.all().iterator():
            subnet.rir = subnet_to_rir[subnet.subnet]
            subnet.save()
        transaction.commit()

    def backwards(self, orm):
        raise RuntimeError("Cannot reverse this migration.")


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
        'blacklist.asnum': {
            'Meta': {'object_name': 'ASNum'},
            'asnum': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '16', 'db_index': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'num_history': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_listed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_subnets': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_whitelisted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'regdate': ('django.db.models.fields.DateTimeField', [], {}),
            'rir': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.RIR']"}),
            'whitelisted': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'blacklist.configstore': {
            'Meta': {'object_name': 'ConfigStore'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250', 'db_index': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'blacklist.country': {
            'Meta': {'ordering': "['code']", 'object_name': 'Country'},
            'additional': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '2', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'rir': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.RIR']"}),
            'whitelisted': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'blacklist.duration': {
            'Meta': {'object_name': 'Duration'},
            'duration': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'blacklist.historylisting': {
            'Meta': {'object_name': 'HistoryListing'},
            'duration': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.Duration']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.IP']"}),
            'reason': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.Reason']"}),
            'reporter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.Sensor']"}),
            'sensor_host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.Host']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'blacklist.host': {
            'Meta': {'object_name': 'Host'},
            'hostname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '512', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.IP']"}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'blacklist.ignore': {
            'Meta': {'object_name': 'Ignore'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignore': ('django.db.models.fields.TextField', [], {}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.Sensor']"})
        },
        'blacklist.ip': {
            'Meta': {'object_name': 'IP'},
            'af': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.DecimalField', [], {'max_digits': '39', 'decimal_places': '0', 'db_index': 'True'}),
            'last': ('django.db.models.fields.DecimalField', [], {'max_digits': '39', 'decimal_places': '0', 'db_index': 'True'}),
            'listed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mask': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'num_listed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'subnet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.Subnet']", 'null': 'True', 'blank': 'True'}),
            'whitelisted': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'blacklist.key': {
            'Meta': {'object_name': 'Key'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250', 'db_index': 'True'})
        },
        'blacklist.listing': {
            'Meta': {'object_name': 'Listing'},
            'duration': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.Duration']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.IP']"}),
            'reason': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.Reason']"}),
            'reporter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.Sensor']"}),
            'sensor_host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.Host']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        'blacklist.peering': {
            'Meta': {'object_name': 'Peering'},
            'asnum': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.ASNum']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.Key']"}),
            'peer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.Host']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'blacklist.reason': {
            'Meta': {'object_name': 'Reason'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'db_index': 'True'}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.Sensor']"})
        },
        'blacklist.rir': {
            'Meta': {'object_name': 'RIR'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32', 'db_index': 'True'}),
            'num_history': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_listed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_providers': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_subnets': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_whitelisted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'whitelisted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'whois': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'blacklist.role': {
            'Meta': {'object_name': 'Role'},
            'admin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250', 'db_index': 'True'}),
            'rpc': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'view': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'blacklist.rule': {
            'Meta': {'object_name': 'Rule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pos_ip': ('django.db.models.fields.IntegerField', [], {}),
            'pos_reason': ('django.db.models.fields.IntegerField', [], {}),
            'rule': ('django.db.models.fields.TextField', [], {}),
            'sensor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.Sensor']"})
        },
        'blacklist.sensor': {
            'Meta': {'object_name': 'Sensor'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256', 'db_index': 'True'})
        },
        'blacklist.subnet': {
            'Meta': {'object_name': 'Subnet'},
            'af': ('django.db.models.fields.IntegerField', [], {}),
            'asnum': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.ASNum']", 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last': ('django.db.models.fields.DecimalField', [], {'max_digits': '39', 'decimal_places': '0', 'db_index': 'True'}),
            'listed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mask': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'num_listed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num_whitelisted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'regdate': ('django.db.models.fields.DateTimeField', [], {}),
            'rir': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.RIR']", 'null': 'True'}),
            'subnet': ('django.db.models.fields.DecimalField', [], {'max_digits': '39', 'decimal_places': '0', 'db_index': 'True'}),
            'whitelisted': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'blacklist.whitelisting': {
            'Meta': {'object_name': 'WhiteListing'},
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['blacklist.IP']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['blacklist']
