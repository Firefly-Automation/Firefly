# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-10-09 21:48:29
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-09 22:40:08
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

class Scheduler(object):
  def __init__(self):
    self._scheduler = BackgroundScheduler()
    self._scheduler.start()

  def runCron(self, function, minute=None, hour=None, day=None, month=None, day_week=None, year=None, job_id=None, args=[], kwargs={}):
    if job_id is None:
      job_id=str(function)
    logging.info('adding cron job: {}'.format(str(job_id)))
    self._scheduler.add_job(function, 'cron', args=args, kwargs=kwargs, minute=minute, hour=hour, day=None, month=month, day_of_week=day_week, year=year, id=job_id)

  def runEveryS(self,delay, function, args=[], kwargs={}, job_id=None, replace=True):
    if job_id is None:
      job_id=str(function)
    logging.info('runEveryS job: {}'.format(str(job_id)))
    self._scheduler.add_job(function, 'interval', seconds=delay, args=args, kwargs=kwargs, id=job_id, replace_existing=replace)

  def runEveryM(self,delay, function, args=[], kwargs={}, job_id=None, replace=True):
    if job_id is None:
      job_id=str(function)
    logging.info('runEveryM job: {}'.format(str(job_id)))
    self._scheduler.add_job(function, 'interval', minutes=delay, args=args, kwargs=kwargs, id=job_id, replace_existing=replace)

  def runEveryH(self,delay, function, args=[], kwargs={}, job_id=None, replace=True):
    if job_id is None:
      job_id=str(function)
    logging.info('runEveryH job: {}'.format(str(job_id)))
    self._scheduler.add_job(function, 'interval', hours=delay, args=args, kwargs=kwargs, id=job_id, replace_existing=replace)

  def runInS(self,delay, function, args=[], kwargs={}, job_id=None, replace=True):
    if job_id is None:
      job_id=str(function)
    logging.info('runInS job: {}'.format(str(job_id)))
    run_time = datetime.now() + timedelta(seconds=delay)
    self._scheduler.add_job(function, 'date', run_date=run_time, args=args, kwargs=kwargs, id=job_id, replace_existing=replace)

  def runInM(self,delay, function, args=[], kwargs={}, job_id=None, replace=True):
    if job_id is None:
      job_id=str(function)
    logging.info('runInM job: {}'.format(str(job_id)))
    run_time = datetime.now() + timedelta(minutes=delay)
    self._scheduler.add_job(function, 'date', run_date=run_time, args=args, kwargs=kwargs, id=job_id, replace_existing=replace)

  def runInH(self,delay, function, args=[], kwargs={}, job_id=None, replace=True):
    if job_id is None:
      job_id=str(function)
    logging.info('runInH job: {}'.format(str(job_id)))
    run_time = datetime.now() + timedelta(hours=delay)
    self._scheduler.add_job(function, 'date', run_date=run_time, args=args, kwargs=kwargs, id=job_id, replace_existing=replace)

  def cancel(self, job_id):
    logging.info('canceling job: {}'.format(str(job_id)))
    self._scheduler.remove_job(job_id)


