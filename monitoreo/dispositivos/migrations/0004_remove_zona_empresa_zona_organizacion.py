# Generated manually for EcoEnergy zones

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0003_organizacion_perfil_organizacion_perfil_rol'),
        ('dispositivos', '0003_alter_alerta_options_alter_medicion_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zona',
            name='empresa',
        ),
        migrations.AddField(
            model_name='zona',
            name='organizacion',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='usuarios.organizacion'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='zona',
            unique_together={('nombre', 'organizacion')},
        ),
        migrations.DeleteModel(
            name='Empresa',
        ),
    ]