"use strict";

(function($) {
  var $p1 = $('#password');
  var $p2 = $('#password2');

  $p2.blur(function() {
    if($p1.val() != $p2.val()) {
      alert('Las contraseñas no coinciden.');
    } 
  });

  $('#the-form').submit(function(e) {

    var checked = false;
    $('.grupo').each(function() {
      if($(this).is(':checked')) {
        checked = true;
      }
    });

    if(!checked) {
      alert('Selecciona al menos un acceso.');
      e.preventDefault();
      return false;
    }

  });

})(jQuery)

