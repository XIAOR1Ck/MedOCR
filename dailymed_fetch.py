from urllib.parse import quote

import requests
from lxml import etree


def get_xml(set_id):
    base_url = "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/"
    url = f"{base_url}{quote(set_id)}.xml"
    # perform a get request on the link to get the xml data
    response = requests.get(url)
    return response.content


ns = {"hl7": "urn:hl7-org:v3"}
nms = "{urn:hl7-org:v3}"


def parse_xml(xml_content):
    tree = etree.fromstring(xml_content)
    # get medicine Name
    name_el = tree.xpath(".//hl7:genericMedicine/hl7:name", namespaces=ns)[0]
    medicine_name = etree.tostring(name_el, encoding="unicode", method="text")
    # Get SetId of the Medicine
    setid = tree.xpath("./hl7:setId/@root", namespaces=ns)[0]

    # Get dosage form of the medicine
    dosage_form = tree.xpath(
        ".//hl7:manufacturedProduct/hl7:formCode/@displayName", namespaces=ns
    )[0]

    # get use route of the medicine
    route = tree.xpath(".//hl7:routeCode/@displayName", namespaces=ns)[0]

    # get the component element to get the medicine data
    component_els = tree.xpath(".//hl7:structuredBody/hl7:component", namespaces=ns)

    # Initialize array to store section value:
    data_array = []
    # Iterate over each components to get extract data from each components
    for el in component_els:
        data = component_parse(el, 2)
        if len(data) != 0:
            data_array.append(data)
    return medicine_name, setid, dosage_form, route, data_array


## function to extract information from components ehich takes component element form the xml and the highest heading level for the title for html formatting
def component_parse(component_el, level):
    data = ""
    section_el = component_el.xpath("./hl7:section", namespaces=ns)
    for el in section_el:
        for child in el:
            if child.tag == f"{nms}title":
                data = (
                    data
                    + f"<h{level}> {etree.tostring(child, encoding='unicode', method='text')} </h{level}>"
                )
            if child.tag == f"{nms}text":
                data += text_parse(child)

            if child.tag == f"{nms}component":
                level += 1
                data += (
                    f"<div class='subSection'> {component_parse(child, level)} </div>"
                )
                level -= 1
    return data


def text_parse(text_el):
    data = ""
    for el in text_el:
        if el.tag == f"{nms}paragraph":
            data += f"<p> {etree.tostring(el, encoding='unicode', method='text')} </p>"

        if el.tag == f"{nms}table":
            data += table_parse(el)

        if el.tag == f"{nms}list":
            data += list_parse(el)
    return data


def list_parse(list_el):
    data = ""
    data += "<ul>"
    for child in list_el:
        data += f"<li> {etree.tostring(child, encoding='unicode', method='text')} </li>"
    data += "</ul>"
    return data


def table_parse(table_el):
    """
    Parse an lxml table element and return clean HTML table markup.

    Args:
        table_el: lxml table element to parse

    Returns:
        String containing clean HTML table markup
    """
    html = ["<table>"]  # Using list for more efficient string building

    for section in table_el:
        if section.tag.endswith("thead"):
            html.append("<thead>")
            for row in section:
                if row.tag.endswith("tr"):
                    html.append("<tr>")
                    for cell in row:
                        if cell.tag.endswith("td"):
                            # Handle th cells (header cells)
                            cell_text = etree.tostring(
                                cell, encoding="unicode", method="text", with_tail=False
                            ).strip()
                            html.append(f"<th>{cell_text}</th>")
                    html.append("</tr>")
            html.append("</thead>")

        elif section.tag.endswith("tbody"):
            html.append("<tbody>")
            for row in section:
                if row.tag.endswith("tr"):
                    html.append("<tr>")
                    for cell in row:
                        if cell.tag.endswith("td"):
                            # Handle colspan if present
                            colspan = (
                                f' colspan="{cell.get("colspan")}"'
                                if "colspan" in cell.attrib
                                else ""
                            )

                            # Get cell text content
                            cell_text = etree.tostring(
                                cell, encoding="unicode", method="text", with_tail=False
                            ).strip()
                            html.append(f"<td{colspan}>{cell_text}</td>")
                    html.append("</tr>")
            html.append("</tbody>")

    html.append("</table>")
    return "\n".join(html)
