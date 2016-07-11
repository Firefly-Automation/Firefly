# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-05-22 14:40:40
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-06-27 19:48:12

import collections
import json


def dash_generator(devices):
  returnData = {}
  devices = collections.OrderedDict(sorted(devices.iteritems(), key=lambda elem: elem[1]['name']))
  for device, config in devices.iteritems():
    if config.get('name') is not None:
      if config.get('dash_view').get('type') == "button":
        returnData[config.get('name')] = generate_button(config)

  returnData = collections.OrderedDict(sorted(returnData.items()))
  return returnData

def refresh_generator():
  refreshJS = '''
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
          console.log(deviceID)
          console.log(status)

          window[ deviceID ](status, false)
        }
      }
    }
  }

  '''
  return refreshJS

def generate_button(config):
  deviceTemplate = '''
  <div class="col s12 m6 l4">
    <div class="card-panel grey darken-1 hoverable" style="padding:0px; height: 65px">
    <table>
    <tbody>
      <tr>
        <td>
          <span class="white-text" style="padding-left:10px">$NAME$</span>
        </td>
        <td style="width:10%; padding: 10px">
          $BUTTONS$
        </td>
        <td style="width:10%">
          <a class="modal-trigger" href="#$ID$-modal"><i class="material-icons right-align white-text" style="font-size: 35px;">more_vert</i></a>
        </td>
      </tr>
      </tbody>
      </table>
      <div id="$ID$-modal" class="modal">
          <div class="modal-content center grey-text">
            <h4>$NAME$</h4>
            <embed src="/devices/views/$IDRAW$" width="100%" />
          </div>
          <div class="modal-footer">
            <a href="#!" class=" modal-action modal-close waves-effect waves-green btn-flat">Close</a>
          </div>
          <script>
            $JAVASCRIPT$
          </script>
        </div>
    </div>
  </div>
  '''
  buttonTemplate = '''<a id="$ID$-$VALUE$" name="$ID$-$VALUE$" class="waves-effect waves-light btn $COLOR$" onClick="$ID$('$CLICK$', true)" style="display:$DISPLAY$; padding: 0px; width: 65px; font-size: 15px">$TEXT$</a>'''

  jsTemplate = '''
  function $ID$(value, send){
    if (value =="on") {
    console.log("Turn On")
    document.getElementById("off").style.display = 'none'
    document.getElementById("on").style.display = ''
    } else if (value =="off") {
    console.log("Turn Off")
    document.getElementById("off").style.display = ''
    document.getElementById("on").style.display = 'none'
    }
  }
  '''

  name = config.get('name')
  deviceIDRaw = config.get('id')
  deviceID = config.get('id').replace('-',"__")
  buttons = config.get('dash_view').get('button')


  print name
  generated_buttons = []
  for b, c in buttons.iteritems():
    #print b
    #print c
    color = c.get('color')
    text = c.get('text')
    click = c.get('click')
    display = '' if c.get('default') else 'none'
    generated_buttons.append(buttonTemplate.replace('$ID$', 'D_' + str(deviceID)).replace('$VALUE$', b).replace('$COLOR$', color).replace('$CLICK$',click).replace('$TEXT$', text).replace('$DISPLAY$',display).replace('$IDRAW$',deviceIDRaw))


  buttonOptions = buttons.keys()

  jsInner = []
  jsInner.append("function " + 'D_' + str(deviceID) + "(value, send){")
  jsInner.append("              console.log(\""+'D_' + str(deviceID)+" Function \" + value)")
  for b, c in buttons.iteritems():
    click = c.get('click')
    command = c.get('command')
    jsInner.append("              if (value == \"" + str(click) + "\"){")
    command = {'device':deviceIDRaw, 'command': command}
    jsInner.append('''                if (send){''')
    jsInner.append('''                  var form = "command=''' + json.dumps(command).replace("\"","\\\"") + '''";''')
    jsInner.append('''                  var url = "/API/translator2"''')
    jsInner.append('''                  console.log(url)''')
    jsInner.append('''                  $.post(url, form);''')
    jsInner.append('''                 }''')
    for o in buttonOptions:
      if o == click:
        jsInner.append("                var n = document.getElementsByName(\""+'D_' + str(deviceID) + "-" + click+"\")")
        jsInner.append("                for (i=0; i< n.length; i++){")
        jsInner.append("                  n[i].style.display = ''")
        jsInner.append("                }")
      else:
        jsInner.append("                var n = document.getElementsByName(\""+'D_' + str(deviceID) + "-" + o+"\")")
        jsInner.append("                for (i=0; i< n.length; i++){")
        jsInner.append("                  n[i].style.display = 'none'")
        jsInner.append("                }")
    jsInner.append("              }")
  jsInner.append("            }")
    
  jsInner = "\n".join(jsInner)

  buttonsString = "".join(generated_buttons)
  generated_button = deviceTemplate.replace('$ID$', 'D_' + str(deviceID)).replace('$NAME$', name).replace('$BUTTONS$',buttonsString).replace('$JAVASCRIPT$',jsInner).replace('$IDRAW$',deviceIDRaw)

  return generated_button



