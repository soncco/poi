"use strict";

(function($) {
  var $p1 = $('#password');
  var $p2 = $('#password2');

  $('#the-form').submit(function(e) {
      if($p1.val() != '') {
          if($p2.val() != $p1.val()) {
              alert('Las contraseñas no coinciden');
              e.preventDefault();
          }
      }
  });

})(jQuery)
