"use strict";

(function($) {
  $("#table").tablesorter({
    theme : "bootstrap",
    widthFixed: true,
    headerTemplate : '{content} {icon}',
    widgets : ["uitheme", "filter", "print"],
    widgetOptions : {
      filter_reset : ".reset",
    }
  })
  .tablesorterPager({
    container: $(".ts-pager"),
    cssGoto  : ".pagenum",
    removeRows: false,
    output: '{startRow} - {endRow} / {filteredRows} ({totalRows})',
    savePages : false,
  });

  $('#table').delegate('a, button', 'click', function(e) {
    e.stopPropagation();
  });


})(jQuery);
