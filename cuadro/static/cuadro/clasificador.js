"use strict";
var plan = plan || {};

(function($) {
  plan.acClasificadorOptions = {
    minLength: 1,
    open: function(e, ui) {
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
        url: '/api/cuadro/clasificador/filter/',
        dataType: 'json',
        data: {
          term: request.term
        },
        success: function(data, e, xhr) {
          if(e)
          response($.map(data, function (item) {
            return {
              data: item,
              label: item.cadena + ' - ' + item.descripcion,
              value: item.cadena,
            }
          }));
        }
      })
    },
    response: function(e, ui) {
      if(ui.content.length === 0) {
        var parent = $(e.target).parent();
        parent.find('.ac-clasificador').val('');
        parent.find('.id_clasificador').val('');
      }
    },
    select: function(e, ui) {
      var parent = $(e.target).parent();
      parent.find('.id_clasificador').val(ui.item.data.id);
    },
    change: function(e,ui) {
      if(!ui.item) {
        var parent = $(e.target).parent();
        parent.find('.ac-clasificador').val('');
      }
    }
  }

  $('.ac-clasificador').autocomplete(plan.acClasificadorOptions);



})(jQuery);
