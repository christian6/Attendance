$(document).ready(function () {
	$('input').focus();
	gethour();
});
//var form = $("input[name=dform]").val();

var segundos = fser.getSeconds();
var hora = fser.getHours(); 
var minutos = fser.getMinutes();
var gethour = function () {
	segundos++; 
	if (segundos == 60) {
		segundos = 0;
		minutos++;
		if (minutos == 60) {
			minutos = 0;
			hora++;
			if (hora == 24) {
				hora = 0;
			}
		}
	}
	var horita = " "  + hora + ":" + minutos + ":" + segundos;
	$('.text-hour').html($("input[name=dlarge]").val()+"  "+horita);
	setTimeout(function() { gethour(); }, 970);
	hlocal();
}
var hlocal = function () {
	var hour = new Date();
	$('.hl').html("Hora Local: "+hour.toLocaleString() );
}