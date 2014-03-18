from django.contrib import admin
from attendance.apps.home import models

admin.site.register(models.Pais)
admin.site.register(models.Departamento)
admin.site.register(models.Provincia)
admin.site.register(models.Distrito)
admin.site.register(models.Cargo)
admin.site.register(models.Empleado)
admin.site.register(models.Proyecto)
admin.site.register(models.Horario)
admin.site.register(models.HorarioPersonal)
admin.site.register(models.Asistencia)
