import csv
import time
import os
from similarity_calc import max_similarity
from User import User
from joblib import dump, load

class Main(User):
    def __init__(self) -> None:
        super().__init__()
        self.stop = False
        self.data = {}
        self.csv_files = {
            "Q":"QADataset",
            "T":"travel_chat", 
            "C":"chitchat",
            "CD":"checkDisruptions", 
            "SF":"searchFare",
            "SR":"searchRoute",
            "ST":"searchTime"
        }
        self.lens = []
        self.documents = {}
        self.answers = {}
        self.similarities = {}
        if os.path.exists("src/joblibs/documents.joblib"):
            self.documents = load("src/joblibs/documents.joblib")
            self.answers = load("src/joblibs/answers.joblib")
        else:
            self.readDocuments()
        
    def readDocuments(self): 
        """
        Reads data from CSV files and load them onto the self.documents and self.answers dictionaries.
        """
        for key, csv_file in self.csv_files.items():
            path_to_csv = "./Datasets/" + csv_file + ".csv"
            len = 0
            self.data[key] = []
            with open(path_to_csv, 'r', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.data[key].append(row)
                    len += 1
                self.lens.append(len)

        for key in self.csv_files.keys():
            self.documents[key] = {}
            for row in self.data[key]:
                self.documents[key][row["id"]] = row["text"]
                self.answers[row["id"]] = (row["response"], row["intent"])
        
        dump(self.documents, "src/joblibs/documents.joblib")
        dump(self.answers, "src/joblibs/answers.joblib")

    def interaction(self):
        """
        Actual interaction part.
        """
        start = time.time()
        first_time = True

        print("Hello, this is London Tube journey planner AI. How can I help you?")
        while not self.stop:    
            query = input("Send a message: ")

            if query == "STOP":
                self.stop = True
            else:
                document_id = max_similarity(self.documents, [query])
                if document_id == None: # if could not find a pair with similarity above 0.8
                    print("Sorry, I could not understand what you said. Could you clarify more?")
                    continue
                response, intent = self.answers[document_id][0], self.answers[document_id][1]
                
                if intent == "name":
                    print(response + self.getName() + ".")
                    continue
                if intent == "greeting":
                    print(response)
                    if first_time:
                        self.askName()
                    first_time = False
                    continue
                if intent in ["goodbye"]:
                    response += f", {self.name}!" if self.name else "!"
                    print(response)
                    break
                if intent == "options":
                    print(response)
                    continue
                if intent == "enquiry":
                    print(response)
                    print("Do you have anything else to ask?")
                    continue
                if intent == "SearchRoute":
                    print("OK, I see you want me to search for the route!")
                    self.ORNDSTreset()
                    found = self.extractORNDST(query)
                    self.getORNDST()
                    map, status = self.getStopPoint(intent)
                    while status == 404 and not self.stop:         
                        self.ORNDSTreset()
                        self.getORNDST()
                        map, status = self.getStopPoint(intent)
                        stop_msg = input("Do you want to continue? Select a number: 1. Yes, 2. No")
                        self.stop = True if stop_msg == "2" else False
                    if self.stop:
                        print(f"See you again!")
                        break
                    self.disambiguate(map)
                    self.getRoute()         
                elif intent == "SearchFare":
                    print("OK, about the fare...")
                    found = self.extractORNDST(query)
                    if found or not self.isLoaded():
                        self.getORNDST()
                        map, status = self.getStopPoint(intent)
                        while status == 404 and not self.stop:
                            self.ORNDSTreset()
                            self.getORNDST()
                            map, status = self.getStopPoint(intent)
                            stop_msg = input("Do you want to continue? Select a number: 1. Yes, 2. No")
                            self.stop = True if stop_msg == "2" else False
                        if self.stop:
                            print(f"See you again!")
                            break
                        self.disambiguate(map)
                    self.getFare()
                elif intent == "checkDisruptions":
                    print("OK, I am checking if there are disruptions on the route.")
                    if not self.isLoaded():
                        query = input("But firstly, which station are you going from and to?: ")
                    found = self.extractORNDST(query)
                    if found or not self.isLoaded():
                        self.getORNDST()
                        map, status = self.getStopPoint(intent)
                        while status == 404 and not self.stop:
                            self.ORNDSTreset()
                            self.getORNDST()
                            map, status = self.getStopPoint(intent)
                            stop_msg = input("Do you want to continue? Select a number: 1. Yes, 2. No")
                            self.stop = True if stop_msg == "2" else False
                        if self.stop:
                            print(f"See you again!")
                            break
                        self.disambiguate(map)
                    self.getRouteInfo()
                elif intent == "SearchTime":
                    print("Ask about the route and I will tell you how long it takes too!")
                
                print("Do you have anything else to ask about the route? If so, type in your question!")

        end = time.time()
        print("Session: " + str(round(end-start, 2)) + " sec")

session = Main()
session.interaction()