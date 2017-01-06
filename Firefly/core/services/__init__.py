from core import ffServices

ffIndigo = None
ffNest = None

if ffServices.has_service('INDIGO'):
  if ffServices.get_boolean('INDIGO', 'enable'):
    from devices.ffIndigo.ffIndigoService import IndigoService
    ffIndigo = IndigoService()

if ffServices.has_service('NEST'):
  if ffServices.get_boolean('NEST', 'enable'):
    import nest
    ffNest = nest.Nest(ffServices.get_string('NEST','username'), ffServices.get_string('NEST','password'), local_time=True)
