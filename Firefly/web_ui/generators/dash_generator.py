# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-05-22 14:40:40
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-08-16 13:51:18

import collections
import json


def dash_generator(devices):
  returnData = {}
  devices = collections.OrderedDict(sorted(devices.iteritems(), key=lambda elem: elem[1]['name']))
  for device, config in devices.iteritems():
    if config.get('name') is not None:
      if config.get('dash_view').get('type') == "switch":
        returnData[config.get('name')] = generate_switch(config)
      if config.get('dash_view').get('type') == "text":
        returnData[config.get('name')] = generate_text(config)
      if config.get('dash_view').get('type') == "button":
        returnData[config.get('name')] = generate_button(config)
      if config.get('dash_view').get('type') == "stateValue":
        returnData[config.get('name')] = generate_stateValue(config)

  returnData = collections.OrderedDict(sorted(returnData.items()))
  return returnData

def refresh_generator():
  refreshJS = ''' '''
  '''
  String.prototype.replaceAll = function(target, replacement) {
    return this.split(target).join(replacement);
  };

  function refreshFunction(){
    console.log("REFRESH")
  
    var data = $.ajax({
        type: "GET",
        url: "/API/allDevices",
        async: false
      })
      .responseText;
    var allDevices = eval('(' + data + ')');
    for (var device in allDevices){
        if (allDevices[device]['views']){ 
        if (allDevices[device]['views']['dash_view']){
          var request = allDevices[device]['views']['dash_view']['request']
          var status = allDevices[device][request].toString()
          var deviceID = 'D_' + device.replaceAll('-','__')
          //console.log(deviceID)
          //console.log(status)

          window[ deviceID ](status, false)
        }
      }
    }
  }

  '''
  return refreshJS


#def generate_button(config):
#  deviceTemplate = '''
#  <div class="col s12 m6 l4">
#    <div class="card-panel grey darken-1 hoverable" style="padding:0px; height: 65px">
#    <table>
#    <tbody>
#      <tr>
#        <td>
#          <span class="white-text" style="padding-left:10px">$NAME$</span>
#        </td>
#        <td style="width:10%; padding: 10px">
#          $BUTTONS$
#        </td>
#        <td style="width:10%">
#          <a class="modal-trigger" href="#$ID$-modal"><i class="material-icons right-align white-text" style="font-size: 35px;">more_vert</i></a>
#        </td>
#      </tr>
#      </tbody>
#      </table>
#      <div id="$ID$-modal" class="modal">
#          <div class="modal-content center grey-text">
#            <h4>$NAME$</h4>
#            <embed src="/devices/views/$IDRAW$" width="100%" />
#          </div>
#          <div class="modal-footer">
#            <a href="#!" class=" modal-action modal-close waves-effect waves-green btn-flat">Close</a>
#          </div>
#          <script>
#            $JAVASCRIPT$
#          </script>
#        </div>
#    </div>
#  </div>
#  '''

def generate_switch(config):

  
  #buttonTemplate = '''<a id="$ID$-$VALUE$" name="$ID$-$VALUE$" class="waves-effect waves-light btn $COLOR$" onClick="$ID$('$CLICK$', true)" style="display:$DISPLAY$; padding: 0px; width: 65px; font-size: 15px">$TEXT$</a>'''
  buttonTemplate =""

  #TODO: Rename this switch template
  deviceTemplate = '''
    <ul class="collection ">
      <li class="collection-item grey lighten-3">
        <span class="title">$NAME$</span>
        <div class="secondary-content" style="top:30%">
          <div class="switch">
            <label>
            Off
            <input name="$ID$_switch" raw="$IDRAW$" commands='$COMMANDS$' type="checkbox" onClick="myFunct(this.checked, this.name, 'checkbox', this.getAttribute('raw'), this.getAttribute('commands'))">
            <span class="lever"></span>
            On
          </label>
          </div>
        </div>
        <a class="modal-trigger" href="#$ID$-modal"><i class="material-icons grey-text" style="vertical-align: middle">more_vert</i></a>
      </li>
    </ul>
    <div id="$ID$-modal" class="modal modal-fixed-footer" style="height:100%; overflow-y:hidden">
      <div class="modal-content center grey-text scroll-wrapper">
        <h4>$NAME$</h4>
        <embed src="/devices/views/$IDRAW$" width="100%" height="85%" />
      </div>
      <div class="modal-footer">
        <a href="#!" class=" modal-action modal-close waves-effect waves-green btn-flat">Close</a>
      </div>
    </div>
 

  '''

  jsTemplate = '''
  function $ID$(value, send){
    if (value =="on") {
    //console.log("Turn On")
    document.getElementById("off").style.display = 'none'
    document.getElementById("on").style.display = ''
    } else if (value =="off") {
    //console.log("Turn Off")
    document.getElementById("off").style.display = ''
    document.getElementById("on").style.display = 'none'
    }
  }
  '''

  name = config.get('name')
  deviceIDRaw = config.get('id')
  deviceID = config.get('id').replace('-',"__")
  buttons = config.get('dash_view').get('switch')
  commands = {}
  for c, s in buttons.iteritems():
    commands[c] = s.get('command')


  print name
  generated_buttons = []
  for b, c in buttons.iteritems():
    #print b
    #print c
    color = c.get('color')
    text = c.get('text')
    click = c.get('click')
    display = '' if c.get('default') else 'none'
    #generated_buttons.append(buttonTemplate.replace('$ID$', 'D_' + str(deviceID)).replace('$VALUE$', b).replace('$COLOR$', color).replace('$CLICK$',click).replace('$TEXT$', text).replace('$DISPLAY$',display).replace('$IDRAW$',deviceIDRaw).replace('$COMMANDS$', json.dumps(commands)))


  generated_button = deviceTemplate.replace('$ID$', 'D_' + str(deviceID)).replace('$NAME$', name).replace('$IDRAW$',deviceIDRaw).replace('$COMMANDS$', json.dumps(commands))

  return generated_button


def generate_text(config):

  deviceTemplate = '''
    <ul class="collection">
      <li class="collection-item grey lighten-3">
        <span class="title">$NAME$</span>
        <a class="modal-trigger" href="#$ID$-modal"><i class="material-icons grey-text" style="vertical-align: middle">more_vert</i></a>
        <div class="secondary-content" style="vertical-align: middle">
          <a name="$ID$_text" class="grey-text" raw="$IDRAW$" commands='$COMMANDS$' style="font-size:90%;" href="#" onClick="myFunct(null, this.name, 'text', this.getAttribute('raw'), this.getAttribute('commands'))">Unknown</a>
        </div>
      </li>
    </ul>
    <div id="$ID$-modal" class="modal modal-fixed-footer" style="height:100%; overflow-y:hidden">
      <div class="modal-content center grey-text scroll-wrapper">
        <h4>$NAME$</h4>
        <embed src="/devices/views/$IDRAW$" width="100%" height="85%" />
      </div>
      <div class="modal-footer">
        <a href="#!" class=" modal-action modal-close waves-effect waves-green btn-flat">Close</a>
      </div>
    </div>
  '''

  name = config.get('name')
  deviceIDRaw = config.get('id')
  deviceID = config.get('id').replace('-',"__")
  buttons = config.get('dash_view').get('text')
  settings = {}
  for c, s in buttons.iteritems():
    settings[c] = {"command":s.get('command'), "text":s.get('text'), "color":s.get('color')}

  generated_text = deviceTemplate.replace('$ID$', 'D_' + str(deviceID)).replace('$NAME$', name).replace('$IDRAW$',deviceIDRaw).replace('$COMMANDS$', json.dumps(settings))

  return generated_text

def generate_stateValue(config):

  deviceTemplate = '''
    <ul class="collection">
      <li class="collection-item grey lighten-3">
        <span class="title">$NAME$</span>
        <a class="modal-trigger" href="#$ID$-modal"><i class="material-icons grey-text" style="vertical-align: middle">more_vert</i></a>
        <div class="secondary-content" style="vertical-align: middle">
          <a name="$ID$_stateValue" class="grey-text" raw="$IDRAW$" commands='$COMMANDS$' style="font-size:90%;" href="#" onClick="myFunct(null, this.name, 'stateValue', this.getAttribute('raw'), this.getAttribute('commands'))">Unknown</a>
        </div>
      </li>
    </ul>
    <div id="$ID$-modal" class="modal modal-fixed-footer" style="height:100%; overflow-y:hidden">
      <div class="modal-content center grey-text scroll-wrapper">
        <h4>$NAME$</h4>
        <embed src="/devices/views/$IDRAW$" width="100%" height="85%" />
      </div>
      <div class="modal-footer">
        <a href="#!" class=" modal-action modal-close waves-effect waves-green btn-flat">Close</a>
      </div>
    </div>
  '''

  name = config.get('name')
  deviceIDRaw = config.get('id')
  deviceID = config.get('id').replace('-',"__")
  stateValue = config.get('dash_view').get('state')
  settings = {}
  for c, s in stateValue.iteritems():
    settings[c] = {"command":s.get('command'), "value":s.get('value'), "color":s.get('color')}

  generated_stateValue = deviceTemplate.replace('$ID$', 'D_' + str(deviceID)).replace('$NAME$', name).replace('$IDRAW$',deviceIDRaw).replace('$COMMANDS$', json.dumps(settings))

  return generated_stateValue


def generate_button(config):

  deviceTemplate = '''
    <ul class="collection">
      <li class="collection-item grey lighten-3">
        <span class="title">$NAME$</span>
        <a class="modal-trigger" href="#$ID$-modal"><i class="material-icons grey-text" style="vertical-align: middle">more_vert</i></a>
        <div class="secondary-content" style="vertical-align: middle">
          <a name="$ID$_text" class="$COLOR$-text" raw="$IDRAW$" commands='$COMMANDS$' style="font-size:90%;" href="#" onClick="myFunct(null, this.name, 'button', this.getAttribute('raw'), this.getAttribute('commands'))">$TEXT$</a>
        </div>
      </li>
    </ul>
    <div id="$ID$-modal" class="modal modal-fixed-footer" style="height:100%; overflow-y:hidden">
      <div class="modal-content center grey-text scroll-wrapper">
        <h4>$NAME$</h4>
        <embed src="/devices/views/$IDRAW$" width="100%" height="85%" />
      </div>
      <div class="modal-footer">
        <a href="#!" class=" modal-action modal-close waves-effect waves-green btn-flat">Close</a>
      </div>
    </div>
  '''

  name = config.get('name')
  deviceIDRaw = config.get('id')
  deviceID = config.get('id').replace('-',"__")
  button = config.get('dash_view').get('button')
  command = button.get('command')
  color = button.get('color')
  text = button.get('text')


  generated_text = deviceTemplate.replace('$ID$', 'D_' + str(deviceID)).replace('$NAME$', name).replace('$IDRAW$',deviceIDRaw).replace('$COMMANDS$', json.dumps(command)).replace('$TEXT$',text).replace('$COLOR$', color)

  return generated_text



