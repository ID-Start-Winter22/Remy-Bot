# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"



from sys import displayhook
from typing import Any, Text, Dict, List
from pyparsing import nestedExpr

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from . import mvg_nojson
import json

from bs4 import BeautifulSoup
import requests
import re
import time
import random 


# NOTE(Michael): We could use this action to store the name in
#                the TrackerStore (in memory database) or a persitent DB
#                such as MySQL. But we need to store a key-value pair 
#                to identify the user by id eg. (user_id, slotvalue)
class ActionStoreUserName(Action):

     def name(self):
         return "action_store_name"
         
     def run(self, dispatcher, tracker, domain):
        username = tracker.get_slot("username")
        print("Sender ID: ", tracker.sender_id)

        return []


class ActionUserName(Action):

     def name(self):
         return "action_get_name"

     def run(self, dispatcher, tracker, domain):
        username = tracker.get_slot("username")
        if not username :
            dispatcher.utter_message(" Du hast mir Deinen Namen nicht gesagt.")
        else:
            dispatcher.utter_message(' Du bist {}'.format(username))

        return []





class ChefkochParser(Action):

    def name(self):
        return "action_start_parser"

  

    def run(self, dispatcher, tracker, domain):
        zutaten = tracker.get_slot("user_zutaten_liste")
        zeit = tracker.get_slot("user_zeit")
        diaet = tracker.get_slot("user_diaet")
        user_ingredients = "+".join(zutaten)
        

        url = f"https://www.chefkoch.de/rs/s0t32p{zeit}/{user_ingredients}/{diaet}Rezepte.html"

        dispatcher.utter_message(f'Lass mich kurz in meinen Notizen nachschauen...')


        page = requests.get(url).text

        doc = BeautifulSoup( page, 'html.parser')

        page_text = doc.find(class_="recipe-list ds-css-grid ds-css-grid-cols-2 ds-css-grid-cols-sm-3 ds-css-grid-cols-m-4")

        img_list = []
        link_list = []
        all_titles = []

        for img in page_text('img', src=True):
                img_list.append(img['src'])

        for a in page_text('a', href=True):
                link_list.append(a['href'])

        dispatcher.utter_message("Ich hätte hier drei vorschläge für dich:\n")

      

       
        x = 0
        y = 3
        
        
        

        for i in range(x,y):
                title_from_List = link_list[i].split('/')
                title = str(title_from_List[-1])
                final_title = title.replace('.html', '').replace('-', ' ')
                all_titles.append(final_title)
                dispatcher.utter_message(image=f"{img_list[i]}")
                dispatcher.utter_message(text=f"{str(i+1)}. {final_title}")
            
        dispatcher.utter_message(text=f"Welches Rezept möchtest du préparer?")       
                
        

        return [SlotSet("rezept_auswahl", link_list), SlotSet("link_list", link_list), SlotSet("title_liste", all_titles), SlotSet("title_liste_1", str(all_titles[0])), SlotSet("title_liste_2", str(all_titles[1])), SlotSet("title_liste_3", str(all_titles[2]))]
    


class ChefkochParser2(Action):

    def name(self):
        return "action_select_rezept"

    def run(self, dispatcher, tracker, domain):
        
        
        url_liste = tracker.get_slot("link_list")
        nummer = tracker.get_slot("rezept_nummer")
        title = tracker.get_slot("title_liste")
        nummer = int(nummer)

        dispatcher.utter_message(f"Magnifique! Lass uns {title[nummer-1]} kochen")
        
        url = url_liste[nummer-1]
        
        page = requests.get(url).content
        doc = BeautifulSoup(page , 'html.parser')
        
        td_left_list = []
        td_left = doc.find_all('td', class_='td-left')

        for i in td_left:
            td = i.text
            td = td.replace(" ", "")
            td_left_list.append(td)


        td_right_list = []
        td_right = doc.find_all('td', class_='td-right')

        for i in td_right:
            td = i.text
            td = td.replace(" ", "")
            td_right_list.append(td)



        chained_ingredients = []

        for i in range(len(td_left_list)):
            el = td_left_list[i] + td_right_list[i]
            el = " ".join(el.splitlines())
            chained_ingredients.append(el)


        dispatcher.utter_message('Für dein Rezept benötigst du folgende weitere Zutaten:')
        zutaten = "\n".join(chained_ingredients)
        dispatcher.utter_message(f'{zutaten}')

        

       
        return [SlotSet("final_url", url)]

class ChefkochParser3(Action):

    def name(self):
        return "action_execute_rezept"

    def run(self, dispatcher, tracker, domain):
       

        url = tracker.get_slot("final_url")
        username = tracker.get_slot("username")
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')


        zubereitung_trackingpoint = soup.find('h2', {"data-vars-tracking-title" :"Zubereitung"})
        
        zubereitung_block = zubereitung_trackingpoint.find_next('div')
        
        zubereitung_raw = str(zubereitung_block)

        
        zubereitung = zubereitung_raw.replace( '<div class="ds-box">' , '').replace('</div>', '').strip().strip()
        zubereitung_steps =  zubereitung.split('<br/>')
        finale_zubereitung = []
        for i in range(len(zubereitung_steps)):
            if i%2 == 0:
                finale_zubereitung.append(zubereitung_steps[i].strip())
    

        for i in range(len(finale_zubereitung)):

            dispatcher.utter_message(finale_zubereitung[i])
            i += 1

        else:
            dispatcher.utter_message(f'Tres Bien das wars schon!Merci fürs kochen es hat spaß gemacht')
        
        return []


        

