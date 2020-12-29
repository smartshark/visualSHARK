# Generated by Django 2.2.13 on 2020-12-27 09:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('visualSHARK', '0018_auto_20201221_1923'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='technologylabel',
            name='times_used',
        ),
        migrations.AddField(
            model_name='technologylabel',
            name='created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='technologylabel',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='technologylabelcommit',
            name='technologies',
            field=models.ManyToManyField(blank=True, null=True, to='visualSHARK.TechnologyLabel'),
        ),
        migrations.AlterField(
            model_name='changetypelabel',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='technologylabel',
            name='ident',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='technologylabel',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='technologylabelcommit',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]