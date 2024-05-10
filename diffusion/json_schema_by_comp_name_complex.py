import json
from parsing_tei_xml import read_grobid
import openai
import os
import ast
import jstyleson
import name_normaliztion as comp_norm

from pprint import pprint

openai.api_key = "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"
def json_schema(text):
    roleSetting1 = "I am a helpful assistant capable of extracting information from text. I will not generate any new tokens, only extract tokens containing information from the text you provide. If provided with a schema then I will follow it and return the information in format of the schema."
    schema = {
                'melt': {'type': 'string'},
                'diffusing species': {'type': 'string'},
                'type of experiment': {'type': 'string'},
                'test temperature': {'type': 'float'},
                'pressure': {'type': 'float'},
                'diffusivity': {'type': 'float'},
                'SiO2': {'type': 'float'},
                'TiO2': {'type': 'float'},
                'Al2O3': {'type': 'float'},
                'FeOt': {'type': 'float'},
                'MnO': {'type': 'float'},
                'MgO': {'type': 'float'},
                'CaO': {'type': 'float'},
                'Na2O': {'type': 'float'},
                'K2O': {'type': 'float'},
                'P2O5': {'type': 'float'},
                'H2Ot': {'type': 'float'}
    }


    prompt =           (f"Extract all information relating to diffusion of elements into a silicate melt from the following text: {text} using the following schema: {schema}. "
                       f"Return a list of schemas in JSON format for every unique compound.\n\n"
                       f"Additional context: there will generally be one or multiple liquids, and one or more elements that move through that liquid at a certain speed. That speed is called the “diffusivity” or the “diffusion coefficient” D(m^2/s). Each element will have a unique diffusivity in each melt and temperature and pressure, so it is important to keep track of every combination.\n\n"
                       f"Restriction: Do not extract any tokens if no relevant property is present as mentioned in the schema. "
                       f"If a property is not available then return 'No information'. Do not violate the schema.\n\n")

    try:
        answer_extracted = openai.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": roleSetting1},
                {"role": "user", "content": prompt},
                {"role": "system", "content": "Extracted information:"}
            ],
            # temperature=0.0,
            response_format={"type": "json_object"},
            seed=22
        )

        properties = answer_extracted.choices[0].message.content
        # pprint(text)
        # pprint(properties)
        if properties=="No information":
            return properties

        return properties

    except openai.OpenAIError as e:
        print(e)
        return f"Error: {e}"


def run():

    failed = {}

    collection = [read_grobid(f) for f in os.listdir('./text') if f.endswith('.tei.xml')]
    collection.sort(key=lambda x: x['title'])

    with open("titles_to_dois.json", "r") as f:
        titles_to_dois = json.load(f)
    papers_to_process = list(titles_to_dois.keys())

    for i, entry in enumerate(collection):

        if entry['title'] == "The effect of glass composition on the thermodynamics of the Fe 2+ /Fe 3+ equilibrium and the iron diffusivity in Na 2 O/MgO/CaO/Al 2 O 3 /SiO 2 melts":
            continue
        elif entry['title'] not in papers_to_process:
            continue

        print(f'Processing index {i+1} of {len(collection)}')


        abstract = entry['abstract']
        entire_text = "\n".join(section for section in entry['body'])
        entire_text = f"{abstract}\n{entire_text}"
        if len(entire_text) < 100:
            failed[failed[titles_to_dois[entry['title']]]] = "Text too short"
            continue
        else:
            extracted_info = json_schema(entire_text)
            try:
                converted_list = json.loads(extracted_info) # list of dictionaries
                information_dict = {
                    'doi': titles_to_dois[entry['title']],
                    'extracted_info': converted_list
                }
                # # # creating a directory for the extracted information
                if not os.path.exists("extracted_info/schema_0shot_complex"):
                    os.makedirs("extracted_info/schema_0shot_complex")

                # # # saving the information to a file
                with open(
                        f"extracted_info/schema_0shot_complex/{titles_to_dois[entry['title']].replace('/', '.')}_extracted_info.json",
                        "w") as f:
                    json.dump(information_dict, f, indent=4)
            except:
                try:
                    converted_list = jstyleson.loads(extracted_info)  # list of dictionaries
                    information_dict = {
                        'doi': titles_to_dois[entry['title']],
                        'extracted_info': converted_list
                    }
                    # # # saving the information to a file
                    with open(
                            f"extracted_info/schema_0shot_complex/{titles_to_dois[entry['title']].replace('/', '.')}_extracted_info.json",
                            "w") as f:
                        json.dump(information_dict, f, indent=4)
                except:
                    print("Error in converting to jstyleson")
                    print(extracted_info)
                    failed[titles_to_dois[entry['title']]] = extracted_info

                print("Error in converting to json")
                print(extracted_info)
                failed[titles_to_dois[entry['title']]] = extracted_info
                continue
    print(f"Failing DOIs:")
    print(failed)

    if len(failed) > 0:
        with open("extracted_info/schema_0shot_complex/failed_DOIs.json", "a") as f:
            json.dump(failed, f, indent=4)

if __name__=='__main__':
    run()