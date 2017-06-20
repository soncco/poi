"use strict";

var plan = plan || {};

(function($) {

    var datepickerOptions = {
        changeMonth: true,
        changeYear: true,
        dateFormat: 'dd-mm-yy'
    };

    $('.test').click(function(e) {
        var total = ('')
        $('.actividad').each(function(i) {
            $(this).find
        })
    })

    $('.datepicker').datepicker(datepickerOptions);

    var ocultar = function() {
        $('.m').addClass('hidden');
        if($('#id_periodo').val() == 1)
            $('.opcional').val(0);
    }

    var periodos = function() {
        if($('#id_periodo').val() == '2') {
            $('.periodo')
                .removeClass('hidden');
            $('.m').removeClass('hidden');
            $('.t').addClass('hidden');
            $('.opcional')
                .removeAttr('readonly')
                .attr('required', 'required');
        } else {
            $('.periodo')
                .addClass('hidden');
            $('.m').addClass('hidden');
            $('.t').removeClass('hidden');
            $('.opcional')
                .val(0)
                .removeAttr('required')
                .attr('readonly', 'readonly');
        }
        sumat();
    }

    var $periodo = $('#id_periodo');
    $periodo.change(periodos);


    var calculo = function() {
        var total = 0;
        $('.distribucion').each(function(i) {
            total += $(this).val() * 1;
        });

        $('#presupuesto').text(total.toFixed(2));
        $('#id_presupuesto').val(total.toFixed(2));

        $('.actividad').each(function(i) {
            var $peso = $(this).find('.peso');
            var $distribucion = $(this).find('.distribucion');
            var peso = ($distribucion.val() * 1) * 100 / total;
            if(isNaN(peso)) peso = 0;
            $peso.val(peso.toFixed(2));
        });
    }

    var sumat = function() {
        $('.actividad').each(function(i) {
            var total = 0;
            var totalmonto = 0;
            // Totales tiempo.
            $(this).find('.t-input').each(function(k) {
                total += $(this).val() * 1;
            })
            $(this).find('.total-t').val(total.toFixed(2));

            // Totales monto.
            $(this).find('.m-input').each(function(k) {
                totalmonto += $(this).val() * 1;
            })
            $(this).find('.distribucion').val(totalmonto.toFixed(2));
            $(this).find('.distribucion').trigger('change');
        })
    }

    ocultar();
    calculo();
    sumat();
    periodos();

    var actualizarTotalFilas = function() {
        var total = $('.actividad').length;
        $('#id_actividad_set-TOTAL_FORMS').val(total);
        $('.actividad').each(function(i) {
            var $this = $(this);
            var selector = '[name*='+ prefix +'-]';
            var $el = $this.find(selector);
            $el.each(function(j) {
                var suffix = $(this).attr('name').split('-')[2];
                $(this).attr('name', prefix + '-' + i + '-' + suffix);
            });
        });
        calculo();
    }


    $('.distribucion').bind('change', calculo);
    $('.t-input').bind('keyup mouseup', sumat);
    $('.m-input').bind('keyup mouseup', sumat);

    var quitar = function() {
        if($('.actividad').length == 1) {
            alert('No se puede quitar la única actividad.');
            return false;
        }
        if(confirm('¿Estás seguro?')) {
            $(this).parent().parent().remove();
            ocultar();
            calculo();
            sumat();
            actualizarTotalFilas();
        }

    }

    $('.quitar-actividad').click(quitar);


    var delegateEvents = function(row) {
        var $row = $(row);
        $row.find('.distribucion').bind('change', calculo);
        $row.find('.t-input').bind('keyup mouseup', sumat);
        $row.find('.m-input').bind('keyup mouseup', sumat);
        $row.find('.quitar-actividad').bind('click', quitar);
        $row.find('.datepicker').datepicker(datepickerOptions);
        $row.find('.acunidadmedida').autocomplete(plan.acUnidadMedidaOptions);
        return $row;
    }

    $('.agregar-actividad').click(function() {
        var filas = $('.actividad').length;
        var template = $('#template').html();
        Mustache.parse(template);
        var rendered = Mustache.render(template, {'numero': filas});
        var $rendered = delegateEvents(rendered);
        $('.actividades').append($rendered);
        ocultar();
        calculo();
        sumat();
        actualizarTotalFilas();
        periodos();
    });

    $('.print').click(function(e) {
        e.preventDefault();
        $('#modalprint .modal-body iframe').attr("src", $(this).attr('href'));
        $('#modalprint').modal({show: true});
        return false;
    })



    $('.aprobar').click(function(e) {
        e.preventDefault();
        var r = confirm('¿Estás seguro de aprobar este plan?');
        if(r) {
            $('#id_aprobado').val('True');
            $('.form-aprobar').submit();
        }
    })

    $('.desaprobar').click(function(e) {
        e.preventDefault();
        var r = confirm('¿Estás seguro de quitar la aprobación de este plan?');
        if(r) {
            $('#id_aprobado').val('False');
            $('.form-aprobar').submit();
        }
    })

    // Evaluación

    var calculoEvaluacion = function() {

        $('.actividad').each(function(i) {

            var resultadototal = 0;
            var resultadomonto = 0;

            $(this).find('.resultadot').each(function(i) {
                resultadototal += $(this).val() * 1;
            });
            $(this).find('.resultadop').each(function(i) {
                resultadomonto += $(this).val() * 1;
            });

            $(this).find('.resultadototal').val(resultadototal.toFixed(2));
            $(this).find('.resultadomonto').val(resultadomonto.toFixed(2));

            var actividad_total = $(this).find('.actividad-total').data('val') * 1;
            var actividad_distribucion = $(this).find('.actividad-distribucion').data('val') * 1;

            var porcentajet = resultadototal * 100 / actividad_total;
            var porcentajep = resultadomonto * 100 / actividad_distribucion;

            var clasep = 'text-success';
            var alertap = 'Adecuado';
            var claset = 'text-success';
            var alertat = 'Adecuado';

            if(porcentajet < 50) {
                claset = 'text-danger';
                alertat = 'Retrasado';
            } else if (porcentajet >= 50 && porcentajet < 75) {
                claset = 'text-warning';
                alertat = 'Aceptable';
            }

            if(porcentajep < 50) {
                clasep = 'text-danger';
                alertap = 'Retrasado';
            } else if (porcentajep >= 50 && porcentajep < 75) {
                clasep = 'text-warning'
                alertap = 'Aceptable';
            }

            $(this).find('.porcentajet span')
                .text(porcentajet.toFixed(2) + '%')
                .removeClass()
                .addClass(claset);
            $(this).find('.porcentajep span')
                .text(porcentajep.toFixed(2) + '%')
                .removeClass()
                .addClass(clasep);

            $(this).find('.alertat span')
                .text(alertat)
                .removeClass()
                .addClass(claset);
            $(this).find('.alertap span')
                .text(alertap)
                .removeClass()
                .addClass(clasep);

        })

    }

    calculoEvaluacion();
    $('.resultadot').bind('keyup mouseup', calculoEvaluacion);
    $('.resultadop').bind('keyup mouseup', calculoEvaluacion);


    $('.guardar-actividad').click(function(e) {
        var pk = $(this).data('actividad');
        $.ajax({
            url: '/actividad/guardar/',
            type: 'POST',
            data: $('.actividad-' + pk).serialize(),
            success: function(data) {
                alert('Se guardaron los datos de esta actividad.');
            },
            error: function(data) {
                alert('No se pudo guardar los datos de la actividad, intente nuevamente.')
            }
        });
        
        return false;
    });


})(jQuery)
