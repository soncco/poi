from .models import Producto

def modificar_post(post, prefix):
    def get_num(string, prefix):
        return string[len(prefix):-9]

    prefix = prefix + '-'
    copy = post.copy()

    for i in copy:
        if i.find('-producto') != -1:
            if copy[i] == '':
                key = '%s%s-nuevo' % (prefix, get_num(i, prefix))
                producto = copy[key]
                nuevo_producto = Producto(descripcion = producto)
                nuevo_producto.save()
                copy[i] = nuevo_producto.pk

    return copy