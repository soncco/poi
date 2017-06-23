from plan.models import Actividad
from django.db.models import Sum

def traer_suma(fuente, modelo, tipo):
    if tipo == 'o':
        suma = Actividad.objects.filter(asignacion_presupuestal = fuente, pertenece_a__unidad_organica = modelo)
    else:
        suma = Actividad.objects.filter(asignacion_presupuestal = fuente, pertenece_a__area_ejecutora = modelo)
    
    total = suma.aggregate(Sum('distribucion_presupuestal'))['distribucion_presupuestal__sum']
    if total is None:
        total = 0

    return total
