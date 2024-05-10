import json
import grobid_tei_xml
import os
from pprint import pprint


def read_grobid(filename):
    path = './text/'
    with open(path + filename, 'r') as xml_file:
        doc = grobid_tei_xml.parse_document_xml(xml_file.read())
    paper_contents = {}
    paper_contents['title'] = doc.header.title
    paper_contents['authors'] = [a.full_name for a in doc.header.authors]
    paper_contents['doi'] = str(doc.header.doi)
    paper_contents['abstract'] = doc.abstract
    try:
        paper_contents['body'] = doc.body.split("\n")
    except:
        paper_contents['body'] = []

    return paper_contents
if __name__=='__main__':

    pprint(read_grobid('A fine-grained NbMoTaWVCr refractory high-entropy alloy with ultra-high strength_ Microstructural evolution and mechanical properties.tei.xml'))