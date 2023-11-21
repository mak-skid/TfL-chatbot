from __future__ import unicode_literals, print_function
import csv
import nltk
from nltk.tokenize import word_tokenize

nltk.download('punkt')  # Download the required resource

def replace_station_names(text, replacement):
    """ 
    replaces station names in the text and return a tuple of the modified text
    and a triple (start_pos, end_pos, label)
    """
    tokens = word_tokenize(text)
    entities = []
    total_length = 0
    space_count = 0 
    for i in range(len(tokens)):
        label = ""
        if tokens[i] == "DST":
            tokens[i] = replacement[0]
            label = "DST"
        if tokens[i] == "ORN":
            tokens[i] = replacement[1]
            label = "ORN"

        word_len = len(tokens[i])
        total_length += word_len
        
        if tokens[i] in replacement:
            start = total_length-(word_len-1)+space_count-1
            end = total_length+space_count-1
            entities.append((start, end, label))
        
        space_count += 1
    new_string = " ".join(tokens)
    return new_string, entities

"""
EXAMPLES = [
    ["SR12",[""],"can i use the tube to travel from Blackfriars to Heathrow?",[""],"SearchRoute", {
        "entities": [(29, 45, "ORN"), (46, 57, "DST")]
    }],
    ["SR13",[""],"what is the best route to reach Vaxuhall from Waterloo on the tube?",[""],"SearchRoute", {
        "entities": [(32, 40, "DST"), (41, 54, "ORN")]
    }],
    ["SR14",[""],"can you suggest a route from Piccadilly Circus to Southwark?",[""],"SearchRoute", {
        "entities": [(24, 46, "ORN"), (47, 59, "DST")]
    }]
]
"""
searchFare = open("../Datasets/searchRoute.csv", newline='')
FareDictReader = csv.DictReader(searchFare)

stationData = open("../Datasets/stations_list.csv", newline='')
stationDictReader = csv.DictReader(stationData)
station_list = []        
for row in stationDictReader:
    station_list.append(row["STATIONNAME"])

user_inputs = []

for row in FareDictReader:
    user_inputs.append(row)

original_user_input_length = len(user_inputs)
new_user_inputs = []
station_list_len = len(station_list)
for i in range(station_list_len):
    new_length = len(user_inputs)
    # for each user_input, create variations of the number of stations
    for j in range(original_user_input_length):
        replacement = (station_list[j], station_list[-j])
        # id = user_inputs[j]["id"][:2] + str(new_length + j)
        replaced = replace_station_names(user_inputs[j]["text"], replacement)
        replaced_text, entities = replaced[0], {"entities": replaced[1]}
        new_user_input = {
            "text": replaced_text,  
            "entities": entities
        }
        new_user_inputs.append(new_user_input)

with open('../Datasets/StationNERDataset.csv', 'w') as csvfile: 
    writer = csv.DictWriter(csvfile, fieldnames=["text", "entities"]) 
    writer.writeheader() 
    writer.writerows(new_user_inputs) 
