from core import ffServices

ffIndigo = None

if ffServices.get_boolean('INDIGO', 'enabled'):
  from devices.ffIndigo.ffIndigoService import IndigoService
  ffIndigo = IndigoService()
