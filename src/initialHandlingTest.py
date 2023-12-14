import csv
from joblib import load
from similarity_calc import max_similarity

path_to_csv = 'Datasets/initialHandlingTest.csv'

test_set = []
with open(path_to_csv, 'r', encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        test_set.append(row)

documents = load("src/joblibs/documents.joblib")
answers = load("src/joblibs/answers.joblib")

count = 0
no_match = 0
fails = 0
for test_query in test_set:
    index = max_similarity(documents, [test_query["question"]])
    if not index:
        no_match += 1
        continue
    intent = answers[index][1]
    if intent == test_query["intent"]:
        count += 1
    else:
        fails += 1

accuracy = count/len(test_set)*100
no_matching_rate = no_match/len(test_set)*100
false_matching_rate = fails/len(test_set)*100
print(f"Accuracy: {accuracy:.2f}%")
print(f"No matching rate: {no_matching_rate:.2f}%")
print(f"False matching rate: {false_matching_rate:.2f}%")
