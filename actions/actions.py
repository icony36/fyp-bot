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

class ActionDefaultFallback(Action):

    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        text = tracker.latest_message['text']
        
        if (detect(text) != "en"):
            dispatcher.utter_message(response="utter_english_only")
            return [UserUtteranceReverted()]
        
        print(server_endpoint)
        print(google_api_key)

        try:
            reply_text = ""

            responses = chat.send_message(text, stream=True)

            for chunk in responses:
                reply_text += chunk.text
            
            dispatcher.utter_message(text=reply_text)
        except Exception as e:
            print(e)
            
            dispatcher.utter_message(response="utter_cant_answer")


        return [UserUtteranceReverted()]


class ActionGetKnowLedges(Action):

    def name(self) -> Text:
        return "action_get_knowledges"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        knowledge = next(tracker.get_latest_entity_values("knowledge"), None)

        if knowledge != None:
            url = f'{server_endpoint}api/knowledges/search?search={knowledge}'
            res = requests.get(url)

            results = res.json().get('data');

            if len(results) > 0:
                dispatcher.utter_message(text=f"Here is the information regarding {knowledge}.\n")
                dispatcher.utter_message(text=results[0]['description'])
            else:
                dispatcher.utter_message(text="I can't find the information of it. Can you try something else?")
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
            dispatcher.utter_message(text="You may check your ticket in your profile page.")
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