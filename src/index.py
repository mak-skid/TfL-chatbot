import csv
import time
import os
from similarity_calc import similarity_calc
from intent_funcs import Identity
from joblib import dump, load

class Main(Identity):
    def __init__(self) -> None:
        self.data = []
        self.csv_files = ["QADataset.csv", "travel_chat.csv", "chitchat.csv"]
        self.lens = []
        self.documents = {}
        self.answers = {}

    def readDocuments(self): # Reading data from a CSV file and processing it into a Python data structure
        for csv_file in self.csv_files:
            path_to_csv = "../Datasets/" + csv_file
            len = 0
            with open(path_to_csv, 'r', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.data.append(row)
                    len += 1
                self.lens.append(len)
        
        for row in self.data:
            self.documents[row["id"]] = row["text"]
            self.answers[row["id"]] = [row["response"], row["intent"]]
        
        dump(self.documents, "documents.joblib")
        dump(self.answers, "answers.joblib")

    def interaction(self):
        if not os.path.exists("documents.joblib"):
            self.readDocuments()
        else:
            self.documents = load("documents.joblib")
            self.answers = load("answers.joblib")
        stop = False
        start = time.time()
        first_time = True

        while not stop:    
            query = input("Send a message: ")

            if query == "STOP":
                stop = True
            else:
                document_index = similarity_calc(self.documents.values(), [query]) 
                if document_index == None: # if could not find a pair with similarity above 0.8
                    print("Sorry, I could not understand what you said. Could you clarify more?")
                    continue
                
                document_index += 1
                QA_last_i = self.lens[0]
                TC_last_i = QA_last_i + self.lens[1]

                if document_index <= QA_last_i: # if index is in QA
                    key = f"Q{str(document_index)}"
                elif document_index <= TC_last_i: # if index is in Travel Chat
                    key = f"T{str(document_index-QA_last_i)}"
                else:
                    key = f"C{str(document_index-TC_last_i)}" # if index is in ChitChat
                
                intent = self.answers[key][1]
                if intent == "name":
                    print(self.answers[key][0] + self.getName() + ".")
                    continue
                if intent == "greeting" and first_time:
                    print(self.answers[key][0])
                    self.askName()
                    first_time = False
                    continue
                if intent == "SearchRoute":
                    pass
                if intent == "SearchFare":
                    pass
                if intent == "SearchTime":
                    pass
                    
                print(self.answers[key][0])
                

        end = time.time()
        print("Session: " + str(round(end-start, 2)) + " sec")

session = Main()
session.interaction()