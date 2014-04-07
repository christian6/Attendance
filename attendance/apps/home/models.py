#-*- Encoding: utf-8 -*-
from django.db import models
import datetime

# Create your models here.
class Pais(models.Model):
	pais_id = models.CharField(primary_key=True,max_length=3)
	paisnom = models.CharField(max_length=56)
	flag = models.BooleanField(default=True)
	def __unicode__(self):
		return self.paisnom

class Departamento(models.Model):
	departamento_id = models.CharField(primary_key=True, max_length=2)
	pais = models.ForeignKey(Pais, to_field='pais_id')
	depnom = models.CharField(max_length=56)
	flag = models.BooleanField(default=True)

	def __unicode__(self):
		return self.depnom

class Provincia(models.Model):
	provincia_id = models.CharField(primary_key=True, max_length=3)
	departamento = models.ForeignKey(Departamento, to_field='departamento_id')
	pais = models.ForeignKey(Pais, to_field='pais_id')
	pronom = models.CharField(max_length=56)
	flag = models.BooleanField(default=True)

	def __unicode__(self):
		return self.pronom

class Distrito(models.Model):
	distrido_id = models.CharField(primary_key=True, max_length=2)
	provincia = models.ForeignKey(Provincia, to_field='provincia_id')
	departamento = models.ForeignKey(Departamento, to_field='departamento_id')
	pais = models.ForeignKey(Pais, to_field='pais_id')
	distnom = models.CharField(max_length=56)
	flag = models.BooleanField(default=True)

	def __unicode__(self):
		return self.distnom

class Cargo(models.Model):
	cargo_id = models.CharField(primary_key=True, max_length=2)
	carnom = models.CharField(max_length=60)
	flag = models.BooleanField(default=True)

	def __unicode__(self):
		return self.carnom

class Empleado(models.Model):
	empdni_id = models.CharField(primary_key=True, max_length=8)
	empnom = models.CharField(max_length=120)
	empape = models.CharField(max_length=120)
	empdir = models.CharField(max_length=180)
	distrido = models.ForeignKey(Distrito, to_field='distrido_id')
	provincia = models.ForeignKey(Provincia, to_field='provincia_id')
	departamento = models.ForeignKey(Departamento, to_field='departamento_id')
	pais = models.ForeignKey(Pais, to_field='pais_id')
	cargo = models.ForeignKey(Cargo, to_field='cargo_id')
	alta = models.DateField(auto_now=False,auto_now_add=False)
	baja = models.DateField(auto_now=True,null=True)
	base = models.FloatField(null=True,blank=True,default=0)
	flag = models.BooleanField(default=True)

	def __unicode__(self):
		return "%s, %s"%(self.empnom,self.empape)

class Proyecto(models.Model):
	proyecto_id = models.CharField(primary_key=True, max_length=7)
	pronom = models.CharField(max_length=160)
	flag = models.BooleanField(default=True)

	def __unicode__(self):
		return self.pronom

class Horario(models.Model):
	horario_id = models.CharField(primary_key=True, max_length=5)
	proyecto = models.ForeignKey(Proyecto, to_field='proyecto_id',null=True,blank=True)
	tipo = models.CharField(max_length=7,blank=True,null=True)
	entrada = models.TimeField(null=True)
	salida = models.TimeField(null=True)
	extraini = models.TimeField(null=True)
	satini = models.TimeField(null=True)
	satfin = models.TimeField(null=True)
	#hextra = models.TimeField(null=True)
	priceex = models.FloatField(default=0,null=True,blank=True)
	pricefes = models.FloatField(default=0,null=True,blank=True)
	flag = models.BooleanField(default=True)

	def __unicode__(self):
		return "%s %s"%(self.horario_id, self.tipo)

class HorarioPersonal(models.Model):
	horario = models.ForeignKey(Horario, to_field='horario_id')
	empdni = models.ForeignKey(Empleado, to_field='empdni_id')

	def __unicode__(self):
		return "%s - %s, %s"%(self.horario.tipo,self.empdni.empnom,self.empdni.empape)

class Asistencia(models.Model):
	empdni = models.ForeignKey(Empleado, to_field='empdni_id', null=False)
	#horario = models.ForeignKey(Horario, to_field='horario_id')
	fecha = models.DateField(auto_now=True)
	entrada = models.TimeField()
	salida = models.TimeField(null=True)
	extras = models.TimeField(null=True)

	def __unicode__(self):
		#return self.entrada.strftime("%H:%M:%S")
		return "%s | %s | %s | %s"%(self.empdni.empnom+', '+self.empdni.empape, self.fecha.strftime('%d/%m/%Y'), self.entrada.strftime("%H:%M:%S"), self.salida)