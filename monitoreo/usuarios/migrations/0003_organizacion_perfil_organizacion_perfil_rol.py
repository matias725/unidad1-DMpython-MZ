# Generated manually for EcoEnergy roles

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_alter_perfil_avatar'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organizacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Organizaciones',
            },
        ),
        migrations.AddField(
            model_name='perfil',
            name='organizacion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='usuarios.organizacion'),
        ),
        migrations.AddField(
            model_name='perfil',
            name='rol',
            field=models.CharField(choices=[('cliente_admin', 'Cliente Admin'), ('cliente_electronico', 'Cliente Electrónico'), ('encargado_ecoenergy', 'Encargado EcoEnergy')], default='cliente_electronico', max_length=20),
        ),
    ]