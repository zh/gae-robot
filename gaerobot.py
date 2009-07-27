#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from waveapi import events
from waveapi import model
from waveapi import robot

from pyactiveresource.activeresource import ActiveResource

import logging
import settings

CC_XMPP = 'cc:xmpp'
CC_TWITTER = 'cc:twitter'

logger = logging.getLogger('GAE_Robot')
logger.setLevel(logging.INFO)

class Notification(ActiveResource):
      _site = settings.MPUB_SITE

### Webhooks start
def OnParticipantsChanged(properties, context):
  """Invoked when any participants have been added/removed."""
  added = properties['participantsAdded']
  for p in added:
    if p != 'gae-robot@appspot.com':
      Notify(context, "Hi, " + p)


def OnRobotAdded(properties, context):
  """Invoked when the robot has been added."""
  root_wavelet = context.GetRootWavelet()
  root_wavelet.CreateBlip().GetDocument().SetText("Connected to XMPP...")


def OnBlipSubmitted(properties, context):
  """Invoked when new blip submitted."""
  blip = context.GetBlipById(properties['blipId'])
  doc = blip.GetDocument()
  text = doc.GetText()
  try:
    if text != '':
      if CC_XMPP in text:
        text = text.replace('cc:xmpp','')
        note = Notification({'escalation':10, 'body':text, 'recipients':{'recipient':[{'position':1,'channel':'gchat','address':settings.MPUB_XMPP}]}})
        note.save()
      if CC_TWITTER in text:
        text = text.replace('cc:twitter','')
        note = Notification({'escalation':10, 'body':text, 'recipients':{'recipient':[{'position':1,'channel':'twitter','address':settings.MPUB_TWITTER}]}})
        note.save()
  except:
    logger.debug(context, 'Submit failed. (blip=%s)' % properties['blipId'])
    pass
  

### Webhooks end

def Notify(context, message):
  root_wavelet = context.GetRootWavelet()
  root_wavelet.CreateBlip().GetDocument().SetText(message)


if __name__ == '__main__':
  myRobot = robot.Robot('gae-robot', 
      image_url='http://gae-robot.appspot.com/assets/bot.png',
      version='1',
      profile_url='http://gae-robot.appspot.com/')
  myRobot.RegisterHandler(events.WAVELET_PARTICIPANTS_CHANGED, OnParticipantsChanged)
  myRobot.RegisterHandler(events.WAVELET_SELF_ADDED, OnRobotAdded)
  myRobot.RegisterHandler(events.BLIP_SUBMITTED, OnBlipSubmitted)
  myRobot.Run(debug=settings.DEBUG)
