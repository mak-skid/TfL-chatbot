import csv
import time
import os
from similarity_calc import max_similarity, similarity_calc
from intent_funcs import Identity
from joblib import dump, load

class Main(Identity):
    def __init__(self) -> None:
        self.data = {}
        self.csv_files = {
            "Q":"QADataset",
            "T":"travel_chat", 
            "C":"chitchat", 
            "SF":"searchFare",
            "SR":"searchRoute",
            "ST":"searchTime"
        }
        self.lens = []
        self.documents = {}
        self.answers = {}
        self.similarities = {}
        
    # Reading data from a CSV file and processing it into a Python data structure
    def readDocuments(self): 
        for key, csv_file in self.csv_files.items():
            path_to_csv = "../Datasets/" + csv_file + ".csv"
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
        
        #dump(self.documents, "documents.joblib")
        #dump(self.answers, "answers.joblib")

    # Actual interaction part.
    def interaction(self):
        if os.path.exists("documents.joblib"):
            self.documents = load("documents.joblib")
            self.answers = load("answers.joblib")
        else:
            self.readDocuments()
        
        stop = False
        start = time.time()
        first_time = True

        while not stop:    
            query = input("Send a message: ")

            if query == "STOP":
                stop = True
            else:
                document_id = max_similarity(self.documents, [query])
                if document_id == None: # if could not find a pair with similarity above 0.8
                    print("Sorry, I could not understand what you said. Could you clarify more?")
                    continue
                
                response, intent = self.answers[document_id][0], self.answers[document_id][1]
                if intent == "name":
                    print(response + self.getName() + ".")
                    continue
                if intent == "greeting" and first_time:
                    print(response)
                    self.askName()
                    first_time = False
                    continue
                if intent == "SearchRoute":
                    #self.getWhereabouts(query)
                    print("Search route!")
                    continue         
                if intent == "SearchFare":
                    pass
                if intent == "SearchTime":
                    pass
                    
                print(response)
                

        end = time.time()
        print("Session: " + str(round(end-start, 2)) + " sec")

session = Main()
session.interaction()