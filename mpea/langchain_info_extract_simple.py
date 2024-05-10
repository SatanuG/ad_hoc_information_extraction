import json
from typing import List, Optional

from langchain.chains import create_structured_output_runnable
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_text_splitters import TokenTextSplitter
from parsing_tei_xml import read_grobid
import os


class MPEA(BaseModel):

    formula: str = Field(
        ..., description="High-entropy alloys (HEAs) are alloys that are formed by mixing equal or relatively large proportions of (usually) five or more elements"
    )
    yield_strength: float = Field(
        ..., description="The yield strength is often used to determine the maximum allowable load in a mechanical component, since it represents the upper limit to forces that can be applied without producing permanent deformation."
    )
    grain_size: Optional[float] = Field(
        ..., description="The grain size of a material is the average grain diameter, usually expressed in millimeters."
    )
    experimental_density: Optional[float] = Field(
        ..., description="The experimental density of a material is the mass of the material divided by its volume."
    )

    hardness: Optional[float] = Field(
        ..., description="=In materials science, hardness (antonym: softness) is a measure of the resistance to localized plastic deformation, such as an indentation (over an area) or a scratch (linear), induced mechanically either by pressing or abrasion."
    )

    test_temperature: Optional[float] = Field(
        ..., description="The temperature at which the material was tested."
    )

    ultimate_tensile_strength: Optional[float] = Field(
        ..., description="The ultimate tensile strength (UTS), often shortened to tensile strength (TS), ultimate strength, or Ftu within equations, is the maximum stress that a material can withstand while being stretched or pulled before necking, which is when the specimen's cross-section starts to significantly contract."
    )

    elongation: Optional[float] = Field(
        ..., description="In materials science, elongation deformation of a material under a tensile load and goes back to normal without it."
    )

    elongation_plastic: Optional[float] = Field(
        ..., description="The plastic elongation is the elongation of a material after the yield point and the deformation becomes permanent."
    )

    evidence: str = Field(
        ...,
        description="Repeat in verbatim the sentence(s) from which the year and description information were extracted",
    )


class ExtractionData(BaseModel):

    mpea_multi: List[MPEA]


# Define a custom prompt to provide instructions and any additional context.
# 1) You can add examples into the prompt template to improve extraction quality
# 2) Introduce additional parameters to take context into account (e.g., include metadata
#    about the document from which the text was extracted.)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert at identifying high entropy alloys and their associated properties. "
            "Only extract information that is related to high entropy alloys. Extract nothing if no important information can be found in the text.",
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

    for i, entry in enumerate(collection):
        if entry['title'] == "A fine-grained NbMoTaWVCr refractory high-entropy alloy with ultra-high strength: Microstructural evolution and mechanical properties":
            continue

        llm = ChatOpenAI(
            model="gpt-4-0125-preview",
            openai_api_key="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",
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


        print(f'Processing index {i + 1} of {len(collection)}')

        abstract = entry['abstract']
        entire_text = "\n".join(section for section in entry['body'])
        entire_text = f"{abstract}\n{entire_text}"

        texts = text_splitter.split_text(entire_text)

        mpea_information = []

        if len(entire_text) < 100:
            failed[entry['doi']] = "Text too short"
            continue
        try:
            extractions = extractor.batch(
                [{"text": text} for text in texts],
                {"max_concurrency": 5},
            )

            for extraction in extractions:

                extraction_dict = [m.dict() for m in extraction.mpea_multi]
                mpea_information.extend(extraction_dict)

            print(mpea_information)

            if not os.path.exists("./extracted_info/langchain_0shot_simple"):
                os.makedirs("./extracted_info/langchain_0shot_simple")


            with open(f"./extracted_info/langchain_0shot_simple/{entry['doi'].replace('/', '.')}.jsonl", "w") as f:
                json.dump(mpea_information, f, indent=4)

        except Exception as e:
            print(f"Failed to process {entry['title']}: Error {e}")
            failed[entry['doi']] = str(e)
            continue

    if len(failed) > 0:
        with open("extracted_info/langchain_0shot_simple/failed_DOIs.json", "a") as f:
            json.dump(failed, f, indent=4)

if __name__ == "__main__":
    run()