from plan.utils import traer_opcion

def mensaje_poi(request):
  return {
    'mostrar_mensaje': traer_opcion('mostrar_mensaje'),
    'mensaje': traer_opcion('mensaje'),
  }
