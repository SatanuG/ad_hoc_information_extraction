import json
from typing import List, Optional

from langchain.chains import create_structured_output_runnable
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_text_splitters import TokenTextSplitter
from parsing_tei_xml import read_grobid
import os


with open("../openAI_key", "r") as f:
    key = f.read().strip()



class Diffusion(BaseModel):

    melt: Optional[str] = Field(description="The melt in which the diffusion is taking place.")
    diffusing_species: Optional[str] = Field(description="The element/compound that is diffusing.")
    test_temperature: Optional[float] = Field(description="The temperature at which the diffusion is being tested.")
    diffusivity: Optional[float] = Field(description="The rate at which the species is diffusing through the melt.")
    SiO2: Optional[float] = Field(description="The concentration of SiO2 in the melt.")
    TiO2: Optional[float] = Field(description="The concentration of TiO2 in the melt.")



class ExtractionData(BaseModel):
    diffusion: List[Diffusion]



prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert at identifying elements diffusing into a silicate melt and their associated properties. "
            "Only extract information that is related to diffsuion. Extract nothing if no important information can be found in the text.",
        ),

        (
            "human",
            "{text}"
        ),
    ]
)


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

        llm = ChatOpenAI(
            model="gpt-4-0125-preview",
            openai_api_key=key,
            temperature=0.0,

        )

        extractor = prompt | llm.with_structured_output(
            schema=ExtractionData,
            method="function_calling",
            include_raw=False,
        )

        text_splitter = TokenTextSplitter(
            chunk_size=2000,
            chunk_overlap=20,
        )


        abstract = entry['abstract']
        entire_text = "\n".join(section for section in entry['body'])
        entire_text = f"{abstract}\n{entire_text}"

        texts = text_splitter.split_text(entire_text)

        diffusion_information = []

        if len(entire_text) < 100:
            failed[entry['doi']] = "Text too short"
            continue
        try:
            extractions = extractor.batch(
                [{"text": text} for text in texts],
                {"max_concurrency": 5},
            )

            for extraction in extractions:
                extraction_dict = [m.dict() for m in extraction.diffusion]
                diffusion_information.extend(extraction_dict)

            print(diffusion_information)

            if not os.path.exists("./extracted_info/langchain_0shot_simple"):
                os.makedirs("./extracted_info/langchain_0shot_simple")

            with open(f"./extracted_info/langchain_0shot_simple/{titles_to_dois[entry['title']].replace('/', '.')}.jsonl", "w") as f:
                json.dump(diffusion_information, f, indent=4)

        except Exception as e:
            print(f"Failed to process {entry['title']}: Error {e}")
            failed[entry['doi']] = str(e)
            continue

    if len(failed) > 0:
        with open("extracted_info/langchain_0shot_simple/failed_DOIs.json", "a") as f:
            json.dump(failed, f, indent=4)


if __name__=='__main__':
    run()