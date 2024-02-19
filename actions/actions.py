from typing import Any, Text, Dict, List
import os
from dotenv import load_dotenv

from langdetect import detect, detect_langs
import google.generativeai as genai

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted, SlotSet, FollowupAction

import requests

load_dotenv()

# server_endpoint = "http://localhost:3210/"
# server_endpoint = "https://fyp-server-b4yk.onrender.com/"
server_endpoint = os.getenv("SERVER_ENDPOINT")
google_api_key = os.getenv("GOOGLE_API_KEY")

# genai.configure(api_key="AIzaSyBSKfve9GwoZeFQaQCIK4qiw96nosZk3ac")
genai.configure(api_key=google_api_key)
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def ask_google(dispatcher, text):
    try:
        reply_text = ""

        ask_text = text + " Just to inform you, I am a university student and presently situated in Singapore."

        responses = chat.send_message(ask_text, stream=True)

        for chunk in responses: 
            new_text = chunk.text.replace("\n\n", "\n \n") 
            reply_text += new_text

        dispatcher.utter_message(text=reply_text)
    except Exception as e:
        print(e)
        
        dispatcher.utter_message(response="utter_cant_answer")

class ActionDefaultFallback(Action):

    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        text = tracker.latest_message['text']

        # if (detect(text) != "en"):
        #     dispatcher.utter_message(response="utter_english_only")
        #     return [UserUtteranceReverted()]
        
        print(server_endpoint)
        print(google_api_key)

        ask_google(dispatcher, text)

        return [UserUtteranceReverted()]

class ActionGetTimetable(Action):
    def name(self) -> Text:
        return "action_get_timetable"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        url = f'{server_endpoint}api/student-profiles/by-user/{tracker.sender_id}'
        res = requests.get(url)

        results = res.json().get('data');

        if results is not None:
            dispatcher.utter_message(text="Here is your timetable.")

            reply_str = ""

            for time in results["timetable"]:
                temp = f'{time["moduleId"]} {time["moduleName"]} {time["lessonType"]} {time["location"]} {time["date"]} {time["time"]} \n'
                reply_str += temp + " \n"
            
            dispatcher.utter_message(text=reply_str)
            dispatcher.utter_message(text="You may also check your timetable on your profile page.")
        else:
            dispatcher.utter_message(text="Can't retrieve your student id")

        return []

class ActionGetFee(Action):
    def name(self) -> Text:
        return "action_get_fee"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        url = f'{server_endpoint}api/student-profiles/by-user/{tracker.sender_id}'
        res = requests.get(url)

        results = res.json().get('data');

        if results != None:
            dispatcher.utter_message(text="Here is your outstanding fee.")
            dispatcher.utter_message(text=f'$ {results["outstandingFee"]}')
            dispatcher.utter_message(text="You may also check your outstanding fee on your profile page.")
        else:
            dispatcher.utter_message(text="Can't retrieve your student id")

        return []

class ActionGetCareerPath(Action):
    def name(self) -> Text:
        return "action_get_career_path"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        url = f'{server_endpoint}api/student-profiles/by-user/{tracker.sender_id}'
        res = requests.get(url)

        results = res.json().get('data');

        course = next(tracker.get_latest_entity_values("course"), None)

        text = tracker.latest_message['text']

        if results is not None and course is None:
            text += f' {results["course"]}'

        ask_google(dispatcher, text)

        return []

class ActionGetStudentId(Action):
    def name(self) -> Text:
        return "action_get_student_id"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text=f"Your student ID is {tracker.sender_id}.")

        return []


class ActionGetKnowLedges(Action):

    def name(self) -> Text:
        return "action_get_knowledges"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        knowledge = next(tracker.get_latest_entity_values("knowledge"), None)

        if knowledge is not None:
            url = f'{server_endpoint}api/knowledges/search?search={knowledge}'
            res = requests.get(url)

            results = res.json().get('data');

            if len(results) > 0:
                dispatcher.utter_message(text=f"Here is the information regarding {knowledge}.\n")
                dispatcher.utter_message(text=results[0]['description'])
            else:
               ask_google(dispatcher, tracker.latest_message['text'])
        else:
            return [FollowupAction('action_default_fallback')]      

        return []

class SubmitTicketForm(Action):

    def name(self) -> Text:
        return "submit_ticket_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        to_submit = {
            "studentId": tracker.sender_id,
            "subject": tracker.get_slot("ticket_subject"),
            "detail":  tracker.get_slot("ticket_detail")
        }

        try:
            url = f"{server_endpoint}api/tickets"
            res = requests.post(url, json=to_submit)
            res.raise_for_status()
            dispatcher.utter_message(text="The ticket is created!")
            dispatcher.utter_message(text="You may check your ticket in your tickets page.")
        except requests.exceptions.HTTPError as err:
            print(err)
            
            results = res.json().get('message')
            if results is not None:
                dispatcher.utter_message(text=results)
            else:
                dispatcher.utter_message(text="Network error occured. Please try again later.")
         

        return [SlotSet("ticket_subject", None), SlotSet("ticket_detail", None)]

class CancelTicketForm(Action):

    def name(self) -> Text:
        return "cancel_ticket_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        return [SlotSet("ticket_subject", None), SlotSet("ticket_detail", None)]
    
class ActionMapDirection(Action):

    def name(self) -> Text:
        return "action_map_direction"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        link = "https://map-viewer.situm.com/?apikey=b48aeb58c2a605532de776ee5dedfefc778ca5b242f3d1c56986044c2baddb93&domain=&lng=en&buildingid=15400&floorid=49585"
     
        dispatcher.utter_message(text="You may use the following link to get the direction to your destination.")
        dispatcher.utter_message(text=link)
        dispatcher.utter_message(text="You can simply enter your starting point and destination in the directions app and it will calculate the best route for you.")
        
        return []

class ActionCampusDirection(Action):
    def name(self) -> Text:
        return "action_campus_direction"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        

        link = "https://www.google.com/maps/dir//SIM+Global+Education+461+Clementi+Rd+Singapore+599491/@1.3294012,103.7761745,15z/"
        

        dispatcher.utter_message(response="utter_campus_located")
        dispatcher.utter_message(text="You may use the following link to get the direction to the school.")
        dispatcher.utter_message(text=link)
        dispatcher.utter_message(text="You can simply enter your starting point in the directions app and it will calculate the best route for you. ")


        return []