import json
from parsing_tei_xml import read_grobid
import openai
import os
import ast
import jstyleson
import name_normaliztion as comp_norm
import re
import os


from pprint import pprint

with open("../openAI_key", "r") as f:
    key = f.read().strip()

openai.api_key = key
def json_schema(text):
    roleSetting1 = "I am a helpful assistant capable of extracting information from text. I will not generate any new tokens, only extract tokens containing information from the text you provide. If provided with a schema then I will follow it and return the information in format of the schema."
    schema = {
            "high entropy alloy formula": {"type": "string"},
            # "microstructure": {"type": "string"},
            # "processing method": {"type": "string"},
            # "BCC/FCC/other": {"type": "string"},
            "grain size": {"type": "float"},
            "experimental density": {"type": "float"},
            "hardness": {"type": "float"},
            # "type of test": {"type": "string"},
            "test temperature": {"type": "float"},
            "yield strength": {"type": "float"},
            "ultimate tensile strength": {"type": "float"},
            "elongation": {"type": "float"},
            "elongation plastic": {"type": "float"},
            # "experimental young modulus": {"type": "float"},
            # "oxygen content": {"type": "float"},
            # "nitrogen content": {"type": "float"},
            # "carbon content": {"type": "float"}
    }


    one_shot_text, one_shot_op = get_exemplar()
    one_shot_prompt = (f"Extract all information relating to every High Entropy Alloys (HEA) from the following text: {one_shot_text} using the following schema: {schema}. "
                       f"Return a list of schemas in JSON format for every unique compound.\n\n"
                       f"Additional context: HEA composition sometimes have variable ratio denoted by 'x', if so then replace x with a float or integer as applicable by the information in the paper."
                       f"\n\nRestriction: Do not extract any tokens if a HEA material does not have a property mentioned in the schema. "
                       f"If a property is not available then return 'No information'. Do not violate the schema.\n\n")

    prompt = f"Extract all information relating to every High Entropy Alloys (HEA) and their yield strength from the following text: {text} using the following schema: {schema}. Return a list of schemas in JSON format for every unique compound.\n\nAdditional context: HEA composition sometimes have variable ratio denoted by 'x', if so then replace x with a float or integer as applicable from the information in the paper.\n\nRestriction: Do not extract any tokens if a HEA material does not have a property mentioned in the schema. If a property is not available then return 'No information'. Do not violate the schema.\n\n"

    try:
        answer_extracted = openai.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": roleSetting1},
                {"role": "user", "content": one_shot_prompt},
                {"role": "system", "content": f"Extracted information: {one_shot_op}"},
                {"role": "user", "content": prompt},
                {"role": "system", "content": "Extracted information:"}
            ],
            response_format={"type": "json_object"},
            # temperature=0.0,

            seed=22
        )

        properties = answer_extracted.choices[0].message.content
        if properties=="No information":
            return properties

        pprint(properties)
        return properties

    except Exception as e:
        print(e)
        return f"Error: {e}"

def get_exemplar():
    exemplar_op = '''[
                           {
                               "high entropy alloy formula": 'NbMoTaWVCr',
                               "grain size": 0.54,
                               "experimental density": 'No information',
                               "hardness": 1072.0, 
                               "test temperature": 25.0,
                               "yield strength": 'No information',
                               "ultimate tensile strength": 'No information',
                               "elongation": 'No information', 
                               "elongation plastic": 'No information',
                           },
                           {
                               "high entropy alloy formula": 'NbMoTaWVCr',
                               "grain size": 1.24,
                               "experimental density": 'No information',
                               "hardness": 1010.0,
                               "test temperature": 25.0,   
                               "yield strength": 3416.0,
                               "ultimate tensile strength": 'No information', 
                               "elongation": 'No information', 
                               "elongation plastic": 5.3,
                           },
                           {
                               "high entropy alloy formula": 'NbMoTaWVCr',
                               "grain size": 5.01,
                               "experimental density": 'No information',  
                               "hardness": 991.3,
                               "test temperature": 25.0,
                               "yield strength": 3410.0, 
                               "ultimate tensile strength": 'No information', 
                               "elongation": 'No information', 
                               "elongation plastic": 2.0,
                           },
                           {
                               "high entropy alloy formula": 'NbMoTaWVCr',
                               "grain size": 10.8,
                               "experimental density": 'No information',
                               "hardness": 988.3,
                               "testing temperature": 25.0,
                               "yield strength": 3338.0,
                               'ultimate tensile strength': 'No information', 
                               'elongation': 'No information', 
                               'elongation plastic': 1.9,
                           }
                       ]'''
    collection = [read_grobid(f) for f in os.listdir('./text') if f.endswith('.tei.xml')]
    collection.sort(key=lambda x: x['title'])
    exemplar_text = ""
    abstract = ""
    for i, entry in enumerate(collection):
        if entry['title'] == "A fine-grained NbMoTaWVCr refractory high-entropy alloy with ultra-high strength: Microstructural evolution and mechanical properties":
            abstract = entry['abstract']
            # pprint(entry_text)
            exemplar_text = "\n".join(section for section in entry['body'])
            break

    exemplar_text = f"{abstract}\n{exemplar_text}"
    return exemplar_text, exemplar_op

def run():

    failed = {}

    collection = [read_grobid(f) for f in os.listdir('./text') if f.endswith('.tei.xml')]
    collection.sort(key=lambda x: x['title'])

    for i, entry in enumerate(collection):
        if entry['title'] == "A fine-grained NbMoTaWVCr refractory high-entropy alloy with ultra-high strength: Microstructural evolution and mechanical properties":
            continue

        print(f'Processing index {i+1} of {len(collection)}')

        abstract = entry['abstract']
        entire_text = "\n".join(section for section in entry['body'])
        entire_text = f"{abstract}\n{entire_text}"
        if len(entire_text) < 100:
            failed[entry['doi']] = "Text too short"
            continue
        else:
            extracted_info = json_schema(entire_text)
            try:
                converted_list = jstyleson.loads(extracted_info) # list of dictionaries
                information_dict = {
                    'doi': entry['doi'],
                    'extracted_info': converted_list
                }
                # # # saving the information to a file
                with open(
                        f"./extracted_info/schema_1shot_simple/{entry['doi'].replace('/', '.')}_extracted_info.json",
                        "w") as f:
                    json.dump(information_dict, f, indent=4)
            except:
                try:
                    converted_list = ast.literal_eval(extracted_info)
                    information_dict = {
                        'doi': entry['doi'],
                        'extracted_info': converted_list
                    }
                    # # # saving the information to a file
                    with open(
                            f"./extracted_info/schema_1shot_simple/{entry['doi'].replace('/', '.')}_extracted_info.json",
                            "w") as f:
                        json.dump(information_dict, f, indent=4)
                except:
                    print(f"Error in converting to json")
                    print(extracted_info)
                    failed[entry['doi']] = extracted_info
                print("Error in converting to jstyleson")
                print(extracted_info)
                failed[entry['doi']] = extracted_info
                continue
    print(f"Failing DOIs:")
    print(failed)

    if len(failed) > 0:
        with open("./extracted_info/schema_1shot_simple/failed_DOIs.json", "a") as f:
            json.dump(failed, f, indent=4)




if __name__=='__main__':
    run()