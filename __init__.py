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

yes = ['yes', 'sure', 'please do', 'ready', 'sounds good', 'ok', 'alright', 'Yes, I would like to', 'yes yes i would', 'yes please']
no = ['no', 'nop', 'Dont want to', 'no i Dont want to', 'not now', 'not really', 'no thank you']

class MemoryBoxSkill(MycroftSkill):

    def get_user_response(self, dialog):
        response = self.get_response(dialog)
        return response

    @intent_handler(IntentBuilder("").require("hello"))
    def handle_knock_knock_intent(self, message):# They said memory box
        
        #say hello and ask for name
        name = self.get_user_response("hello")
        #got name from user and ask what to do next

        choosenOption = self.get_response("HelloNameTellOptions", data={'username': name})
        self.choose_option(choosenOption, name)


    def choose_option(self, choosenOption, name):

        exerciseAnswer = ['I want to do my exercises', 'do my exercises', 'do my exercise', ' do my exercises with me', 'exercise', 'exercises', 'my exercises', 'the first one', 'i would like to do my exercises', 'practice my exercises']
        reminderAnswers = ['tell me the next reminder', 'reminder', 'the next reminder', 'next reminder', 'memory box reminder', 'pill reminder', 'pill intake', 'tell me the pill intake', 'reminders', 'tell me my reminder']
        helpAnswers = ['can you tell me the options again?', 'what can I do?', 'what', 'None']

        if choosenOption in exerciseAnswer:
            doExercise = self.get_response("exercise", data={'username': name})
            self.do_exercise(doExercise, name)
        elif choosenOption in reminderAnswers:
            #self.get_next_reminder(self.get_response("getTimerForWhichDate"))
            self.speak_dialog("today at 4 pm you should do your hand movement exercise.")
            self.speak_dialog("And you should take your Celebrex on Mondays, Wednesdays and Fridays.")
            self.speak_dialog("Today is Wednesday, so don't forget it.")
            repeat = self.get_response("Would you like me to repeat the information?")
            if repeat in yes:
                self.choose_option(choosenOption, name)
            elif repeat in no:
                self.speak_dialog("I will remind you five minutes before the scheduled time.")
                returnToSchedul = self.get_response("Would you like to return to the schedule information?")
                if returnToSchedul in yes:
                    choosenOption = self.get_response("HelloNameTellOptions", data={'username': name})
                    self.choose_option(choosenOption, name)
                elif returnToSchedul in no:
                    self.speak_dialog("byebye", data={'username': name})
        elif choosenOption in helpAnswers:
            choosenOption = self.get_response("Do you want to do your exercises or get your reminders?")

    def do_exercise(self, doExercise, name):
        if doExercise in yes:
            goOnExer= self.get_response("firstStepExer")
            self.go_on_exercise(goOnExer)
        elif doExercise in no:
            choosenOption = self.get_response("so what about doing your exercises or do you want to know when you have to take your pills again?")
            self.choose_option(choosenOption, name)
            #self.do_exercise(doExercise)

    def go_on_exercise(self, goOnExer):
        if  goOnExer in yes:
            self.speak_dialog("secondStepExer")
        elif goOnExer in no:
            self.speak_dialog("so please find a place and start again")

    @intent_file_handler('StartExerciseAgain.intent')
    def start_exer_again(self):
        self.do_exercise(doExercise, name)


def create_skill():
    return MemoryBoxSkill()


