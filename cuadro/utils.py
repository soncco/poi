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
                producto = copy[key].strip()
                try:
                    nuevo_producto, created = Producto.objects.get_or_create(descripcion = producto)
                    nuevo_producto.save()
                except:
                    nuevo_producto= Producto.objects.filter(descripcion = producto)
                    nuevo_producto = nuevo_producto[0]
                    nuevo_producto.save()
                copy[i] = nuevo_producto.pk

    return copy

def actualizar_precio(cuadro):
    for detalle in cuadro.cuadrodetalle_set.all():
        if detalle.precio != 0:
            p = Producto.objects.get(pk = detalle.producto.pk)
            p.precio = detalle.precio
            p.save()
