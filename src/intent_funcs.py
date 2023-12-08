from datetime import datetime
from urllib.error import HTTPError, URLError
import spacy, csv, os
from joblib import dump, load
from nltk import word_tokenize
import requests, json 
from itertools import cycle
from time import sleep
import threading

class Customer():
    def __init__(self) -> None:
        self.name = ""
        self.DSTlist = []
        self.destination = ""
        self.ORNlist = []
        self.origin = ""
        self.routeInfo = []
    
    def isLoaded(self):
        """
        Checks if both origin and destination information are loaded. 
        """
        return not "" in [self.origin, self.destination]
 
    def askName(self):
        """
        Asks the user's name
        """
        print("Oh, but firstly what is your name?")
        self.name = input("Type your name: ")
        print(f"Nice to meet you, {self.name}.")
    
    def getName(self):
        """
        Returns the user's name
        """
        return self.name
    
    def is_number(self, variable):
        """
        Returns True if the variable is an integer. 
        """
        try:
            int(variable)
            return True # Successfully converted to int, so it's a number
        except ValueError:
            return False   # Conversion to int failed, so it's not a number
    
    def check_input(self, script, expected_range):
        """
        Ask the script to the user and checks if the input is an expected index.
        
        Returns the index if the input is an integer 
        and is in the expected range of the list
        """
        is_number, in_range = False, False
        while not is_number or not in_range:
            index = input(script)
            if self.is_number(index):
                is_number = True
                if int(index) in expected_range:
                    in_range = True
                else:
                    print("You typed in an expected number.")
            if not is_number:
                print("The value you entered was not a number.")
        return index
    
    def extractORNDST(self, text):
        """
        Extracts origin and destination from the text.
        If they are found, returns True.
        """
        nlp_ner = spacy.load("./src/model-last")  # location of your created model

        doc = nlp_ner(text)
        
        found = False
        for ent in doc.ents:
            if ent.label_ == "DST":
                if not found:
                    self.ORNDSTreset()
                self.DSTlist.append(ent.text)
                found = True
            if ent.label_ == "ORN":
                if not found:
                    self.ORNDSTreset()
                self.ORNlist.append(ent.text)
                found = True

        return found

    def getORNDST(self):
        """
        Loads extracted origin and destination to the instance variables.
        """
        if len(self.ORNlist) > 1:
            indexed_origin = {i+1: self.ORNlist[i] for i in range(len(self.ORNlist))}
            print("More than one station names have been detected as your starting station.")
            ornIndex = self.check_input("Which station are you travelling from? Select a number: " + str(indexed_origin) + " ", range(1, len(self.ORNlist)+1))
            self.origin = self.ORNlist[int(ornIndex)-1]
        if len(self.DSTlist) > 1:
            indexed_dst = {i+1: self.DSTlist[i] for i in range(len(self.DSTlist))}
            print("More than one station names have been detected as the station of your destination.")
            dstIndex = self.check_input("Which station are you travelling to? Select a number: " + str(indexed_dst) + " ", range(1, len(self.DSTlist)+1))
            self.destination = self.DSTlist[int(dstIndex)-1]
        if len(self.ORNlist) == 1:
            self.origin = self.ORNlist[0]
        if len(self.DSTlist) == 1:
            self.destination = self.DSTlist[0]
        if len(self.ORNlist) == 0:
            print("I could not recognise the name of the station you are travelling from.")
            self.origin = input("Please type in the name of the station you are travelling from: ")
        if len(self.DSTlist) == 0:
            print("I could not recognise the name of the station you are travelling to.")
            self.origin = input("Please type in the name of the station you are travelling to: ")

        """
        confirmation = input("I see you want to go to " + self.destination + " from " + self.origin + ". Is it correct?: ")

        if not confirmation in ["Yes", "Yep", "Correct", "Yes." "Yes!"]:
            self.ORNDSTreset()
            text = input("Please type in where you are going from and to.")
            self.getORNDST(text)
        """

    def ORNDSTreset(self):
        """
        Resets user's starting point and destination information
        """
        self.DSTlist = []
        self.destination = ""
        self.ORNlist = []
        self.origin = ""
        self.routeInfo = []
    
    def getStopPoint(self, intent):
        """
        Sends a request to API and get a list of stop points. 
        When sucessful, dictionary of origins and destinations and status 200 are returned. 
        Otherwise, or if no stations that matche the original are found, None and 404 are returned.
        """
        # API returns nothing when the query contains 'station' so escape
        originalValues = {"destinations": self.destination, "origins": self.origin}
        self.destination = self.destination.lower().replace(" station","").replace(" ", "%20")
        self.origin = self.origin.lower().replace(" station","").replace(" ", "%20")
        
        if intent == "SearchRoute":
            mode = "bus,overground,national-rail,tube,dlr,tram,walking"
        if intent == "SearchFare":
            mode = "tube"
        
        map = {"origins": self.origin, "destinations": self.destination}
        for key, stopPoint in map.items():
            url = f"https://api.tfl.gov.uk/StopPoint/Search/{stopPoint}?modes={mode}&includeHubs=False"
            response = self.sendRequest(url)
            if response.status_code != 200:
                print(f"I could not find a station or a stop that matches '{originalValues[key]}'. Please start again.")
                return None, 404
            else:
                data = response.json()
                matches = data["matches"]
                if not matches:
                    print(f"I could not find a station or a stop that matches '{originalValues[key]}'. Please start again.")
                    return None, 404
                map[key] = {j+1: {
                    "commonName": match["name"],
                    "availableModes": match["modes"],
                    "naptanId": match["id"]
                } for j, match in enumerate(matches)}
        
        return map, 200
        
    def disambiguate(self, map):
        """
        Asks the user to disambiguate their destination and starting point, 
        and then finalises the content of self.destination and self.origin
        """
        o, d = len(map["origins"]), len(map["destinations"])
        if o > 1 or d > 1:
            print("There are multiple stations and stops available around the locations you provided.")
        if o > 1:
            print("Choose the number of the station or the stop from which you are departing from the list below")
            for i, item in map["origins"].items():
                name = item["commonName"]
                modes = ", ".join(item["availableModes"])
                print(f"{i}. {name} (Available modes of transport: {modes})")
            
            originIndex = self.check_input("Select a number: ", range(1, o+1))
        else:
            originIndex = 1
        
        if d > 1:
            print("Choose the number of the station or the stop to which you are going from the list below")
            for i, item in map["destinations"].items():
                name = item["commonName"]
                modes = ", ".join(item["availableModes"])
                print(f"{i}. {name} (Available modes of transport: {modes})")
            
            dstIndex = self.check_input("Select a number: ", range(1, d+1))
        else:
            dstIndex = 1
        
        self.origin = map["origins"][int(originIndex)]["naptanId"]
        self.destination = map["destinations"][int(dstIndex)]["naptanId"]

    def sendRequest(self, url):
        """
        Sends a request and returns the response with a loading animation.
        """
        done = False
        def animate():
            n_points = 5
            points_l = ['.' * i + ' ' * (n_points - i) + '\r' for i in range(n_points)]
            for points in cycle(points_l):
                print(points, end='')
                sleep(0.1)
                if done:
                    break

        t = threading.Thread(target=animate)
        t.start()

        response = requests.get(url)
        done = True

        return response
            
    def getRoute(self):
        """
        Sends a request to API and get the journey result.
        When successful, it outputs the best result.
        Otherwise, None and 404 are returned.
        """
        base_url = "https://api.tfl.gov.uk/Journey/JourneyResults"
        endpoint = f"{self.destination}/to/{self.origin}"
        mode = "bus,overground,national-rail,tube,dlr,tram,walking"
        journeyPreference = "LeastInterchange"
        walkSpeed = "Slow"
        url = f"{base_url}/{endpoint}?timeIs=Departing&journeyPreference={journeyPreference}&mode={mode}&accessibilityPreference=NoRequirements&walkingSpeed={walkSpeed}&cyclePreference=None&bikeProficiency=Easy"
          
        response = self.sendRequest(url)
        if response.status_code == 200:
            json = response.json()
        else:
            print("Sorry, I could not find a route...")
            return None, 404
        
        output = "OK, the best route is as follows: "
        best_journey = json["journeys"][0]
        duration = best_journey["duration"]
        arrivalTime = datetime.strptime(best_journey["arrivalDateTime"], "%Y-%m-%dT%H:%M:%S").strftime("%H:%M") 
        legs = best_journey["legs"]
        for i, leg in enumerate(legs):
            subRoute = leg["instruction"]["detailed"]
            deptPoint = leg["departurePoint"]["commonName"]
            arrPoint = leg["arrivalPoint"]["commonName"].replace(" Underground Station","")
            self.routeInfo += leg["disruptions"]
            suboutput = f"take {subRoute} from {deptPoint}, then get off at {arrPoint}." 
            output += suboutput
            if i < len(legs)-1:
                output += " Then, "
            else:
                output += f" In total, it will take {str(duration)} minutes. The estimated arrival time is {arrivalTime}."
        
        print(output)
        
        if self.routeInfo:
            self.getRouteInfo()

    def getFare(self):
        """
        Sends the API request and get information on the fare of the route.
        If unsuccessful, returns None.
        """
        methodIndex = self.check_input("What payment method are you using? Choose the number from these two: 1. Cash or 2. Pay as you go: ", range(1, 3))
        methods = ["CashSingle", "Pay as you go"]
        url = f"https://api.tfl.gov.uk/Stoppoint/{self.origin}/FareTo/{self.destination}"
        response = self.sendRequest(url)
        data = response.json()
        if response.status_code != 200 or not data:
            print("Sorry, I could not get the information. The information is only available for the Tube network.")
            return None
        
        row = data[0]["rows"][0]
        from_station = row["from"].replace(" Underground Station","")
        to_station = row["to"].replace(" Underground Station", "")
        passenger_type = row["passengerType"]
        print(f"The Tube fare from {from_station} to {to_station} for {passenger_type} is: ")
        for ticket in row["ticketsAvailable"]:
            paymentMethod = ticket["description"]
            if paymentMethod == methods[int(methodIndex)-1]:
                cost = ticket["cost"]
                ticketTimeDescription = ticket["ticketTime"]["description"]
                if paymentMethod == "CashSingle":
                    print(f"£{cost} {ticketTimeDescription}")
                else: # paymentMethod == "Pay as you go"
                    ticketTime = ticket["ticketTime"]["type"]
                    if ticketTime == "Peak":
                        print(f"£{cost} during {ticketTime} time. Peak time applies to {ticketTimeDescription}")
                    else:
                        print(f"£{cost} during {ticketTime} time. This applies to {ticketTimeDescription}")
        
    def getRouteInfo(self):
        """
        Sends a request to API and outputs the information of disruptions on the route.
        If unsuccessful, returns None.
        """
        if not self.routeInfo: # No information is loaded, then queries API      
            base_url = "https://api.tfl.gov.uk/Journey/JourneyResults"
            endpoint = f"{self.destination}/to/{self.origin}"
            mode = "bus,overground,national-rail,tube,dlr,tram,walking"
            journeyPreference = "LeastInterchange"
            walkSpeed = "Slow"
            url = f"{base_url}/{endpoint}?timeIs=Departing&journeyPreference={journeyPreference}&mode={mode}&accessibilityPreference=NoRequirements&walkingSpeed={walkSpeed}&cyclePreference=None&bikeProficiency=Easy"
            
            response = self.sendRequest(url)
            if response.status_code == 200:
                json = response.json()
            else:
                print("Sorry, I could not find a route...")
                return None, 404
            
            best_journey = json["journeys"][0]
            legs = best_journey["legs"]
            for i, leg in enumerate(legs):
                self.routeInfo += leg["disruptions"]
        
        output = "Currently, good service and no planned work on the route."
        for i, disruption in enumerate(self.routeInfo):
            if i == 0:
                output = "\nPlease mind a disruption on the suggested route. "
            type, description = disruption["type"], disruption["description"]
            output += f"\nDisruption Type: {type}, {description}"
        print(output)