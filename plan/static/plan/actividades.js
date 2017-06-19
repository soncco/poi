var plan = plan || {};

(function($) {
    $('.imprimir-cuadro').click(function(e) {
        e.preventDefault();
        $('#modalprint .modal-body iframe').attr("src", $(this).attr('href'));
        $('#modalprint').modal({show: true});
        return false;
    });
})(jQuery);
