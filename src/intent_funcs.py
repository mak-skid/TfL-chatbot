from datetime import datetime
from urllib.error import HTTPError, URLError
import spacy, csv, os
from joblib import dump, load
from nltk import word_tokenize
import requests, json 

class Identity():
    def __init__(self) -> None:
        self.name = ""
        self.DSTlist = []
        self.destination = ""
        self.ORNlist = []
        self.origin = ""
    
    def isLoaded(self):
        return not "" in [self.origin, self.destination]

    # Used for asking the user's name
    def askName(self):
        print("Oh, but firstly what is your name?")
        self.name = input("Type your name: ")
        print(f"Nice to meet you, {self.name}.")
    
    # Output the user's name
    def getName(self):
        return self.name
    
    def is_number(self, variable):
        try:
            int(variable)
            return True # Successfully converted to int, so it's a number
        except ValueError:
            return False   # Conversion to int failed, so it's not a number
    
    def check_input(self, script, expected_range):
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
    
    def getORNDST(self, text):
        nlp_ner = spacy.load("./src/model-last")  # location of your created model

        doc = nlp_ner(text)

        self.ORNDSTinit()
        
        for ent in doc.ents:
            if ent.label_ == "DST":
                self.DSTlist.append(ent.text)
            if ent.label_ == "ORN":
                self.ORNlist.append(ent.text)
        
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

        confirmation = input("I see you want to go to " + self.destination + " from " + self.origin + ". Is it correct?: ")

        if not confirmation in ["Yes", "Yep", "Correct", "Yes." "Yes!"]:
            self.ORNDSTinit()
            text = input("Please type in where you are going from and to.")
            self.getORNDST(text)

    def ORNDSTinit(self):
        self.DSTlist = []
        self.destination = ""
        self.ORNlist = []
        self.origin = ""
    
    def getStopPoint(self, intent):
        self.destination = self.destination.replace(" ", "%20")
        self.origin = self.origin.replace(" ", "%20")
        
        if intent == "SearchRoute":
            mode = "bus,overground,national-rail,tube,dlr,tram,walking"
        if intent == "SearchFare":
            mode = "tube"
        
        map = {"origins": self.origin, "destinations": self.destination}
        for key, stopPoint in map.items():
            url = f"https://api.tfl.gov.uk/StopPoint/Search/{stopPoint}?modes={mode}&includeHubs=False"
            response = requests.get(url)
            if response.status_code != 200:
                print(f"I could not find a station or a stop")
                return None, 404
            else:
                data = response.json()
                map[key] = {j+1: {
                    "commonName": match["name"],
                    "availableModes": match["modes"],
                    "naptanId": match["id"]
                } for j, match in enumerate(data["matches"])}
        
        return map, 200
        
    def disambiguate(self, map):
        o, d = len(map["origins"]), len(map["destinations"])
        if o > 1 or d > 1:
            print("There are multiple stations and stops available around the locations you provided.")
        if o > 1:
            print("Choose a station or a stop from which you are departing from the list below")
            for i, item in map["origins"].items():
                name = item["commonName"]
                modes = ", ".join(item["availableModes"])
                print(f"{i}. {name} (Available modes of transport: {modes})")
            
            originIndex = self.check_input("Select a number: ", range(1, o+1))
        else:
            originIndex = 1
        
        if d > 1:
            print("Choose a station or a stop to which you are going from the list below")
            for i, item in map["destinations"].items():
                name = item["commonName"]
                modes = ", ".join(item["availableModes"])
                print(f"{i}. {name} (Available modes of transport: {modes})")
            
            dstIndex = self.check_input("Select a number: ", range(1, d+1))
        else:
            dstIndex = 1
        
        self.origin = map["origins"][int(originIndex)]["naptanId"]
        self.destination = map["destinations"][int(dstIndex)]["naptanId"]


    def getRoute(self):
        base_url = "https://api.tfl.gov.uk/Journey/JourneyResults"
        endpoint = f"{self.destination}/to/{self.origin}"
        mode = "bus,overground,national-rail,tube,dlr,tram,walking"
        journeyPreference = "LeastInterchange"
        walkSpeed = "Slow"
        url = f"{base_url}/{endpoint}?timeIs=Departing&journeyPreference={journeyPreference}&mode={mode}&accessibilityPreference=NoRequirements&walkingSpeed={walkSpeed}&cyclePreference=None&bikeProficiency=Easy"
        response = requests.get(url)
        if response.status_code == 200:
            json = response.json()
        else:
            print("I could not find a route...")
            return None, 404
        
        output = "OK, the best route is as follows: "
        best_journey = json["journeys"][0]
        duration = best_journey["duration"]
        arrivalTime = datetime.strptime(best_journey["arrivalDateTime"], "%Y-%m-%dT%H:%M:%S").strftime("%H:%M") 
        legs = best_journey["legs"]
        for i, leg in enumerate(legs):
            subRoute = leg["instruction"]["detailed"]
            deptPoint = leg["departurePoint"]["commonName"]
            arrPoint = leg["arrivalPoint"]["commonName"]
            suboutput = f"take {subRoute} from {deptPoint}, then get off at {arrPoint}." 
            output += suboutput
            if i < len(legs)-1:
                output += " Then, "
            else:
                output += f" In total, it will take {str(duration)} minutes. The estimated arrival time is {arrivalTime}."
        
        print(output)

    def getFare(self):
        methodIndex = self.check_input("What payment method are you using? Choose the number from these two: 1. Cash or 2. Pay as you go: ", range(1, 3))
        methods = ["CashSingle", "Pay as you go"]
        url = f"https://api.tfl.gov.uk/Stoppoint/{self.origin}/FareTo/{self.destination}"
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200 or not data:
            print("Sorry, I could not get the information.")
            return None
        
        row = data[0]["rows"][0]
        from_station = row["from"]
        to_station = row["to"]
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