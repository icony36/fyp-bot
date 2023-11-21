from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted



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
            resText = f"Here is the information regarding [{query}]."
        else:
            resText = f"I can't find the information of it. Can you try something else?"

        dispatcher.utter_message(text=resText)

        return []

