from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted, SlotSet

import requests

api_endpoint = "http://localhost:3210/"
# api_endpoint = "https://fyp-server-b4yk.onrender.com/"

class ActionDefaultFallback(Action):

    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(response="utter_rephrase")

        return [UserUtteranceReverted()]

class ActionTwoStageFallback(Action):

    def name(self) -> Text:
        return "action_two_stage_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(response="utter_rephrase")

        return [UserUtteranceReverted()]


class ActionGetKnowLedges(Action):

    def name(self) -> Text:
        return "action_get_knowledges"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        knowledge = next(tracker.get_latest_entity_values("knowledge"), None)

        if knowledge != None:
            url = f'{api_endpoint}api/knowledges/search?search={knowledge}'
            res = requests.get(url)

            results = res.json().get('data');

            if len(results) > 0:
                dispatcher.utter_message(text=f"Here is the information regarding {knowledge}.\n")
                dispatcher.utter_message(text=results[0]['description'])
            else:
                dispatcher.utter_message(text="I can't find the information of it. Can you try something else?")
        else:
             dispatcher.utter_message(text="I can't get it. Can you rephrase it?")
       

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
            url = f"{api_endpoint}api/tickets"
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