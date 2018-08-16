from openpyxl import load_workbook
wb = load_workbook(filename = r'utiles.xlsx')
from cuadro.models import Producto
from decimal import Decimal

s = wb['utiles']

rows = s.get_highest_row()

for i in range(2,rows):
  nombre = s['A%s' % i].value
  clasificador = s['B%s' % i].value
  u_medida = s['C%s' % i].value
  precio = Decimal(s['D%s' % i].value)
  try:
    _producto, created = Producto.objects.get_or_create(descripcion = nombre, defaults={'clasificador': clasificador, 'unidad_medida': u_medida, 'precio': precio})
    _producto.save()
  except:
    producto = Producto.objects.filter(descripcion = nombre)[0]
    producto.clasificador_id = clasificador
    producto.unidad_medida = u_medida
    producto.precio = precio
    producto.save()
    print 'Duplicado: %s' % producto.pk
