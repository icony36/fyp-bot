from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted

import requests


class ActionTwoStageFallback(Action):

    def name(self) -> Text:
        return "action_two_stage_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(response="utter_ask_rephrase")

        return [UserUtteranceReverted()]

class ActionFAQ(Action):

    def name(self) -> Text:
        return "action_faq"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        query = next(tracker.get_latest_entity_values("query"), None)

        if query != None:
            # api_endpoint = f'https://fyp-server-b4yk.onrender.com/api/knowledges/search?search={query}'
            api_endpoint = f'http://localhost:3210/api/knowledges/search?search={query}'
            res = requests.get(api_endpoint)

            results = res.json().get('data');

            if len(results) > 0:
                dispatcher.utter_message(text=f"Here is the information regarding {query}.\n")
                dispatcher.utter_message(text=results[0]['description'])
            else:
                dispatcher.utter_message(text=f"I can't find the information of it. Can you try something else?")
        else:
             dispatcher.utter_message(text=f"I can't get it. Can you rephrase it?")

        return []

