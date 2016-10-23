# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-10-12 22:09:46
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-14 17:08:04
import json
import pickle

from collections import OrderedDict
from core import Routine
from core import routineDB


def getRoutineList():
  routine_list = []
  for r in routineDB.find({}).sort('id'):
    routine_list.append(r.get('id'))
  return routine_list


def getRoutineViewsDict():
  routine_list = []
  for r in routineDB.find({}).sort('id'):
    routine_list.append(dict(r))
  return routine_list


def reinstallRoutinesFromConfig(file):
  routineDB.remove({})
  with open(file) as routines:
    routine = json.load(routines, object_pairs_hook=OrderedDict)
    for r in routine.get('routines'):
      r_object = Routine(json.dumps(r))
      r_binary = pickle.dumps(r_object)
      r['listen'] = r_object.listen
      r['ffObject'] = r_binary
      routineDB.insert(r)
