# /usr/bin/python
# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-04-11 09:00:14
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-12 22:51:35
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import logging
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='%(asctime)s %(levelname)s {%(module)s} [%(funcName)s] %(message)s', datefmt='%Y-%m-%d,%H:%M:%S', level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


from core import firefly_api

if __name__ == "__main__":
  #firefly_api.run()
  from core import firefly
  firefly.run()