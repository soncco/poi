"use strict";

var plan = plan || {};

(function($) {

    var faltante = function() {
        var presupuesto = $('#id_presupuesto').val() * 1;
        var saldo = distribucion_actividad - presupuesto;
        $('.saldo').text(saldo.toFixed(2));
    }

    var clasificadores = function() {
        var f = $('.flotante2 ul');
        f.html('');
        var clas = [];
        $('.id_clasificador').each(function(i) {
            var parent = $(this).parent();
            var c = parent.find('.ac-clasificador').val();
            if(c != '') {
                var p = parent.parent().parent().find('.total').val();
                clas.push({'c': c, 'p': (p * 1)});
            }
        });

        if (clas.length) {
            var result = [];
            clas.forEach(function(obj) {
              var id = obj.c;
              if(!this[id]) result.push(this[id] = obj);
              else this[id].p += obj.p;
            }, Object.create(null));

            //console.log(result);
            for(var i in result) {
                f.append('<li>' + result[i].c + ' =  S/' + result[i].p + '</li>');
            }
        }
    }


    var calculo = function() {
        var total = 0;
        $('.total').each(function(i) {
            total += $(this).val() * 1;
        });

        $('#presupuesto').text(total.toFixed(2));
        $('#id_presupuesto').val(total.toFixed(2));
        $('.total-cuadro').text(total.toFixed(2));

        faltante();
        clasificadores();

    }

    var sumat = function() {
        $('.producto').each(function(i) {
            var total = 0;
            var totalmonto = 0;
            // Totales tiempo.
            $(this).find('.t-input').each(function(k) {
                if(!$(this).prop('readonly'))
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

    $('.imprimir-cuadro').click(function(e) {
        e.preventDefault();
        $('#modalprint .modal-body iframe').attr("src", $(this).attr('href'));
        $('#modalprint').modal({show: true});
        return false;
    });

    $('form').submit(function(e) {
        var pre = $(this).find("button[type=submit]:focus").data('pre');
        $('#pre').val(pre);
    });

    $(window).scroll(function() {
        var top = $(document).scrollTop();
        var height = $(window).height();
        var h = $(document).height();
        if(top+height-h > -140) {
            $('.pre').fadeOut();
        } else {
            $('.pre').fadeIn();
        }
    })

})(jQuery)
