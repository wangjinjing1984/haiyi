# Generated by Django 2.1.3 on 2018-12-22 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('haiyi', '0003_auto_20181222_0728'),
    ]

    operations = [
        migrations.AddField(
            model_name='productsfile',
            name='products_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='productsfile',
            name='file',
            field=models.FileField(upload_to='upload/'),
        ),
        migrations.AlterField(
            model_name='usersfile',
            name='file',
            field=models.FileField(upload_to='upload/'),
        ),
    ]
