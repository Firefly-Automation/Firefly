DEVICE_TEMPLATE='''
  <div class="col-md-3">

<br>
<center>
<button type="button" class="btn btn-primary" data-toggle="modal" data-target=".bs-example-modal-MODID" style="width:90%;height:45px;text-align: center; ">TITLE</button>

<div class="modal fade bs-example-modal-MODID" tabindex="-1" role="dialog" aria-labelledby="mySmallModalLabel">

  <div class="modal-dialog modal-MODID">

  <div class="modal-content">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
    <h4 class="modal-title">TITLE : STATUS </h4>
    </div>


    
          <div class="row">
          <br>
          COMMANDS


    </div>
  </div>
  </div>
</div>
</center>

    
  </div>

  '''

COMMAND_TEMPLATE='''
            <div class="col-md-6">
              <form style="text-align:center" class="form-inline" enctype='application/json' action=/API/translator method='POST'>
                <input name='device' value='DEVICE' type='hidden'>
                <input name='command' value='COMMAND' type='hidden'>
                <input name='value' value='VALUE' type='hidden'>
              <input class="btn btn-default" type="submit" value='CTITLE' >
              </form>
            </div>
'''

PAGE_TEMPLATE = '''
<html>
  <head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Latest compiled and minified CSS -->
    <link href="/static/css/bootstrap.min.css" rel="stylesheet">
    <link href="/static/css/bootstrap-switch.css" rel="stylesheet">

    <script src="/static/js/jquery.min.js"></script> 
    <script src="/static/js/bootstrap.min.js"></script>
    <script src="/static/js/bootstrap-switch.js"></script>


  </head>
  
  <body>
NAVBAR
    <div class=container>

      <div class="row">
        PAGEBODY
      </div>
    </div>
  </body>
</html>
'''


NAV_TEMPLATE='''
<nav class="navbar navbar-inverse">
  <div class="container">
  <!-- Brand and toggle get grouped for better mobile display -->
  <div class="navbar-header">
    <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
    <span class="sr-only">Toggle navigation</span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
    </button>
    <a class="navbar-brand" href="#">Firefly</a>
  </div>

  <!-- Collect the nav links, forms, and other content for toggling -->
  <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
    <ul class="nav navbar-nav">
    NAVLINKS
    </ul>
  </div><!-- /.navbar-collapse -->
  </div><!-- /.container-fluid -->
</nav>
'''


@app.route('/debugView')
@flask_login.login_required
def debugView():
  page_body = ""
  allDevices = getAllDevices().get('all_devices')
  navbar = formNavbar(allDevices, 'all')
  for name, options in collections.OrderedDict(sorted(allDevices.items())).iteritems():
    if options is not True and options is not False:
      device_name = name
      device_title = options.get('title')
      device_config = ""
      device_body = ""
      device_status = options.get('value')
      print device_name
      print device_status
      if options.get('config'):
        for c, v in options.get('config').iteritems():
          print v.get('value')
          device_config += str(COMMAND_TEMPLATE).replace('DEVICE',device_name).replace('CTITLE',c).replace('COMMAND',v.get('command')).replace('VALUE',v.get('value')).replace('ID',device_title.replace(' ', ''))

      device_body = DEVICE_TEMPLATE.replace('TITLE', device_title).replace('COMMANDS', device_config).replace('STATUS',device_status)
      if device_status == 'Active':
        device_body = device_body.replace('panel-default','panel-danger')
      if device_status == 'Inactive':
        device_body = device_body.replace('panel-default','panel-success')
      page_body += device_body

  return PAGE_TEMPLATE.replace('PAGEBODY',page_body).replace('NAVBAR', navbar)


def generateDeviceView(dtype):
  count = 0
  page_body = ""
  allViews = getAllDevices()
  allDevices = allViews.get('all_devices')
  dashboarGroups = allViews.get('dashboard_groups')
  navbar = formNavbar(allDevices, dashboarGroups, dtype)
  filtered_devices = {}
  for name, device in allDevices.iteritems():
    if not isinstance(allDevices[name], bool):
      filtered_devices[name] = device
  allDevices = filtered_devices
  for name, options in collections.OrderedDict(sorted(allDevices.items(), key=lambda elem: elem[1]['title'])).iteritems():
    if options is not True and options is not False:
      if options.get('capabilities') is not None and dtype in options.get('capabilities') or dtype == 'all':
        device_name = name
        device_title = options.get('title')
        device_config = ""
        device_body = ""
        device_status = options.get('value')
        if options.get('config'):
          for c, v in options.get('config').iteritems():
            print v.get('value')
            device_config += str(COMMAND_TEMPLATE).replace('DEVICE',device_name).replace('CTITLE',c).replace('COMMAND',v.get('command')).replace('VALUE',v.get('value'))
        else:
          device_config = '<div class="row"><div class="col-md-6" style="height:45px;"></div><div class="col-md-6"></div><div class="col-md-6" style="height:30px;"></div><div class="col-md-6"></div></div>'

        device_body = DEVICE_TEMPLATE.replace('TITLE', device_title).replace('COMMANDS', device_config).replace('STATUS',device_status).replace('MODID',device_name.replace(' ', ''))
        if device_status == 'Active':
          device_body = device_body.replace('panel-default','panel-danger')
        if device_status == 'Inactive':
          device_body = device_body.replace('panel-default','panel-success')
        page_body += device_body

  return PAGE_TEMPLATE.replace('PAGEBODY',page_body).replace('NAVBAR', navbar)

def generateGroupView(groupName):
  page_body = ""
  allViews = getAllDevices()
  allDevices = allViews.get('all_devices')
  dashboarGroups = allViews.get('dashboard_groups')
  navbar = formNavbar(allDevices, dashboarGroups, groupName)

  filtered_devices = {}
  for name, device in allDevices.iteritems():
    if not isinstance(allDevices[name], bool):
      filtered_devices[name] = device
  allDevices = filtered_devices
  for name, options in collections.OrderedDict(sorted(allDevices.items(), key=lambda elem: elem[1]['title'])).iteritems():
    if options is not True and options is not False and name in dashboarGroups.get(groupName):
      if options.get('capabilities') is not None:
        device_name = name
        device_title = options.get('title')
        device_config = ""
        device_body = ""
        device_status = options.get('value')
        if options.get('config'):
          for c, v in options.get('config').iteritems():
            device_config += str(COMMAND_TEMPLATE).replace('DEVICE',device_name).replace('CTITLE',c).replace('COMMAND',v.get('command')).replace('VALUE',v.get('value'))
        else:
          device_config = '<div class="row"><div class="col-md-6" style="height:45px;"></div><div class="col-md-6"></div><div class="col-md-6" style="height:30px;"></div><div class="col-md-6"></div></div>'

        device_body = DEVICE_TEMPLATE.replace('TITLE', device_title).replace('COMMANDS', device_config).replace('STATUS',device_status).replace('MODID',device_name.replace(' ', ''))
        if device_status == 'Active':
          device_body = device_body.replace('panel-default','panel-danger')
        if device_status == 'Inactive':
          device_body = device_body.replace('panel-default','panel-success')
        page_body += device_body

  return PAGE_TEMPLATE.replace('PAGEBODY',page_body).replace('NAVBAR', navbar)

def formNavbar(devices, groups, current):
  navlinks = ''
  c = getDeviceCapabilities(devices)
  i = 'all'
  navlinks += '<li><a href="/devices/'+i+'">'+i.upper()+'</a></li>' if i != current else '<li class="active"><a href="/devices/'+i+'">'+i.upper()+' <span class="sr-only">(current)</span></a></li>'
  for i in sorted(groups):
    navlinks += '<li><a href="/groups/'+i+'">'+i.upper()+'</a></li>' if i != current else '<li class="active"><a href="/groups/'+i+'">'+i.upper()+' <span class="sr-only">(current)</span></a></li>'

  navlinks += '''<li class="dropdown">
      <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">DEVICES <span class="caret"></span></a>
      <ul class="dropdown-menu">
    '''
  for i in sorted(c):
    
    navlinks += '<li><a href="/devices/'+i+'">'+i.upper()+'</a></li>' if i != current else '<li class="active"><a href="/devices/'+i+'">'+i.upper()+' <span class="sr-only">(current)</span></a></li>'
  navlinks += '''
        </ul>
  </li>
  '''

  return NAV_TEMPLATE.replace('NAVLINKS', navlinks)
