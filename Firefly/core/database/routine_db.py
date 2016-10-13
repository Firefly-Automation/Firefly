# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-10-12 22:09:46
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-13 13:06:51
from core import routineDB

def getRoutineList():
  routine_list = []
  for r in routineDB.find({}).sort('id'):
    routine_list.append(r.get('id'))
  return routine_list

def getRoutinViewsDict():
  routine_list = []
  for r in routineDB.find({}).sort('id'):
    routine_list.append(dict(r))
  return routine_list