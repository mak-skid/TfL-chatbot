from __future__ import unicode_literals, print_function
import csv
import nltk
from nltk.tokenize import word_tokenize
import os, random
from joblib import dump, load

nltk.download('punkt')  # Download the required resource

def replace_station_names(text, replacement):
    """ 
    Replaces station names in the text and return a tuple of the modified text
    and a list of tuples 
    >>> return tuple(new_string, [(start_pos, end_pos, label)])
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
            end = total_length+space_count 
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
def build_ner_dataset(isTest):
    """
    Builds a dataset for a custom NER model (for station name detection)
    In test mode, it builds a test dataset 
    """
    user_inputs = []
    searchDatasets = ["searchRoute", "searchFare", "searchTime"]
    for dataset in searchDatasets:
        directory = "./Datasets/" + dataset + ".csv" 
        file = open(directory, newline='')
        DictReader = csv.DictReader(file)
        for row in DictReader:
            user_inputs.append(row)

    stationData = open("./Datasets/stations_list.csv", newline='')
    stationDictReader = csv.DictReader(stationData)
    station_list = []        
    for row in stationDictReader:
        station_list.append(row["STATIONNAME"])

    original_user_input_length = len(user_inputs)
    new_user_inputs = []
    station_list_len = len(station_list)
    for _ in range(station_list_len): 
        # for each user_input, create variations of the number of stations
        for j in range(original_user_input_length):
            if isTest: # if in a test mode, build a randomised data
                while True:
                    randomIndex = random.randint(0, original_user_input_length)
                    if j != randomIndex:
                        break
                replacement = (station_list[j], station_list[randomIndex])
            else:
                replacement = (station_list[j], station_list[-j])
            replaced = replace_station_names(user_inputs[j]["text"], replacement)
            replaced_text, entities = replaced[0], replaced[1]
            new_user_input = {
                "text": replaced_text,  
                "entities": entities
            }
            new_user_inputs.append(new_user_input)
    
    if isTest:
        dump(new_user_inputs, "src/joblibs/custom_ner_test_dataset.joblib")
        ner_test_dataset_output(new_user_inputs)
    else:
        dump(new_user_inputs, "src/joblibs/custom_ner_dataset.joblib")
        ner_dataset_output(new_user_inputs)
    
    return new_user_inputs    

def get_ner_dataset():
    """
    Returns a dataset for a custom station NER model 
    """
    ner_path = "src/joblibs/custom_ner_dataset.joblib"
    if os.path.exists(ner_path):
        ner_dataset = load(ner_path)
        return ner_dataset
    else:
        return build_ner_dataset(isTest=False)

def ner_dataset_output(new_user_inputs):
    with open('../../Datasets/StationNERDataset.csv', 'w') as csvfile: 
        writer = csv.DictWriter(csvfile, fieldnames=["text", "entities"]) 
        writer.writeheader() 
        writer.writerows(new_user_inputs)

def get_test_ner_dataset():
    """
    Create and store a test dataset
    """
    ner_path = "src/joblibs/custom_ner_test_dataset.joblib"
    if os.path.exists(ner_path):
        ner_dataset = load(ner_path)
        return ner_dataset
    else:
        return build_ner_dataset(isTest=True)

def ner_test_dataset_output(new_user_inputs):
    with open('./Datasets/StationNERDataset.csv', 'w') as csvfile: 
        writer = csv.DictWriter(csvfile, fieldnames=["text", "entities"]) 
        writer.writeheader() 
        writer.writerows(new_user_inputs)