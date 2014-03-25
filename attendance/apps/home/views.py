#-*- encoding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, TemplateDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseNotFound
from django.contrib import messages
from attendance.apps.home import models
from django.db.models import Count

def view_home(request):
	if request.method == 'GET':
		return render_to_response('home/home.html',context_instance=RequestContext(request))

def view_register_now(request):
	if request.method == 'GET':
		return render_to_response('home/register.html',context_instance=RequestContext(request))

def view_getter_month(request):
	if request.method == 'GET':
		from django.utils import simplejson
		import datetime
		months = {}
		try:
			m = models.Asistencia.objects.dates('fecha','month').filter(fecha__year=request.GET['anio'])
			m_name = { 1:u'ENERO',2:u'FEBRERO',3:u'MARZO',4:u'ABRIL',5:u'MAYO',6:u'JUNIO',7:u'JULIO',8:u'AGOSTO',9:u'SETIEMBRE',10:u'OCTUBRE',11:u'NOVIEMBRE',12:u'DICIEMBRE', }
			for x in m:
				print x
				print 'aqui'
				print x.strftime('%m')
				months[int(x.strftime('%m'))] = m_name[int(x.strftime('%m'))]

			months['status'] = 'success'
		except Exception, e:
			raise e
			months['status'] = 'fail'
		data = simplejson.dumps(months)
	return HttpResponse(data, mimetype='application/json')

def view_report(request):
	if request.method == 'GET':
		import datetime
		emp = models.Empleado.objects.filter(flag=True)
		anio = models.Asistencia.objects.dates('fecha','year')
		a = []
		for x in anio:
			a.append(x.strftime('%Y'))
		ctx = { 'emp' : emp, 'anios': a }
		return render_to_response('home/generateReport.html',ctx,context_instance=RequestContext(request))

def view_show_details_employee(request):
	if request.method == 'POST':
		ctx = {}
		# check formato de dni
		if len(request.POST['dni']) == 8:
			#check exists dni
			countd = models.Empleado.objects.filter(empdni_id=request.POST['dni']).count()
			if countd == 1:
				from datetime import date
				import datetime, time
				first = models.Asistencia.objects.filter(empdni_id=request.POST['dni'], fecha=date.today(), entrada__isnull=False,salida__isnull=False).count()
				if first == 0:
					counta = models.Asistencia.objects.filter(empdni_id=request.POST['dni'], fecha=date.today()).count()

					hora = datetime.datetime.strptime( time.strftime('%H:%M:%S', time.localtime()) ,'%H:%M:%S').time()
					# check si asistio hoy
					if counta == 1:
						#Registrar salida de personal
						aobj = models.Asistencia.objects.get(empdni_id=request.POST['dni'],fecha=date.today())
						##print 'id de asistencias '+aobj[0].id
						aobj.id = aobj.id
						#aobj.fecha = date.today()
						#aobj.entrada=datetime.time(int(datetime.datetime.now().strftime('%H')),int(datetime.datetime.today().strftime('%M')),int(datetime.datetime.today().strftime('%S')))
						aobj.salida = hora
						#print hora
						# Consultar si empleado cuenta con asignacion de horas extras
						hx = models.HorarioPersonal.objects.filter(empdni_id=request.POST['dni'],horario__flag=True,empdni__flag=True,empdni__empdni_id=request.POST['dni'])[:1]
						# preguntar si existe horario
						if hx == []:
							# obteniendo horario por defecto
							hx = models.Horario.objects.filter(flag=True,tipo='CENTRAL',proyecto_id__isnull=True)[:1]
							if date.today().strftime('%A') == 'Saturday':
								hs = hx[0].satfin
								he = hx[0].extraini
							else:
								hs = hx[0].salida
								he = hx[0].extraini
						else:
							if date.today().strftime('%A') == 'Saturday':
								hs = hx[0].satfin
								he = hx[0].extraini
							else:
								he = hx[0].horario.extraini
								hs = hx[0].horario.salida
						#formato de hora
						format = '%H:%M:%S'
						# convirtiendo type time to datetime
						ts=datetime.datetime.strptime( hs.strftime(format), format)
						tx=datetime.datetime.strptime( he.strftime(format), format)
						#print ts
						#print tx
						# suamando la hora de salida mas hora extra para saber si se genero horas extras
						tl = ts + datetime.timedelta(hours=tx.hour,minutes=tx.minute,seconds=tx.second)
						# convertiendo type datetime to time tiempo limite h. salida + min extra
						tl = datetime.datetime.strptime( tl.strftime(format), format ).time()
						#print tl
						# preguntar si se ha exedido el tiempo limite para la generacion de horas extras ||| las dos son datetime.time
						outend = ''
						if hora > tl: #datetime.datetime.strptime(hs.strftime(format), format) > tl:
							# obtenemos la horas y minutos extras
							# pasando la variables tiempo limite (tl) y hora actual (hora) a types datetimes
							tl = datetime.datetime.strptime( tl.strftime(format), format );
							hora = datetime.datetime.strptime( hora.strftime(format), format );
							# obteniendo horas extras
							outend = hora - datetime.timedelta( hours=tl.hour, minutes=tl.minute, seconds=tl.second )
							outend = datetime.datetime.strptime( outend.strftime(format), format ).time()	
						else:
							# se guarda la hora en salida y como extra 00:00:00
							outend = datetime.time(0,0,0)

						#print outend
						# agregando horas extras
						aobj.extras = outend
						# guardando, actualizando
						aobj.save();
					elif counta == 0:
						# registrar entrada de personal
						aobj = models.Asistencia()
						aobj.empdni_id = request.POST['dni']
						aobj.fecha = date.today()
						#aobj.entrada=datetime.time(int(datetime.datetime.now().strftime('%H')),int(datetime.datetime.today().strftime('%M')),int(datetime.datetime.today().strftime('%S')))
						aobj.entrada = datetime.datetime.strptime( time.strftime('%H:%M:%S', time.localtime()) ,'%H:%M:%S').time()
						aobj.save();

				# ahora solo obtenemos los datos de empleado para mostrarlos
				eobj = models.Empleado.objects.filter(pk=request.POST['dni'])
				hora = datetime.datetime.strptime( time.strftime('%H:%M:%S', time.localtime()) ,'%H:%M:%S').time()
				ctx = { 'status': 'success', 'dni': request.POST['dni'], 'emp' : eobj, 'hour' : hora }
			else:
				ctx = {'status' : 'fail', 'msg':'El DNI ingresado no Existe.'}
		else:
			ctx = {'status' : 'fail', 'msg':'El DNI ingresado no contiene el formato.'}
		return render_to_response('home/attendance.html',ctx,context_instance=RequestContext(request))
	else:
		messages.error(request, 'Esta pagina solo acepta peticiones Encriptadas!')
		raise Http404('Method no proccess')

def view_test_pdf(request):
	from reportlab.pdfgen import canvas
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'filename="attendance.pdf"'
	p = canvas.Canvas(response)
	p.drawString(100,100,"Hello world.")
	p.showPage()
	p.save()
	return response

def rpt_single_hours(request):
	if request.method == 'GET':
		try:
			from reportlab.pdfgen import canvas
			from reportlab.lib.units import cm, mm, inch
			from reportlab.lib.styles import getSampleStyleSheet
			from reportlab.platypus import Paragraph, SimpleDocTemplate, Table
			from reportlab.lib.pagesizes import landscape, LETTER
			from reportlab.lib import colors
			from django.db.models import Count
			import datetime

			emp = []

			if request.GET['type'] == 'n':
				# verificar que las fecha ingresada
				years = models.Asistencia.objects.filter(empdni=request.GET['dni'],fecha__year=request.GET['anio']).count()
				if years > 0:
					# verificar mes que tenga registro si falla el reporte
					months = models.Asistencia.objects.filter(empdni=request.GET['dni'],fecha__year=request.GET['anio'],fecha__month="%02d"%int(request.GET['mes'])).count()
					if months > 0:
						# vefiricar que el periodo contenga datos para realizar el reporte
						periodo = 0
						if request.GET['periodo'] == '1':
							# periodo value 1 primera, los primeros quince dias
							anio = int(request.GET['anio'])
							mes = int(request.GET['mes'])
							desde = datetime.date(anio,mes,1)
							hasta = datetime.date(anio,mes,15)
							periodo = models.Asistencia.objects.filter(empdni=request.GET['dni'],fecha__range=(desde,hasta)).count()
							if periodo > 0:
								emp = models.Asistencia.objects.filter(empdni=request.GET['dni'],fecha__range=(desde,hasta))
						elif request.GET['periodo'] == '2':
							import calendar
							de = datetime.date(int(request.GET['anio']),int(request.GET['mes']),16)
							hasta = datetime.date(int(request.GET['anio']),int(request.GET['mes']),calendar.monthrange(int(request.GET['anio']),int(request.GET['mes']) )[1] )
							periodo = models.Asistencia.objects.filter(empdni=request.GET['dni'],fecha__range=(de,hasta)).count()
							if periodo > 0:
								emp = models.Asistencia.objects.filter(empdni=request.GET['dni'],fecha__range=(de,hasta))
						else: #request.GET['periodo'] == '3':
							import calendar
							de = datetime.date(int(request.GET['anio']),int(request.GET['mes']),1)
							hasta = datetime.date(int(request.GET['anio']),int(request.GET['mes']),calendar.monthrange(int(request.GET['anio']),int(request.GET['mes']) )[1] )
							periodo = models.Asistencia.objects.filter(empdni=request.GET['dni'],fecha__range=(de,hasta)).count()
							if periodo > 0:
								emp = models.Asistencia.objects.filter(empdni=request.GET['dni'],fecha__range=(de,hasta))
					else:
						# redireccionar a otra pagina y mostrar mensaje
						messages.error(request, 'No se han encontrado datos para este mes!')
						raise Http404('Method no proccess')
				else:
					# redireccionar a otra pagina para mostrar mensaje
					messages.error(request, 'No se han encontrado datos para este Año!')
					raise Http404('Method no proccess')
			elif request.GET['type'] == 'a':
				print 'dentro de advance'
				desde = datetime.date( int(request.GET['ayeari']),int(request.GET['amonthi']),int(request.GET['adayi']) )
				hasta = datetime.date( int(request.GET['ayearf']),int(request.GET['amonthf']),int(request.GET['adayf']) )
				exists = models.Asistencia.objects.filter(empdni=request.GET['dni'],fecha__range=(desde,hasta)).count()
				if exists > 0:
					emp = models.Asistencia.objects.filter(empdni=request.GET['dni'],fecha__range=(desde,hasta))

			#emp = models.Asistencia.objects.all()
			# redireccionamos si emp esta vacio
			if emp == []:
				messages.error(request, 'No se ha encontrado datos para generar el reporte.')
				raise Http404('Method Proccess Fail')
			response = HttpResponse(content_type='application/pdf')
			response['Content-Disposition'] = 'filename="rpt_total.pdf"'
			days = {'Sunday':u'Domingo','Monday':u'Lunes','Tuesday':u'Martes','Wednesday':u'Miercoles','Thursday':u'Jueves','Friday':u'Viernes','Saturday':u'Sabado'}
			elements = []
			tbl = [
				['Item','Fecha','Turno','Entrada','Salida','Horas T','T. Desc','Almuerzo','Extra','Total','Status']
			]
			format = '%H:%M:%S'
			
			hf = 0
			mf = 0
			sf = 0
			hdf = 0
			mdf = 0
			sdf = 0
			hxf = 0
			mxf = 0
			sxf = 0
			i = 1
			th = datetime.datetime(1900,1,1,0,0,0)
			nombre = ''
			for x in emp:
				# statsus
				sts = ''
				almuerzo = 0
				nombre = x.empdni.empnom+', '+x.empdni.empape
				# obteniendo dia de la semana
				day = x.fecha.strftime('%A')
				# convertiendo times a datetimes
				he = datetime.datetime.strptime( x.entrada.strftime(format), format )
				# obteniendo horas trabajados del dia
				hs = datetime.datetime(1900,1,1,0,0)
				h = models.HorarioPersonal.objects.filter(empdni_id=request.GET['dni'],horario__flag=True,empdni__flag=True,empdni__empdni_id=request.GET['dni'])[:1]
				# vamos a obtener descuento de tardanza
				#obtener hora de ingreso tambien verificar la hora de entrada de sabados
				entrada  = datetime.time(0,0,0)
				if days[day] == 'Sabado':
					entrada = h[0].horario.satini
				else:
					entrada = h[0].horario.entrada

				entrada = datetime.datetime.strptime( entrada.strftime(format), format )
				tolerancia = datetime.datetime(1900,1,1,0,10,0) + datetime.timedelta(hours=entrada.hour,minutes=entrada.minute,seconds=entrada.second)
				des = datetime.datetime(1900,1,1,0,0,0)
				dt = datetime.datetime(1900,1,1,0,0,0)
				thextra = datetime.datetime(1900,1,1,0,0)
				# generando descuaneto por tardanza
				if he > tolerancia:
					# generamos descuento
					des = he - datetime.timedelta(hours=tolerancia.hour,minutes=tolerancia.minute,seconds=tolerancia.second)
					dt = des #datetime.timedelta(hours=des.hour,minutes=des.minute,seconds=des.second)
				if x.entrada < entrada.time():
					he = entrada
				## ver la hora de la salida si es de central o de obra para ver si tiene horas extras
				#validar que h no este vacio
				# variable de hsalida de horario
				hsalida = datetime.datetime(1900,1,1,0,0)
				dsalida = datetime.datetime(1900,1,1,0,0)
				hextras = datetime.datetime(1900,1,1,0,0)
				if h != []:
					# validando que el horario del personal es de la central
					if h[0].horario.tipo == 'CENTRAL':
						# verificar el dia de la semana
						if days[day] == 'Sabado':
							print 'dentro de Sabado'
							# verificando que el horario de salida es menor o igual que al del horario Central no se cuenta horas extras
							if x.salida == None:
								hs = h[0].horario.satfin
								hs = datetime.datetime.strptime( hs.strftime(format), format )
								almuerzo = 0
								sts = 'Default'
							if x.salida < h[0].horario.satfin:
								tmphs = datetime.datetime.strptime( x.salida.strftime(format), format )
								tmphc = datetime.datetime.strptime( h[0].horario.satfin.strftime(format), format )
								dsalida = tmphc - datetime.timedelta(hours=tmphs.hour,minutes=tmphs.minute,seconds=tmphs.second)
								dt += datetime.timedelta(hours=dsalida.hour,minutes=dsalida.minute,seconds=dsalida.second)
								hs = datetime.datetime.strptime(tmphs.strftime(format), format)
								sts = 'Incompletas'
							else:
								hsalida = h[0].horario.satfin
								hs = datetime.datetime.strptime(hsalida.strftime(format), format)
								almuerzo = 0
								sts = 'Completas'
						else:
							# verificando que el horario de salida es menor o igual que al del horario Central no se cuenta horas extras
							if x.salida == None:
								hs = h[0].horario.salida
								hs = datetime.datetime.strptime( hs.strftime(format), format )
								almuerzo = 1
								sts = 'Default'
							elif x.salida < h[0].horario.salida:
								tmphs = datetime.datetime.strptime( x.salida.strftime(format), format )
								tmphc = datetime.datetime.strptime( h[0].horario.salida.strftime(format), format )
								dsalida = tmphc - datetime.timedelta(hours=tmphs.hour,minutes=tmphs.minute,seconds=tmphs.second)
								dt += datetime.timedelta(hours=dsalida.hour,minutes=dsalida.minute,seconds=dsalida.second)
								hs = datetime.datetime.strptime(tmphs.strftime(format), format)
								if hs.time() > datetime.time(14,0,0):
									almuerzo=0 # esto tiene que valer 1
								#print almuerzo
								sts = 'Incompletas'
							else:
								hsalida = h[0].horario.salida
								hs = datetime.datetime.strptime(hsalida.strftime(format), format)
								almuerzo = 1
								sts = 'Completas'
					else:
						#Preguntar si el dia es sabado
						if days[day] == 'Sabado':
							# caso en que el tipo de horario no es de la central y/o casos especiales
							if x.salida == None:
								hs = h[0].horario.satfin
								hs = datetime.datetime.strptime( hs.strftime(format), format )
								almuerzo = 1
								sts = 'Default'
							elif x.salida < h[0].horario.salida:
								tmphs = datetime.datetime.strptime( x.salida.strftime(format), format )
								tmphc = datetime.datetime.strptime( h[0].horario.satfin.strftime(format), format )
								dsalida = tmphc - datetime.timedelta(hours=tmphs.hour,minutes=tmphs.minute,seconds=tmphs.second)
								dt += datetime.timedelta(hours=dsalida.hour,minutes=dsalida.minute,seconds=dsalida.second)
								hs = datetime.datetime.strptime(tmphs.strftime(format), format)
								if hs.time() > datetime.time(14,0,0):
									almuerzo = 1
								sts = 'Incompletas'
							elif x.salida >= h[0].horario.satfin:
								#preguntamos si tiene horas extras para ser generadas
								iniex = datetime.datetime(1900,1,1,0,0)
								if h[0].horario.extraini > datetime.time(0,0,0):
									# calculo de horas extras
									tmps = datetime.datetime.strptime(h[0].horario.satfin.strftime(format), format)
									tmpe = datetime.datetime.strptime( h[0].horario.extraini.strftime(format), format )
									iniex = tmps + datetime.timedelta(hours=tmpe.hour,minutes=tmpe.minute,seconds=tmpe.second)
									almuerzo = 1
								if x.salida > iniex.time():
									# Horas extras
									hs = datetime.datetime.strptime( x.satfin.strftime(format), format )
									hextras = hs - datetime.timedelta(hours=iniex.hour,minutes=iniex.minute,seconds=iniex.second)
									thextra += datetime.timedelta(hours=hextras.hour,minutes=hextras.minute,seconds=hextras.second)
									almuerzo = 1
									sts = 'H. Extras'
								else:
									hs = datetime.datetime.strptime(h[0].horario.satfin.strftime(format), format)
									almuerzo = 1
									sts = 'Completas'
						else:
							# caso en que el tipo de horario no es de la central y/o casos especiales
							if x.salida == None:
								hs = h[0].horario.salida
								hs = datetime.datetime.strptime( hs.strftime(format), format )
								almuerzo = 1
								sts = 'Default'
							elif x.salida < h[0].horario.salida:
								tmphs = datetime.datetime.strptime( x.salida.strftime(format), format )
								tmphc = datetime.datetime.strptime( h[0].horario.salida.strftime(format), format )
								dsalida = tmphc - datetime.timedelta(hours=tmphs.hour,minutes=tmphs.minute,seconds=tmphs.second)
								dt += datetime.timedelta(hours=dsalida.hour,minutes=dsalida.minute,seconds=dsalida.second)
								hs = datetime.datetime.strptime(tmphs.strftime(format), format)
								if hs.time() > datetime.time(14,0,0):
									almuerzo = 1
								sts = 'Incompletas'
							elif x.salida >= h[0].horario.salida:
								#preguntamos si tiene horas extras para ser generadas
								iniex = datetime.datetime(1900,1,1,0,0)
								if h[0].horario.extraini > datetime.time(0,0,0):
									# calculo de horas extras
									tmps = datetime.datetime.strptime(h[0].horario.salida.strftime(format), format)
									tmpe = datetime.datetime.strptime( h[0].horario.extraini.strftime(format), format )
									iniex = tmps + datetime.timedelta(hours=tmpe.hour,minutes=tmpe.minute,seconds=tmpe.second)
									almuerzo = 1
								if x.salida > iniex.time():
									# Horas extras
									hs = datetime.datetime.strptime( x.salida.strftime(format), format )
									hextras = hs - datetime.timedelta(hours=iniex.hour,minutes=iniex.minute,seconds=iniex.second)
									thextra += datetime.timedelta(hours=hextras.hour,minutes=hextras.minute,seconds=hextras.second)
									almuerzo = 1
									sts = 'H. Extras'
								else:
									hs = datetime.datetime.strptime(h[0].horario.salida.strftime(format), format)
									almuerzo = 1
									sts = 'Completas'
				else:
					if days[day] == 'Sabado':
						h = models.Horario.objects.filter(flag=True,tipo='CENTRAL',proyecto_id__isnull=True)[:1]
						hs = h[0].satfin
						almuerzo = 1
						sts = 'DEFAULT'
					else:
						h = models.Horario.objects.filter(flag=True,tipo='CENTRAL',proyecto_id__isnull=True)[:1]
						hs = h[0].salida
						almuerzo = 1
						sts = 'DEFAULT'
				#Este caso es solo si la hora de salida no se ha registrato
				#block salida sin data
				"""
				if x.salida != None:
					hs = datetime.datetime.strptime( x.salida.strftime(format), format )
					sts = 'Total Horas'
				else:
					#hs = datetime.datetime(1900,1,1,17,30,0)
					sts = 'Hora Default'
					if h == []:
						h = models.Horario.objects.filter(flag=True,tipo='CENTRAL',proyecto_id__isnull=True)[:1]
						hs = h[0].salida
					else:	
						hs = h[0].horario.salida
					hs = datetime.datetime.strptime( hs.strftime(format), format )
				"""
				# endblock salida sin data

				hr = hs - datetime.timedelta(hours=he.hour,minutes=he.minute,seconds=he.second)
				th = th + datetime.timedelta(hours=hr.hour,minutes=hr.minute,seconds=hr.second)
				subt = hr - datetime.timedelta(hours=almuerzo,minutes=0)
				hf += hr.hour
				hf -= almuerzo
				mf += hr.minute
				sf += hr.second
				hdf += dt.hour
				mdf += dt.minute
				sdf += dt.second
				hxf += thextra.hour
				mxf += thextra.minute
				sxf += thextra.second
				#print dt
				tbl.append([i,x.fecha,days[day],he.strftime(format),hs.strftime(format),hr.strftime(format),dt.strftime(format),datetime.time(almuerzo,0).strftime(format),hextras.strftime(format),subt.strftime(format),sts])
				i+=1

			rht = returnsHours(hf,mf,sf)
			rdt = returnsHours(hdf,mdf,sdf)
			rxt = returnsHours(hxf,mxf,sxf)
			#print rht
			tbl.append(['','Horas Totales : ',str(rht[0])+':'+str(rht[1])+':'+str(rht[2]),'Descuento T.',str(rdt[0])+':'+str(rdt[1])+':'+str(rdt[2]),'T. H. Extras',str(rxt[0])+':'+str(rxt[1])+':'+str(rxt[2]) ])
			t=Table(tbl, style=[
	                    #('BOX',(0,0),(-1,-1),2,colors.black),
	                    ('GRID',(0,0),(-1,-1),0.5,colors.black),
	                    ('BACKGROUND',(0,0),(-1,0),colors.limegreen),
	                    ('BACKGROUND',(1,1),(-1,-1),colors.beige),
	                    ('ALIGN',(0,0),(0,-1),'CENTER'),
	                    ('ALIGN',(0,0),(-1,0),'CENTER'),
			])
			t._argW[3]=1.5*inch
			doc = SimpleDocTemplate(response,pagesize=landscape(LETTER),topMargin=30,bottomMargin=20)
			styleSheet = getSampleStyleSheet()
			h1 = styleSheet['Heading2']
			h1.pageBreakBefore=0
			h1.keepWithNext=1
			rango_year = int(request.GET['anio'])
			rango_month = int(request.GET['mes'])
			desde = datetime.date(1900,1,1)
			hasta = datetime.date(1900,1,1)
			if request.GET['periodo'] == '1':
				# periodo value 1 primera, los primeros quince dias
				desde = datetime.date(rango_year,rango_month,1)
				hasta = datetime.date(rango_year,rango_month,15)
			elif request.GET['periodo'] == '2':
				import calendar
				desde = datetime.date(rango_year,rango_month,16)
				hasta = datetime.date(rango_year,rango_month,calendar.monthrange(rango_year,rango_month )[1] )
			elif request.GET['periodo'] == '3':
				import calendar
				desde = datetime.date(rango_year,rango_month,1)
				hasta = datetime.date(rango_year,rango_month,calendar.monthrange(rango_year,rango_month )[1] )
			rango_periodo = "%s - %s"%(desde.strftime('%d/%m/%Y'),hasta.strftime('%d/%m/%Y'))
			P=Paragraph('Horario '+nombre +' Periodo: '+rango_periodo,h1)
			elements.append(P)
			elements.append(t)
			# write the document to disk
			doc.build(elements)
			return response
		except Exception, e:
			messages.error(request, 'No se ha podido cargar la pagina por precentar un error.')
			raise Http404('Method Proccess Fail')
	else:
		raise Http404('Method faild GET')

def returnsHours(hour=0,minute=0,second=0):
	if second >= 60:
		minute += 1
		second-=60
		if minute >= 60:
			hour += 1
			minute-=60
		if second >= 60:
			re=returnsHours(hour,minute,second)
			hour=re[0]
			minute=re[1]
			second=re[2]
	if minute >= 60:
		hour += 1
		minute-=60
		if minute >= 60:
			re=returnsHours(hour,minute,second)
			hour=re[0]
			minute=re[1]
			second=re[2]
	return [hour,minute,second]

def rpt_all_hours(request):
	if request.method == 'GET':
		try:
			from reportlab.pdfgen import canvas
			from reportlab.lib.units import cm, mm, inch
			from reportlab.lib.styles import getSampleStyleSheet
			from reportlab.platypus import Paragraph, SimpleDocTemplate, Table
			from reportlab.lib.pagesizes import landscape, LETTER
			from reportlab.lib import colors
			from django.db.models import Count
			import datetime

			response = HttpResponse(content_type='application/pdf')
			response['Content-Disposition'] = 'filename="rpt_all_hours.pdf"'
			days = {'Sunday':u'Domingo','Monday':u'Lunes','Tuesday':u'Martes','Wednesday':u'Miercoles','Thursday':u'Jueves','Friday':u'Viernes','Saturday':u'Sabado'}
			
			# obtener todo el listado de los empleados activos
			employee = models.Empleado.objects.filter(flag=True).distinct('empdni_id');
			elements = []
			tbl = [
				['Item','Nombre','Periodo','Total Horas','Total Descuento','T H. Extras','Status']
			]
			format = '%H:%M:%S'
			i = 1
			rango_periodo = ''
			for e in employee:
				emp = []
				if request.GET['type'] == 'n':
					# verificar que las fecha ingresada
					print 'optin normal'
					years = models.Asistencia.objects.filter(empdni=e.empdni_id,fecha__year=request.GET['anio']).count()
					if years > 0:
						# verificar mes que tenga registro si falla el reporte
						print e.empdni_id +' aqui el DNI que se gestiona'
						print "%02d"%int(request.GET['mes'])
						months = models.Asistencia.objects.filter(empdni=e.empdni_id,fecha__year=request.GET['anio'],fecha__month="%02d"%int(request.GET['mes'])).count()
						if months > 0:
							# vefiricar que el periodo contenga datos para realizar el reporte
							periodo = 0
							if request.GET['periodo'] == '1':
								# periodo value 1 primera, los primeros quince dias
								anio = int(request.GET['anio'])
								mes = int(request.GET['mes'])
								desde = datetime.date(anio,mes,1)
								hasta = datetime.date(anio,mes,15)
								periodo = models.Asistencia.objects.filter(empdni=e.empdni_id,fecha__range=(desde,hasta)).count()
								if periodo > 0:
									emp = models.Asistencia.objects.filter(empdni=e.empdni_id,fecha__range=(desde,hasta))
							elif request.GET['periodo'] == '2':
								import calendar
								de = datetime.date(int(request.GET['anio']),int(request.GET['mes']),16)
								hasta = datetime.date(int(request.GET['anio']),int(request.GET['mes']),calendar.monthrange(int(request.GET['anio']),int(request.GET['mes']) )[1] )
								periodo = models.Asistencia.objects.filter(empdni=e.empdni_id,fecha__range=(de,hasta)).count()
								if periodo > 0:
									emp = models.Asistencia.objects.filter(empdni=e.empdni_id,fecha__range=(de,hasta))
							else: #request.GET['periodo'] == '3':
								import calendar
								de = datetime.date(int(request.GET['anio']),int(request.GET['mes']),1)
								hasta = datetime.date(int(request.GET['anio']),int(request.GET['mes']),calendar.monthrange(int(request.GET['anio']),int(request.GET['mes']) )[1] )
								periodo = models.Asistencia.objects.filter(empdni=e.empdni_id,fecha__range=(de,hasta)).count()
								if periodo > 0:
									emp = models.Asistencia.objects.filter(empdni=e.empdni_id,fecha__range=(de,hasta))
							print 'mes encontrado continue'
						else:
							emp = []
							print 'mes menor o igual que cero'
							# redireccionar a otra pagina y mostrar mensaje
							messages.error(request, 'No se han encontrado datos para este mes!')
							#raise Http404('Method no proccess')
					else:
						# redireccionar a otra pagina para mostrar mensaje
						messages.error(request, 'No se han encontrado datos para este Año!')
						raise Http404('Method no proccess')
				elif request.GET['type'] == 'a':
					print 'dentro de advance'
					desde = datetime.date( int(request.GET['ayeari']),int(request.GET['amonthi']),int(request.GET['adayi']) )
					hasta = datetime.date( int(request.GET['ayearf']),int(request.GET['amonthf']),int(request.GET['adayf']) )
					exists = models.Asistencia.objects.filter(empdni=e.empdni_id,fecha__range=(desde,hasta)).count()
					if exists > 0:
						emp = models.Asistencia.objects.filter(empdni=e.empdni_id,fecha__range=(desde,hasta))
				# Total de Horas
				hf = 0
				mf = 0
				sf = 0
				# Total de Horas descontadas
				hdf = 0
				mdf = 0
				sdf = 0
				# Total de Horas Extras
				hxf = 0
				mxf = 0
				sxf = 0
				th = datetime.datetime(1900,1,1,0,0,0)
				#verificar que la lista de asistencia no se encuentre vacia
				if emp != []:
					nombre = ''
					#start block
					
					for x in emp:
						# statsus
						sts = ''
						almuerzo = 0
						nombre = x.empdni.empnom+', '+x.empdni.empape
						# obteniendo dia de la semana
						day = x.fecha.strftime('%A')
						# convertiendo times a datetimes
						he = datetime.datetime.strptime( x.entrada.strftime(format), format )
						# obteniendo horas trabajados del dia
						hs = datetime.datetime(1900,1,1,0,0)
						h = models.HorarioPersonal.objects.filter(empdni_id=e.empdni_id,horario__flag=True,empdni__flag=True,empdni__empdni_id=e.empdni_id)[:1]
						# vamos a obtener descuento de tardanza
						#obtener hora de ingreso tambien verificar la hora de entrada de sabados
						entrada  = datetime.time(0,0,0)
						if days[day] == 'Sabado':
							entrada = h[0].horario.satini
						else:
							entrada = h[0].horario.entrada
						entrada = datetime.datetime.strptime( entrada.strftime(format), format )
						tolerancia = datetime.datetime(1900,1,1,0,10,0) + datetime.timedelta(hours=entrada.hour,minutes=entrada.minute,seconds=entrada.second)
						des = datetime.datetime(1900,1,1,0,0,0)
						dt = datetime.datetime(1900,1,1,0,0,0)
						thextra = datetime.datetime(1900,1,1,0,0)
						# generando descuaneto por tardanza
						if he > tolerancia:
							# generamos descuento
							des = he - datetime.timedelta(hours=tolerancia.hour,minutes=tolerancia.minute,seconds=tolerancia.second)
							dt = des #datetime.timedelta(hours=des.hour,minutes=des.minute,seconds=des.second)

						if x.entrada < entrada.time():
							he = entrada
						## ver la hora de la salida si es de central o de obra para ver si tiene horas extras
						#validar que h no este vacio
						# variable de hsalida de horario
						hsalida = datetime.datetime(1900,1,1,0,0)
						dsalida = datetime.datetime(1900,1,1,0,0)
						hextras = datetime.datetime(1900,1,1,0,0)
						if h != []:
							# validando que el horario del personal es de la central
							if h[0].horario.tipo == 'CENTRAL':
								# verificar el dia de la semana
								if days[day] == 'Sabado':
									print 'dentro de Sabado'
									# verificando que el horario de salida es menor o igual que al del horario Central no se cuenta horas extras
									if x.salida == None:
										hs = h[0].horario.satfin
										hs = datetime.datetime.strptime( hs.strftime(format), format )
										almuerzo = 0
										sts = 'Default'
									if x.salida < h[0].horario.satfin:
										tmphs = datetime.datetime.strptime( x.salida.strftime(format), format )
										tmphc = datetime.datetime.strptime( h[0].horario.satfin.strftime(format), format )
										dsalida = tmphc - datetime.timedelta(hours=tmphs.hour,minutes=tmphs.minute,seconds=tmphs.second)
										dt += datetime.timedelta(hours=dsalida.hour,minutes=dsalida.minute,seconds=dsalida.second)
										hs = datetime.datetime.strptime(tmphs.strftime(format), format)
										sts = 'Incompletas'
									else:
										hsalida = h[0].horario.satfin
										hs = datetime.datetime.strptime(hsalida.strftime(format), format)
										almuerzo = 0
										sts = 'Completas'
								else:
									# verificando que el horario de salida es menor o igual que al del horario Central no se cuenta horas extras
									if x.salida == None:
										hs = h[0].horario.salida
										hs = datetime.datetime.strptime( hs.strftime(format), format )
										almuerzo = 1
										sts = 'Default'
									elif x.salida < h[0].horario.salida:
										tmphs = datetime.datetime.strptime( x.salida.strftime(format), format )
										tmphc = datetime.datetime.strptime( h[0].horario.salida.strftime(format), format )
										dsalida = tmphc - datetime.timedelta(hours=tmphs.hour,minutes=tmphs.minute,seconds=tmphs.second)
										dt += datetime.timedelta(hours=dsalida.hour,minutes=dsalida.minute,seconds=dsalida.second)
										hs = datetime.datetime.strptime(tmphs.strftime(format), format)
										if hs.time() > datetime.time(14,0,0):
											almuerzo=0 # esto tiene que valer 1
										#print almuerzo
										sts = 'Incompletas'
									else:
										hsalida = h[0].horario.salida
										hs = datetime.datetime.strptime(hsalida.strftime(format), format)
										almuerzo = 1
										sts = 'Completas'
							else:
								#Preguntar si el dia es sabado
								if days[day] == 'Sabado':
									# caso en que el tipo de horario no es de la central y/o casos especiales
									if x.salida == None:
										hs = h[0].horario.satfin
										hs = datetime.datetime.strptime( hs.strftime(format), format )
										almuerzo = 1
										sts = 'Default'
									elif x.salida < h[0].horario.salida:
										tmphs = datetime.datetime.strptime( x.salida.strftime(format), format )
										tmphc = datetime.datetime.strptime( h[0].horario.satfin.strftime(format), format )
										dsalida = tmphc - datetime.timedelta(hours=tmphs.hour,minutes=tmphs.minute,seconds=tmphs.second)
										dt += datetime.timedelta(hours=dsalida.hour,minutes=dsalida.minute,seconds=dsalida.second)
										hs = datetime.datetime.strptime(tmphs.strftime(format), format)
										if hs.time() > datetime.time(14,0,0):
											almuerzo = 1
										sts = 'Incompletas'
									elif x.salida >= h[0].horario.satfin:
										#preguntamos si tiene horas extras para ser generadas
										iniex = datetime.datetime(1900,1,1,0,0)
										if h[0].horario.extraini > datetime.time(0,0,0):
											# calculo de horas extras
											tmps = datetime.datetime.strptime(h[0].horario.satfin.strftime(format), format)
											tmpe = datetime.datetime.strptime( h[0].horario.extraini.strftime(format), format )
											iniex = tmps + datetime.timedelta(hours=tmpe.hour,minutes=tmpe.minute,seconds=tmpe.second)
											almuerzo = 1
										if x.salida > iniex.time():
											# Horas extras
											hs = datetime.datetime.strptime( x.satfin.strftime(format), format )
											hextras = hs - datetime.timedelta(hours=iniex.hour,minutes=iniex.minute,seconds=iniex.second)
											thextra += datetime.timedelta(hours=hextras.hour,minutes=hextras.minute,seconds=hextras.second)
											almuerzo = 1
											sts = 'H. Extras'
										else:
											hs = datetime.datetime.strptime(h[0].horario.satfin.strftime(format), format)
											almuerzo = 1
											sts = 'Completas'
								else:
									# caso en que el tipo de horario no es de la central y/o casos especiales
									if x.salida == None:
										hs = h[0].horario.salida
										hs = datetime.datetime.strptime( hs.strftime(format), format )
										almuerzo = 1
										sts = 'Default'
									elif x.salida < h[0].horario.salida:
										tmphs = datetime.datetime.strptime( x.salida.strftime(format), format )
										tmphc = datetime.datetime.strptime( h[0].horario.salida.strftime(format), format )
										dsalida = tmphc - datetime.timedelta(hours=tmphs.hour,minutes=tmphs.minute,seconds=tmphs.second)
										dt += datetime.timedelta(hours=dsalida.hour,minutes=dsalida.minute,seconds=dsalida.second)
										hs = datetime.datetime.strptime(tmphs.strftime(format), format)
										if hs.time() > datetime.time(14,0,0):
											almuerzo = 1
										sts = 'Incompletas'
									elif x.salida >= h[0].horario.salida:
										#preguntamos si tiene horas extras para ser generadas
										iniex = datetime.datetime(1900,1,1,0,0)
										if h[0].horario.extraini > datetime.time(0,0,0):
											# calculo de horas extras
											tmps = datetime.datetime.strptime(h[0].horario.salida.strftime(format), format)
											tmpe = datetime.datetime.strptime( h[0].horario.extraini.strftime(format), format )
											iniex = tmps + datetime.timedelta(hours=tmpe.hour,minutes=tmpe.minute,seconds=tmpe.second)
											almuerzo = 1
										if x.salida > iniex.time():
											# Horas extras
											hs = datetime.datetime.strptime( x.salida.strftime(format), format )
											hextras = hs - datetime.timedelta(hours=iniex.hour,minutes=iniex.minute,seconds=iniex.second)
											thextra += datetime.timedelta(hours=hextras.hour,minutes=hextras.minute,seconds=hextras.second)
											almuerzo = 1
											sts = 'H. Extras'
										else:
											hs = datetime.datetime.strptime(h[0].horario.salida.strftime(format), format)
											almuerzo = 1
											sts = 'Completas'
						else:
							if days[day] == 'Sabado':
								h = models.Horario.objects.filter(flag=True,tipo='CENTRAL',proyecto_id__isnull=True)[:1]
								hs = h[0].satfin
								almuerzo = 1
								sts = 'DEFAULT'
							else:
								h = models.Horario.objects.filter(flag=True,tipo='CENTRAL',proyecto_id__isnull=True)[:1]
								hs = h[0].salida
								almuerzo = 1
								sts = 'DEFAULT'
						#Este caso es solo si la hora de salida no se ha registrato
						#block salida sin data
						# endblock salida sin data

						hr = hs - datetime.timedelta(hours=he.hour,minutes=he.minute,seconds=he.second)
						th = th + datetime.timedelta(hours=hr.hour,minutes=hr.minute,seconds=hr.second)
						subt = hr - datetime.timedelta(hours=almuerzo,minutes=0)
						hf += hr.hour
						hf -= almuerzo
						mf += hr.minute
						sf += hr.second
						hdf += dt.hour
						mdf += dt.minute
						sdf += dt.second
						hxf += thextra.hour
						mxf += thextra.minute
						sxf += thextra.second
						#print dt
						#end block
				else:
					continue

				#tbl.append([i,x.fecha,days[day],x.entrada,hs.strftime(format),hr.strftime(format),dt.strftime(format),datetime.time(almuerzo,0).strftime(format),hextras.strftime(format),subt.strftime(format),sts])
				rango_year = int(request.GET['anio'])
				rango_month = int(request.GET['mes'])
				desde = datetime.date(1900,1,1)
				hasta = datetime.date(1900,1,1)
				if request.GET['periodo'] == '1':
					# periodo value 1 primera, los primeros quince dias
					desde = datetime.date(rango_year,rango_month,1)
					hasta = datetime.date(rango_year,rango_month,15)
				elif request.GET['periodo'] == '2':
					import calendar
					desde = datetime.date(rango_year,rango_month,16)
					hasta = datetime.date(rango_year,rango_month,calendar.monthrange(rango_year,rango_month )[1] )
				elif request.GET['periodo'] == '3':
					import calendar
					desde = datetime.date(rango_year,rango_month,1)
					hasta = datetime.date(rango_year,rango_month,calendar.monthrange(rango_year,rango_month )[1] )

				rht = returnsHours(hf,mf,sf)
				rdt = returnsHours(hdf,mdf,sdf)
				rxt = returnsHours(hxf,mxf,sxf)
				completas = '%i:%s:%s'%(rht[0],"%02d"%rht[1],"%02d"%rht[2])
				descuentos = '%i:%s:%s'%(rdt[0],"%02d"%rdt[1],"%02d"%rdt[2])
				extras = '%i:%s:%s'%(rxt[0],"%02d"%rxt[1],"%02d"%rxt[2])
				rango_periodo = "%s - %s"%(desde.strftime('%d/%m/%Y'),hasta.strftime('%d/%m/%Y'))
				tbl.append([
					i,nombre,rango_periodo,completas,descuentos,extras
					])
				i+=1

			t = Table(tbl, style=[
	                    ('GRID',(0,0),(-1,-1),0.5,colors.black),
	                    ('BACKGROUND',(0,0),(-1,0),colors.limegreen),
	                    ('BACKGROUND',(1,1),(-1,-1),colors.beige),
	                    ('ALIGN',(0,0),(0,-1),'CENTER'),
	                    ('ALIGN',(0,0),(-1,0),'CENTER'),
			])
			t._argW[3]=1.5*inch
			doc = SimpleDocTemplate(response,pagesize=landscape(LETTER),topMargin=10,bottomMargin=20)
			styleSheet = getSampleStyleSheet()
			elements.append( Paragraph('<font size=12>ICR PERU SA</font>', styleSheet['Normal']) )
			h1 = styleSheet['Heading1']
			h1.pageBreakBefore=0
			h1.keepWithNext=1
			P=Paragraph('Horario Periodo '+rango_periodo ,h1)
			elements.append(P)
			elements.append(t)
			# write the document to disk
			doc.build(elements)
			return response
		except Exception, e:
			messages.error(request, 'No se ha podido cargar la pagina por precentar un error.')
			#raise Http404('Method Proccess Fail')
	else:
		raise Http404('Method faild GET')
