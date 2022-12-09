from typing import Any, Text, Dict, List
import json
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

list_order = []

class ActionHoursFallback(Action):
    def name(self) -> Text:
        return "action_hours_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        data_file = open('opening_hours.json')
        data = json.load(data_file)
        menu_items = data['items']

        day = tracker.get_slot("day_available")
        hour = tracker.get_slot("hour")
        if day and hour:
            if day in data['items']:
                open_hours = data['items'][day]['open']
                closed_hours = data['items'][day]['close']
                if open_hours <= int(hour) <= closed_hours:
                    dispatcher.utter_message("We deliver at this time!")
                else:
                    dispatcher.utter_message("Sorry, we don't deliver at this time")
            else:
                dispatcher.utter_message("Can you repeat your question?")
        elif day:
            if day in data['items']:
                open_hours = data['items'][day]['open']
                closed_hours = data['items'][day]['close']
                dispatcher.utter_message(
                    day + ": \r\n open: " + str(open_hours) + " closed: " + str(closed_hours))
            else:
                dispatcher.utter_message("Can you repeat your question?")
        else:
            for day in menu_items:
                open_hours = data['items'][day]['open']
                closed_hours = data['items'][day]['close']
                dispatcher.utter_message(
                    day + ": \r\n open: " + str(open_hours) + " closed: " + str(closed_hours) )

        return []

class ActionMenuFallback(Action):
    def name(self) -> Text:
        return "action_menu_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        data_file = open('menu.json')
        data = json.load(data_file)
        menu_items = data['items']

        for i, menu_items in enumerate(menu_items):
            text = str(i) + ". " + menu_items['name'] + " - price: " + str(menu_items['price'])
            dispatcher.utter_message(
                text)

        return []

class ActionOrderFallback(Action):
    def name(self) -> Text:
        return "action_order_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        data_file = open('menu.json')
        data = json.load(data_file)
        menu_items = data['items']

        dish = tracker.get_slot("question_dish")
        output = ""
        for i, item in enumerate(menu_items):
            if item['name'] == dish:
                list_order.append(dish)
                output = "Added dish {} with price {}".format(item['name'], str(item['price']))
                break
            else:
                output = "Excuse me, can you repeat which dish you want?"

        dispatcher.utter_message(output)
        return []

class ActionGetOrder(Action):
    def name(self) -> Text:
        return "action_get_order_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        data_file = open('menu.json')
        data = json.load(data_file)
        menu_items = data['items']

        summary = 0
        if not list_order:
            dispatcher.utter_message("Nothing selected to order")
        else:
            output = "You have: "
            for dish in list_order:
                for i, item in enumerate(menu_items):
                    if item['name'] == dish:
                        summary += item['price']
                        output += item['name']
                        output += ", "
            output = output[:-2]
            output += ". Finally price: {}".format(str(summary))
            dispatcher.utter_message(output)
        return []

class ActionBill(Action):
    def name(self) -> Text:
        return "action_get_bill_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not list_order:
            dispatcher.utter_message("You don't order anything!")
        else:
            data_file = open('menu.json')
            data = json.load(data_file)
            menu_items = data['items']
            preparation_time = 0
            for dish in list_order:
                for i, item in enumerate(menu_items):
                    if item['name'] == dish:
                        preparation_time += item['preparation_time']*10

            dispatcher.utter_message("Thank you! Your order will be in {} minutes".format(preparation_time))
            list_order.clear()