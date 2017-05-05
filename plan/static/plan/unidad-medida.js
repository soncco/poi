"use strict";
var plan = plan || {};

(function($) {
    plan.acUnidadMedidaOptions = {
        minLength: 1,
        open: function() {
            var acData = $(this).data('uiAutocomplete');
            acData
                .menu
                .element
                .find('li')
                .each(function () {
                    var me = $(this);
                    var keywords = acData.term.split(' ').join('|');
                    me.html(me.text().replace(new RegExp("(" + keywords + ")", "gi"), '<strong class="text-danger">$1</strong>'));
             });;
        },
        source: function(request, response) {
            $.ajax({
                url: '/api/base/unidad/filter/',
                dataType: 'json',
                data: {
                    term: request.term
                },
                success: function(data, e) {
                    if(e)
                    response($.map(data, function (item) {
                        return {
                            data: item,
                            label: item.nombre,
                            value: item.nombre
                        }
                    }));
                }
            })
        },
        response: function(e, ui) {
            if(ui.content.length === 0) {
                var parent = $(e.target).parent();
                parent.find('.acunidadmedida').val('');
                parent.find('.id_unidad_medida').val('');
            }
        },
        select: function(e, ui) {
            var parent = $(e.target).parent().parent();
            parent.find('.id_unidad_medida').val(ui.item.data.pk);
        },
        change: function(e,ui) {
            if(!ui.item) {
                var parent = $(e.target).parent();
                parent.find('.acunidadmedida').val('');
                parent.find('.id_unidad_medida').val('');
            }
        }
    };

    $('.acunidadmedida').autocomplete(plan.acUnidadMedidaOptions);

})(jQuery);
