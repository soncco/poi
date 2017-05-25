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

