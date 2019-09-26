from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import getLogger
import time
from os.path import dirname, join
from datetime import datetime, timedelta
from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.parse import extract_datetime, normalize
from mycroft.util.time import now_local
from mycroft.util.format import nice_time, nice_date
from mycroft.util.log import LOG
from mycroft.util import play_wav
from mycroft.messagebus.client import MessageBusClient


__author__ = 'Paula Braeuer'
LOGGER = getLogger(__name__)

REMINDER_PING = join(dirname(__file__), 'twoBeep.wav')

MINUTES = 60  # seconds


def deserialize(dt):
    return datetime.strptime(dt, '%Y%d%m-%H%M%S-%z')


def serialize(dt):
    return dt.strftime('%Y%d%m-%H%M%S-%z')


def is_today(d):
    return d.date() == now_local().date()


def is_tomorrow(d):
    return d.date() == now_local().date() + timedelta(days=1)


def contains_datetime(utterance, lang='en-us'):
    return extract_datetime(utterance)[1] != normalize(utterance)


def is_affirmative(utterance, lang='en-us'):
    affirmatives = ['yes', 'sure', 'please do']
    for word in affirmatives:
        if word in utterance:
            return True
    return False

class MemoryBoxSkill(MycroftSkill):

    def get_user_response(self, dialog):
        response = self.get_response(dialog)
        return response

    @intent_handler(IntentBuilder("").require("hello"))
    def handle_knock_knock_intent(self, message):# They said help me
        #say hello and ask for name
        name = self.get_user_response("hello")
        #got name from user and ask what to do next
        choosenOption = self.get_response("HelloNameTellOptions", data={'username': name}) 

        exerciseAnswer = ['I want to do my exercises', 'do my exercies', 'exercises']
        timerAnswers = ['tell me the next reminder', 'reminder', 'the next reminder', 'next reminder']
        helpAnswers = ['can you tell me the options again?', 'what can I do?']

        if choosenOption in exerciseAnswer:
            self.speak_dialog("here comes an exercise")
        elif choosenOption in timerAnswers:
            self.speak_dialog("here comes a timer")
        elif choosenOption in helpAnswers:
            self.speak_dialog("I can help you")


def create_skill():
    return MemoryBoxSkill()


