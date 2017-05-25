from openpyxl import load_workbook
wb = load_workbook(filename = r'usuarios.xlsx')
from django.contrib.auth.models import User, Group

s = wb['Usuarios']

rows = s.get_highest_row()

for i in range(2,rows):
  usuario = s['A%s' % i].value
  nombres = s['B%s' % i].value
  print usuario
  _user, created = User.objects.get_or_create(username = usuario, password = usuario)
  _user.first_name = nombres
  _user.save()
  the_grupo = Group.objects.get(pk = 3)
  _user.groups.add(the_grupo)

from openpyxl import load_workbook
wb = load_workbook(filename = r'oficinas.xlsx')
from base.models import Unidad

s = wb['Oficinas']

rows = s.get_highest_row()

for i in range(2,rows):
  nombre = s['A%s' % i].value
  abreviatura = s['B%s' % i].value
  print nombre
  _oficina, created = Unidad.objects.get_or_create(nombre = nombre, abreviatura = abreviatura, pertenece_a = 1)
  _oficina.save()
