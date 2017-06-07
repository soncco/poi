"use strict";
(function($) {
    var $ejecutoras = $('#ejecutoras');
    var $template = $('<option value=""></option>');
    var clean = function() {
        $ejecutoras.html('');
        var tpl = $template.clone();
            tpl
                .text('Escoja un área ejecutora');
            tpl.appendTo($ejecutoras);
    }

    $('#unidades').on('change', function(e) {
        var val = $(this).val();
        var especial = $(this).find(':selected').data('especial');


        if(val != '') {
            $.ajax({
                dataType: 'json',
                method: 'GET',
                url: '/api/base/unidad/filter/?organica=' + val,
                success: function(data) {
                    clean();
                    data.forEach(function(unidad) {
                        var tpl = $template.clone();
                        tpl
                            .attr('value', unidad.pk)
                            .text(unidad.nombre)
                        tpl.appendTo($ejecutoras);
                    });
                    $('.areas').show('fade');
                    if(especial == 'True') {
                        $('.especial').show('fade');
                        $('#si')
                            .attr('required', 'required');
                    } else {
                        $('.especial').hide('fade');
                        $('#si')
                            .removeAttr('required');
                    }
                },
                error: function(error) {
                    alert('Ocurrió un error, por favor intente nuevamente');
                    $('.areas').hide('fade');
                    $('.especial').hide('fade');
                    $('#si')
                        .removeAttr('required');
                }
            })
        } else {
            clean();
            $('.areas').hide('fade');
            $('.especial').hide('fade');
            $('#si')
                .removeAttr('required');
        }
    });

    $('#ejecutoras').on('change', function(e) {
        var especial = $('#unidades').find(':selected').data('especial');
        if(especial == 'True') {
            var val = $(this).val();
            if(val != '') {
                $('.especial').hide('fade');
                $('#si')
                    .removeAttr('required');
            } else {
                $('.especial').show('fade');
                $('#si')
                    .attr('required', 'required');
            }
        }
    });

    clean();
})(jQuery);
