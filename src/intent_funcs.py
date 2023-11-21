import spacy, csv, os
from joblib import dump, load

class Identity():
    def __init__(self) -> None:
        self.name = ""
        self.destination = ""
        self.location = ""

    # Used for asking the user's name
    def askName(self):
        print("Oh, but firstly what is your name?")
        self.name = input("Type your name: ")
        print(f"Nice to meet you, {self.name}.")
    
    # Output the user's name
    def getName(self):
        return self.name
    
    # Extract user's destination and location from user input
    def getWhereabouts(self, text):
        nlp = spacy.load("en_core_web_sm")

        stationData = open("../Datasets/stations_list.csv", newline='')
        stationDictReader = csv.DictReader(stationData)
        
        for row in stationDictReader:
            print(row["STATIONNAME"])

        def extract_station_name(text):
            doc = nlp(text)
            station_names = []
            for ent in doc.ents:
                print(ent.label_)
                if ent.label_ in ["GPE", "FAC"]:
                    station_names.append([ent.text, ent.label_])
            return station_names
        
        stations = extract_station_name(text)
        if stations:
            print(stations)
        else:
            print("No station names detected")
        
