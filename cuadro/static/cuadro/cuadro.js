"use strict";

var plan = plan || {};

(function($) {


    var calculo = function() {
        var total = 0;
        $('.total').each(function(i) {
            total += $(this).val() * 1;
        });

        $('#presupuesto').text(total.toFixed(2));
        $('#id_presupuesto').val(total.toFixed(2));

    }

    var sumat = function() {
        $('.producto').each(function(i) {
            var total = 0;
            var totalmonto = 0;
            // Totales tiempo.
            $(this).find('.t-input').each(function(k) {
                total += $(this).val() * 1;
            })
            $(this).find('.total-cantidades').val(total.toFixed(2));

            // Totales monto.
            var unitario = $(this).find('.unitario').val() * 1;
            if(isNaN(unitario)) unitario = 0;
            totalmonto = unitario * total;
            $(this).find('.total-cantidades').val(total.toFixed(2));

            $(this).find('.total').val(totalmonto.toFixed(2));
            $(this).find('.total').trigger('change');
        })
    }

    calculo();
    sumat();

    var actualizarTotalFilas = function() {
        var total = $('.producto').length;
        $('#id_cuadrodetalle_set-TOTAL_FORMS').val(total);
        $('.producto').each(function(i) {
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


    $('.total').bind('change', calculo);
    $('.t-input').bind('keyup mouseup', sumat);
    $('.unitario').bind('keyup mouseup', sumat);

    var quitar = function() {
        if($('.producto').length == 1) {
            alert('No se puede quitar el único producto.');
            return false;
        }
        if(confirm('¿Estás seguro?')) {
            $(this).parent().parent().parent().remove();
            calculo();
            sumat();
            actualizarTotalFilas();
        }

    }

    $('.quitar-producto').click(quitar);


    var delegateEvents = function(row) {
        var $row = $(row);
        $row.find('.total').bind('change', calculo);
        $row.find('.t-input').bind('keyup mouseup', sumat);
        $row.find('.unitario').bind('keyup mouseup', sumat);
        $row.find('.quitar-producto').bind('click', quitar);
        $row.find('.ac-producto').autocomplete(plan.acProductoOptions);
        $row.find('.ac-clasificador').autocomplete(plan.acClasificadorOptions);
        return $row;
    }

    $('.agregar-producto').click(function() {
        var filas = $('.producto').length;
        var template = $('#template').html();
        Mustache.parse(template);
        var rendered = Mustache.render(template, {'numero': filas});
        var $rendered = delegateEvents(rendered);
        $('.productos').append($rendered);
        calculo();
        sumat();
        actualizarTotalFilas();
    });

    $('.borrar-cuadro').click(function(e) {
        var c = confirm('¿Estás seguro de borrar este cuadro de necesidades?');
        if(!c) {
            e.preventDefault();
        }
    });

    $('.imprimir-cuadro').click(function(e) {
        e.preventDefault();
        $('#modalprint .modal-body iframe').attr("src", $(this).attr('href'));
        $('#modalprint').modal({show: true});
        return false;
    });

})(jQuery)
