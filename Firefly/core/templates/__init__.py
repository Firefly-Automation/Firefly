# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-12 13:33:30
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-04-12 13:33:30


class Templates(object):
  def __init__(self):
    self._filepath = 'core/templates/'
    self._switch_template = self.get_template('switch')

  def get_template(self, template):
    with open('%s%s.html' % (self._filepath, template)) as template_file:
      return template_file.read().replace('\n', '')

  @property
  def switch(self):
    """
    Builds a switch template from switch.html.

    Returns:
      template (str): string of switch template
    """
    return self._switch


ffTemplates = Templates()
