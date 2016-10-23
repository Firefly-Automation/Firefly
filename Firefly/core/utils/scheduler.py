# -*- coding: utf-8 -*-
# @Author: Zachary Priddy
# @Date:   2016-10-09 21:48:29
# @Last Modified by:   Zachary Priddy
# @Last Modified time: 2016-10-14 17:17:51
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from datetime import timedelta

DAYS_OF_WEEK = ['mon','tue','wed','thu','fri','sat','sun']

class Scheduler(object):
  def __init__(self):
    self._scheduler = BackgroundScheduler()
    self._scheduler.start()

  def runCron(self, function, minute=None, hour=None, day=None, month=None, day_week=None, year=None, job_id=None, args=[], kwargs={}):
    if job_id is None:
      job_id=str(function)
    logging.info('adding cron job: {}'.format(str(job_id)))
    self._scheduler.add_job(function, 'cron', args=args, kwargs=kwargs, minute=minute, hour=hour, day=None, month=month, day_of_week=day_week, year=year, id=job_id, replace_existing=True)

  #TODO: Build cron class
  def runSimpleWeekCron(self, function, minute=None, hour=None, days_of_week=None, job_id=None, args=[], kwargs={}):
    '''days_of_week takes a list of days'''
    if job_id is None:
      job_id=str(function)
    if days_of_week is not None and days_of_week != '*':
      run_days = []
      for d in DAYS_OF_WEEK:
        if d in days_of_week:
          run_days.append(d)
      days_of_week = ','.join(run_days)
    logging.info('adding simple weekly cron job: {}'.format(str(job_id)))
    self._scheduler.add_job(function, 'cron', args=args, kwargs=kwargs, minute=minute, hour=hour, day='*', month='*', day_of_week=days_of_week, year='*', id=job_id, replace_existing=True)


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

  def runAt(self, date, function, args=[], kwargs={}, job_id=None, replace=True):
    if job_id is None:
      job_id=str(function)
    logging.info('runAt job: {} date: {}'.format(str(job_id),str(date)))
    self._scheduler.add_job(function, 'date', run_date=date, args=args, kwargs=kwargs, id=job_id, replace_existing=replace)

  def cancel(self, job_id):
    try:
      logging.info('canceling job: {}'.format(str(job_id)))
      self._scheduler.remove_job(job_id)
      return True
    except:
      return False


