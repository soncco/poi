def crear_enlace(href, clase, titulo, icono):
    return '<a href="%s" class="btn btn-%s btn-xs" title="%s"><i class="fa fa-%s"></i></a> ' % (href, clase, titulo, icono)
