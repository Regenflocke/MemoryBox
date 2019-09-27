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
        self.choose_option(choosenOption, name)


    def choose_option(self, choosenOption, name):

        exerciseAnswer = ['I want to do my exercises', 'do my exercises', 'do my exercise', 'exercise', 'exercises', 'my exercises']
        reminderAnswers = ['tell me the next reminder', 'reminder', 'the next reminder', 'next reminder', 'memory box reminder']
        helpAnswers = ['can you tell me the options again?', 'what can I do?', '']

        if choosenOption in exerciseAnswer:
            doExercise = self.get_response("exercise", data={'username': name})
            self.do_exercise(doExercise, name)
        elif choosenOption in reminderAnswers:
            self.get_next_reminder(self.get_response("getTimerForWhichDate"))
        elif choosenOption in helpAnswers:
            choosenOption = self.get_response("Do you want to do your exercises or get the next reminder?")

    def do_exercise(self, doExercise, name):
        if doExercise == 'yes':
            goOnExer= self.get_response("firstStepExer")
            self.go_on_exercise(goOnExer)
        elif doExercise == 'no':
            choosenOption = self.get_response("so what about doing your exercises or do you want to know when you have to take your pills again?")
            self.choose_option(choosenOption, name)
            #self.do_exercise(doExercise)

    def go_on_exercise(self, goOnExer):
        if  goOnExer == 'yes':
            self.speak_dialog("secondStepExer")
        elif goOnExer == 'no':
            self.speak_dialog("so please finde a place and start again")

    @intent_file_handler('GetRemindersForDay.intent')
    def get_reminders_for_day(self, msg=None):
        """ List all reminders for the specified date. """
        if 'date' in msg.data:
            date, _ = extract_datetime(msg.data['date'], lang=self.lang)
        else:
            date, _ = extract_datetime(msg.data['utterance'], lang=self.lang)

        if 'reminders' in self.settings:
            reminders = [r for r in self.settings['reminders']
                         if deserialize(r[1]).date() == date.date()]
            if len(reminders) > 0:
                for r in reminders:
                    reminder, dt = (r[0], deserialize(r[1]))
                    self.speak(reminder + ' at ' + nice_time(dt))
                return
        self.speak_dialog('NoUpcoming')

    def get_next_reminder(self, msg=None):
        """ Get the first upcoming reminder. """
        if len(self.settings.get('reminders', [])) > 0:
            reminders = [(r[0], deserialize(r[1]))
                         for r in self.settings['reminders']]
            next_reminder = sorted(reminders, key=lambda tup: tup[1])[0]

            if is_today(next_reminder[1]):
                self.speak_dialog('NextToday',
                                  data={'time': nice_time(next_reminder[1]),
                                        'reminder': next_reminder[0]})
            elif is_tomorrow(next_reminder[1]):
                self.speak_dialog('NextTomorrow',
                                  data={'time': nice_time(next_reminder[1]),
                                        'reminder': next_reminder[0]})
            else:
                self.speak_dialog('NextOtherDate',
                                  data={'time': nice_time(next_reminder[1]),
                                        'date': nice_date(next_reminder[1]),
                                        'reminder': next_reminder[0]})
        else:
            self.speak_dialog('NoUpcoming')

def create_skill():
    return MemoryBoxSkill()


