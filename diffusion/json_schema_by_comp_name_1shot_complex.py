import json
from parsing_tei_xml import read_grobid
import openai
import os
import ast
import jstyleson
import name_normaliztion as comp_norm

from pprint import pprint

with open("../openAI_key", "r") as f:
    key = f.read().strip()

openai.api_key = key
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


    one_shot_text, one_shot_op = get_exemplar()
    one_shot_prompt = (f"Extract all information relating to diffusion of elements into a silicate melt from the following text: {one_shot_text} using the following schema: {schema}. "
                       f"Return a list of schemas in JSON format for every unique compound.\n\n"
                       f"Additional context: there will generally be one or multiple liquids, and one or more elements that move through that liquid at a certain speed. That speed is called the “diffusivity” or the “diffusion coefficient” D(m^2/s). Each element will have a unique diffusivity in each melt and temperature and pressure, so it is important to keep track of every combination.\n\n"
                       f"Restriction: Do not extract any tokens if no relevant property is present as mentioned in the schema. "
                       f"If a property is not available then return 'No information'. Do not violate the schema.\n\n")

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
                {"role": "user", "content": one_shot_prompt},
                {"role": "system", "content": f"Extracted information: {one_shot_op}"},
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


def get_exemplar():
    exemplar_op = '''[
    {
        "melt": "NCMAS6",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.35e-07,
        "SiO2": 80.6793201360426,
        "TiO2": "No information",
        "Al2O3": 0.0,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 0.0,
        "CaO": 14.11921335907197,
        "Na2O": 5.201466504885413,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.74e-07,
        "SiO2": 73.06889615165592,
        "TiO2": "No information",
        "Al2O3": 8.26638532993126,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 0.0,
        "CaO": 13.63984833370735,
        "Na2O": 5.024870184705469,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.38e-07,
        "SiO2": 65.95827029695563,
        "TiO2": "No information",
        "Al2O3": 15.98989368800878,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 0.0,
        "CaO": 13.19196456925617,
        "Na2O": 4.85987144577941,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.51e-07,
        "SiO2": 59.29977312460353,
        "TiO2": "No information",
        "Al2O3": 23.22230326963554,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 0.0,
        "CaO": 12.77255946482794,
        "Na2O": 4.705364140933018,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 2.24e-07,
        "SiO2": 53.05161051355635,
        "TiO2": "No information",
        "Al2O3": 30.00901053495324,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 0.0,
        "CaO": 12.3790004943065,
        "Na2O": 4.560378457183919,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.82e-07,
        "SiO2": 81.7618221185077,
        "TiO2": "No information",
        "Al2O3": 0.0,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 3.427817748006067,
        "CaO": 9.539103776706044,
        "Na2O": 5.271256356780171,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS5",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.48e-07,
        "SiO2": 74.01556975098646,
        "TiO2": "No information",
        "Al2O3": 8.373483824172876,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 3.309931239102126,
        "CaO": 9.211043265623625,
        "Na2O": 5.089971920114894,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.74e-07,
        "SiO2": 66.78440752214011,
        "TiO2": "No information",
        "Al2O3": 16.19016950395928,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 3.199883640594887,
        "CaO": 8.904797268983787,
        "Na2O": 4.920742064321916,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 2.19e-07,
        "SiO2": 60.0186119376424,
        "TiO2": "No information",
        "Al2O3": 23.5038067567281,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 3.096918234412368,
        "CaO": 8.61825995364458,
        "Na2O": 4.762403117572553,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 6.46e-08,
        "SiO2": 82.873767753853,
        "TiO2": "No information",
        "Al2O3": 0.0,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 6.948870868827822,
        "CaO": 4.834416910528287,
        "Na2O": 5.342944466790883,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.2e-07,
        "SiO2": 74.98709535492684,
        "TiO2": "No information",
        "Al2O3": 8.483393860084693,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 6.706754545829711,
        "CaO": 4.665973537739805,
        "Na2O": 5.156782701418962,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.48e-07,
        "SiO2": 71.24632400233786,
        "TiO2": "No information",
        "Al2O3": 12.50719948041893,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 6.591915009044993,
        "CaO": 4.586078226816733,
        "Na2O": 5.068483281381496,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS4",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.7e-07,
        "SiO2": 67.63150222814542,
        "TiO2": "No information",
        "Al2O3": 16.39552592449181,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 6.480942052138587,
        "CaO": 4.508872944173431,
        "Na2O": 4.983156851050733,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS3",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 2.24e-07,
        "SiO2": 60.75509230062255,
        "TiO2": "No information",
        "Al2O3": 23.79221882713044,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 6.269840208057144,
        "CaO": 4.362006734664607,
        "Na2O": 4.82084192952528,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.66e-07,
        "SiO2": 72.22978101565018,
        "TiO2": "No information",
        "Al2O3": 16.34291014695689,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 6.46014370710211,
        "CaO": 0.0,
        "Na2O": 4.967165130290811,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 7.71e-08,
        "SiO2": 84.0163748892496,
        "TiO2": "No information",
        "Al2O3": 0.0,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 10.56701576015797,
        "CaO": 0.0,
        "Na2O": 5.416609350592419,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.35e-07,
        "SiO2": 75.98446459910187,
        "TiO2": "No information",
        "Al2O3": 8.596227622777114,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 10.1939370557773,
        "CaO": 0.0,
        "Na2O": 5.225370722343701,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.66e-07,
        "SiO2": 68.50036213537885,
        "TiO2": "No information",
        "Al2O3": 16.60615876073641,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 9.84630378426992,
        "CaO": 0.0,
        "Na2O": 5.047175319614805,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 2.14e-07,
        "SiO2": 61.50987171293333,
        "TiO2": "No information",
        "Al2O3": 24.08779696328162,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 9.521598575225134,
        "CaO": 0.0,
        "Na2O": 4.880732748559932,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS2",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.86e-07,
        "SiO2": 54.96571825773216,
        "TiO2": "No information",
        "Al2O3": 31.09173882357569,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 9.217625522223098,
        "CaO": 0.0,
        "Na2O": 4.724917396469047,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.12e-07,
        "SiO2": 82.45446408262421,
        "TiO2": "No information",
        "Al2O3": 0.0,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 6.913712734412498,
        "CaO": 0.0,
        "Na2O": 10.63182318296328,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.38e-07,
        "SiO2": 67.31225105403928,
        "TiO2": "No information",
        "Al2O3": 16.31813165216256,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 6.450349084493427,
        "CaO": 0.0,
        "Na2O": 9.919268209304738,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 3.31e-07,
        "SiO2": 60.47759978778918,
        "TiO2": "No information",
        "Al2O3": 23.68355036267394,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 6.241203370410868,
        "CaO": 0.0,
        "Na2O": 9.597646479126022,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 1.05e-07,
        "SiO2": 70.99650549202799,
        "TiO2": "No information",
        "Al2O3": 16.06386581391881,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 3.174920522610949,
        "CaO": 0.0,
        "Na2O": 9.76470817144224,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 3.31e-07,
        "SiO2": 63.50948886829985,
        "TiO2": "No information",
        "Al2O3": 16.58057620670492,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 9.83113509883213,
        "CaO": 0.0,
        "Na2O": 10.0787998261631,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 6.76e-07,
        "SiO2": 59.58240758966843,
        "TiO2": "No information",
        "Al2O3": 16.85160054282749,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 13.32244505078141,
        "CaO": 0.0,
        "Na2O": 10.24354681672267,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS1",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 7.08e-07,
        "SiO2": 52.79034448650031,
        "TiO2": "No information",
        "Al2O3": 24.43191021746902,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 12.87682953440664,
        "CaO": 0.0,
        "Na2O": 9.900915761624018,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 3.24e-07,
        "SiO2": 62.40961005973729,
        "TiO2": "No information",
        "Al2O3": 16.29342818003241,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 6.440584117385974,
        "CaO": 0.0,
        "Na2O": 14.85637764284433,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    },
    {
        "melt": "NCMAS",
        "diffusing species": "Fe",
        "type of experiment": "electrochemistry",
        "test temperature": 1573.15,
        "pressure": "No information",
        "diffusivity": 3.55e-07,
        "SiO2": 57.52179051523218,
        "TiO2": "No information",
        "Al2O3": 16.26879939035861,
        "FeOt": "No information",
        "MnO": "No information",
        "MgO": 6.430848671299929,
        "CaO": 0.0,
        "Na2O": 19.77856142310928,
        "K2O": "No information",
        "P2O5": "No information",
        "H2Ot": "No information"
    }
]'''
    collection = [read_grobid(f) for f in os.listdir('./text') if f.endswith('.tei.xml')]
    collection.sort(key=lambda x: x['title'])
    exemplar_text = ""
    abstract = ""
    for i, entry in enumerate(collection):
        if entry['title'] == "The effect of glass composition on the thermodynamics of the Fe 2+ /Fe 3+ equilibrium and the iron diffusivity in Na 2 O/MgO/CaO/Al 2 O 3 /SiO 2 melts":
            abstract = entry['abstract']
            # pprint(entry_text)
            exemplar_text = "\n".join(section for section in entry['body'])
            break

    exemplar_text = f"{abstract}\n{exemplar_text}"
    # pprint(exemplar_text)
    return exemplar_text, exemplar_op


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
                if not os.path.exists("extracted_info/schema_1shot_complex"):
                    os.makedirs("extracted_info/schema_1shot_complex")

                # # # saving the information to a file
                with open(
                        f"extracted_info/schema_1shot_complex/{titles_to_dois[entry['title']].replace('/', '.')}_extracted_info.json",
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
                            f"extracted_info/schema_1shot_complex/{titles_to_dois[entry['title']].replace('/', '.')}_extracted_info.json",
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
        with open("extracted_info/schema_1shot_complex/failed_DOIs.json", "a") as f:
            json.dump(failed, f, indent=4)

if __name__=='__main__':
    run()