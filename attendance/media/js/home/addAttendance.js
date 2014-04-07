$(function () {
	$('.inow').datepicker({ changeMonth: true, changeYear: true, showAnim:'slide', dateFormat: 'yy-mm-dd' });
	$('.tnow').click(function  () {
		$('.inow').val(  $.datepicker.formatDate('yy-mm-dd', new Date()) );
	});
	var validation = function () {
		var $emp = $('#emp'), $fec = $('.inow'), valid = false, $in = $('.intime'), $out = $('.outtime');
		if ($emp.val().trim() != '' && $emp.val().length > 0 ) { valid = true; }else{ valid = false; };
		if ($fec.val().trim() != '' && $fec.val().length > 0 ) { valid = true; }else{ valid = false; };
		if ($in.val().trim() != '' && $in.val().length > 0) { valid = true; }else{ valid = false; };
		if($out.val().trim() != '' && $out.val().length > 0){ valid = true; }else{ valid = false; };
		return valid;
	};
	$(".btnadd").click(function () {
		if (validation()) {
			console.log('se hizo click');
			var prm = {
				emp: $('#emp').val(),
				fec: $('.inow').val(),
				in: $(".intime").val().trim(),
				out: $(".outtime").val().trim(),
				csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
			}
			$.ajax({
				url: '/ws/save/attendance/',
				data: prm,
				type: 'POST',
				dateType: 'json',
				success: function (response) {
					console.log(response);
					if (eval(response.status)) {
						setTimeout(function() {location.reload();}, 3000);
					}else{
						console.warn('El servidor a tenino problemas!');
					}
				},
				error: function () {
					throw 'Nuestro servidor se a quedado dormido.'
				}
			});
		}else{
			console.log("Existe un campo vacio!");
		};
	});
});