"use strict";
var plan = plan || {};

(function($) {
    plan.acProductoOptions = {
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
                url: '/api/cuadro/producto/filter/',
                dataType: 'json',
                data: {
                    term: request.term
                },
                success: function(data, e) {
                    if(e)
                    response($.map(data, function (item) {
                        return {
                            data: item,
                            label: item.descripcion,
                            value: item.descripcion
                        }
                    }));
                }
            })
        },
        response: function(e, ui) {
            if(ui.content.length == 0) {
                var parent = $(e.target).parent();
                parent.find('.id_producto').val('');
                parent.parent().parent().find('.unitario').val('');
            }
            
        },
        select: function(e, ui) {
            var parent = $(e.target).parent().parent();
            parent.find('.id_producto').val(ui.item.data.id);
            parent.parent().parent().find('.unitario').val(ui.item.data.precio);
        },
        change: function(e,ui) {
            if(!ui.item) {
                var parent = $(e.target).parent();
                parent.find('.id_producto').val('');
                parent.parent().parent().find('.unitario').val('');
            }
        },

    };

    $('.ac-producto').autocomplete(plan.acProductoOptions);

})(jQuery);
