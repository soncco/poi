var plan = plan || {};

(function($) {
    $('.imprimir-cuadro').click(function(e) {
        e.preventDefault();
        $('#modalprint .modal-body iframe').attr("src", $(this).attr('href'));
        $('#modalprint').modal({show: true});
        return false;
    });

    $('.borrar-cuadro').click(function(e) {
        var c = confirm('¿Estás seguro de borrar este cuadro de necesidades?');
        if(!c) {
            e.preventDefault();
        }
    });
})(jQuery);
