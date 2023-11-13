import csv
import time
from similarity_calc import similarity_calc

# Reading data from a CSV file and processing it into a Python data structure
data = []
csv_files = ["QADataset.csv", "travel_chat.csv", "chitchat.csv"]
lens = []
for csv_file in csv_files:
    len = 0
    with open(csv_file, 'r', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
            len += 1
        lens.append(len)


documents = {}
answers = {}
for row in data:
    documents[row["id"]] = row["text"]
    answers[row["id"]] = [row["response"], row["intent"]]

stop = False

start = time.time()
print("Hello, this is London Tube journey planner AI. What is your name?")
name = input("Type your name: ")
print(f"Nice to meet you, {name}.")

while not stop:    
    query = input("Send a message: ")

    if query == "STOP":
        stop = True
    else:
        related_product_index = similarity_calc(documents.values(), [query])[0]
        print(related_product_index)
        
        name_index = [7183, 7190, 7194] # IDs for name QAs

        if related_product_index < lens[0]:
            key = f"Q{str(related_product_index+1)}"
        elif related_product_index < lens[0]+lens[1]:
            key = f"T{str(related_product_index-lens[0]+1)}"
        else:
            if related_product_index-lens[0]-lens[1]+1 in name_index:
                key = f"C{str(related_product_index+1-lens[0]-lens[1])}"
                print(key+": "+answers[key][0]+name+".")
                continue
            key = f"C{str(related_product_index-lens[0]-lens[1]+1)}"
        print(key+": "+answers[key][0])
        

end = time.time()
print("Session: " + str(round(end-start, 2)) + " sec")
