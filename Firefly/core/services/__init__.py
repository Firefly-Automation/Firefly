from core import ffServices

ffIndigo = None

if ffServices.has_service('INDIGO'):
  if ffServices.get_boolean('INDIGO', 'enable'):
    from devices.ffIndigo.ffIndigoService import IndigoService
    ffIndigo = IndigoService()
