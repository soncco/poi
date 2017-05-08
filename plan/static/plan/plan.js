"use strict";

var plan = plan || {};

(function($) {

    var datepickerOptions = {
        changeMonth: true,
        changeYear: true,
        dateFormat: 'dd-mm-yy'
    };

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
            $(this).find('.t-input').each(function(k) {
                total += $(this).val() * 1;
            })
            $(this).find('.total-t').val(total.toFixed(2));
        })
    }

    ocultar();
    calculo();
    sumat();
    periodos();

    var actualizarTotalFilas = function() {
        $('#id_actividad_set-TOTAL_FORMS').val($('.actividad').length);
        calculo();
    }


    $('.distribucion').bind('keyup mouseup', calculo);
    $('.t-input').bind('keyup mouseup', sumat);

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
        $row.find('.distribucion').bind('keyup mouseup', calculo);
        $row.find('.t-input').bind('keyup mouseup', sumat);
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







})(jQuery)
