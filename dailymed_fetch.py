import xml.etree.ElementTree as ET
from urllib.parse import quote

import requests


def get_xml(set_id):
    base_url = "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/"
    url = f"{base_url}{quote(set_id)}.xml"
    # perform a get request on the link to get the xml data
    response = requests.get(url)
    return response.content


def parse_xml(xml_content):
    root = ET.fromstring(xml_content)

    # Define XML namespcae for the xml as per dailymed specification
    NS = "{urn:hl7-org:v3}"

    # Get data From the XML
    set_id_el = root.find(f"{NS}setId")
    set_id = set_id_el.attrib.get("root") if set_id_el is not None else None

    # Get the physical form of the medicine
    med_form_el = root.find(f".//{NS}manufacturedProduct/{NS}formCode")
    med_form = (
        med_form_el.attrib.get("displayName") if med_form_el is not None else None
    )

    # get the title of the spl document
    title_el = root.find(f"{NS}title")
    if title_el is not None:
        title = " ".join(
            [
                ET.tostring(values, encoding="unicode", method="text").strip()
                for values in title_el
            ]
        )

    # Get the usage Route of the medicine
    route_el = root.find(f".//{NS}routeCode")
    route = route_el.attrib.get("displayName") if route_el is not None else None

    # get the description of the medicine
    description = None
    for section in root.findall(f".//{NS}section"):
        code_el = section.find(f"{NS}code")
        if (
            code_el is not None
            and code_el.attrib.get("displayName") == "DESCRIPTION SECTION"
        ):
            text_el = section.find(f"{NS}text")
            if text_el is not None:
                paragraph_el = text_el.findall(f"{NS}paragraph")
                description = "\n".join(
                    [
                        ET.tostring(p, encoding="unicode", method="text").strip()
                        for p in paragraph_el
                    ]
                )
            break

    medicine_info = {
        "set_id": set_id,
        "title": title,
        "form": med_form,
        "route": route,
        "description": description,
    }
    return medicine_info


def main():
    set_id = "1efe378e-fee1-4ae9-8ea5-0fe2265fe2d8"
    xml_content = get_xml(set_id)
    xml_data = parse_xml(xml_content)
    print(f"setid: {xml_data['set_id']}")
    print(f"title: {xml_data['title']}")
    print(f"form: {xml_data['form']}")
    print(f"route: {xml_data['route']}")
    print(f"description: {xml_data['description']}")
    return


if __name__ == "__main__":
    main()
