import csv
import time
from similarity_calc import similarity_calc

# Reading data from a CSV file and processing it into a Python data structure
data = []
csv_file = "QADataset.csv"
#csv_file = 'simple.csv'
with open(csv_file, 'r', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        data.append(row)

documents = {}
answers = {}
for row in data:
    documents[row["QuestionID"]] = row["Question"]
    answers[row["QuestionID"]] = row["Answer"]

stop = False
while not stop:
    query = input("Enter your query, or STOP to quit, and press return: ")

    if query == "STOP":
        stop = True
    else:
        print(f"You are searching for {query}")

        start = time.time()
        related_product_indices = similarity_calc(documents.values(), [query])    
        print(answers["Q"+ str(related_product_indices[0])])
        stop = True

end = time.time()
print("Search took " + str(round(end-start, 2)) + " sec")
