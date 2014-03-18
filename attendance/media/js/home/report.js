$(document).ready(function () {
	$('.t,.p,.avanzadoper,.avanzadogen').hide();
	$('.fi,.ff').datepicker({ changeMonth: true, changeYear: true, showAnim:'slide', formatDate: 'yy-mm-dd' });
	$('input[name=report]').change(function () {
		var item = this;
		if (item.checked) {
			if (item.value == 't') {
				$('.p').removeClass('bs-callout-info');
				$('.p').hide('blind',500);
			};
			if (item.value == 'p') {
				$('.t').removeClass('bs-callout-info');
				$('.t').hide('blind',500);
			};
			$('.'+item.value).addClass('bs-callout-info');
			$('.'+item.value).show('blind',1000);
		}
	});
	var aper = true;
	$('.aper').click(function () {
		if (aper) {
			$('.aper span').addClass('glyphicon-chevron-up').removeClass('glyphicon-chevron-down');
			$('.avanzadoper').show('blind',500);
			aper = false;
		}else{
			$('.aper span').addClass('glyphicon-chevron-down').removeClass('glyphicon-chevron-up');
			$('.avanzadoper').hide('blind',500);
			aper = true;
		};
	});
	var agen = true;
	$('.agen').click(function () {
		if (agen) {
			$('.agen span').addClass('glyphicon-chevron-up').removeClass('glyphicon-chevron-down');
			$('.avanzadogen').show('blind',500);
			agen = false;
		}else{
			$('.agen span').addClass('glyphicon-chevron-down').removeClass('glyphicon-chevron-up');
			$('.avanzadogen').hide('blind',500);
			agen = true;
		};
	});
	// reporte detallado
	$('.reportper').click(function () {
		//location.href=;
		var $per = $('#per');
		var $anio = $('#panio');
		var $mes = $('#pmes');
		var $periodo = $('#pperiodo');
		if ($per.val() != '') {
			if ($anio.val() != '') {
				if ($mes.val() != null) {
					if ($periodo.val() != '') {
						window.open('/single/?dni='+$('#per').val()+'&anio='+$anio.val()+'&mes='+$mes.val()+'&periodo='+$periodo.val());
					}else{
						alert('No se a seleccionado un Periodo.');
					};
				}else{
					alert('No se a seleccionado un mes para el reporte.')
				};
			}else{
				alert('No se a seleccionado un año para el reporte.');
			};
		}else{
			$('.msg-client').show('drop',1000);
		};
	});
	// 
	$('#ganio').click(function () {
		getterMonths('ganio','gmes');
	});
	$('#panio').click(function () {
		getterMonths('panio','pmes');
	});
});
var getterMonths = function (anio,mes) {
	$.ajax({
		url : '/ws/request/months/',
		type : 'GET',
		data : { 'anio' : $('#'+anio).val() },
		dataType : 'json',
		success : function (response) {
			console.log(response);
			if (response.status == 'success') {
				// rellenamos el combo
				var cbo = document.getElementById(mes);
				cbo.innerHTML = '';
				for (var x in response) {
					if (x != 'status') {
						var options = document.createElement('option');	
						options.value = x;
						options.text = response[x];
						cbo.appendChild(options);
					};
				};
			};
		},
		error : function () {
			console.log('Se ha producido un error al traer los meses');
		}
	});
}