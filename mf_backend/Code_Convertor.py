import json
import dicttoxml
from lxml import etree
import lxml.etree as ET
import pdfkit

if __name__=='__main__':
    # Read the content of the file as a string
    with open("sample_cibil_report.txt", "r") as u:
        json_str = u.read()

    # Parse the JSON string
    json_data = json.loads(json_str)

    # Convert JSON to XML
    xml_data = dicttoxml.dicttoxml(json_data)

    # Parse the XML string
    root = ET.fromstring(xml_data)
    newroot = ET.Element("Root")
    newroot.insert(0, root)
    tree = ET.ElementTree(newroot)

    # Convert the ElementTree to a pretty-printed XML string
    final_xml = ET.tostring(tree.getroot(), encoding="utf-8", xml_declaration=True, method="xml", pretty_print=True)

    # Save the XML to a file
    # with open("Final1.xml", "wb") as f:
    #     tree.write(f, encoding="utf-8", xml_declaration=True, method="xml", pretty_print=True)

    # Parse the XSLT file
    xslt_doc = etree.parse("python_cir_JSONConverter_v2.xslt")
    # xslt_transform = etree.XSLT(xslt_doc)
    #
    # # Parse the XML string for transformation
    # source_doc = ET.fromstring(final_xml)
    # output_doc = xslt_transform(source_doc)
    #
    # # Save the transformed HTML output
    # with open("final2.html", "wb") as f:
    #     f.write(ET.tostring(output_doc, pretty_print=True))
    #
    # print("Report created Successfully")
    #
    # # If you want to convert the HTML to PDF, uncomment the following lines:
    #
    # pdfkit.from_file('final2.html', 'out.pdf')
    xslt_transform = ET.XSLT(xslt_doc)

    # Parse the XML string for transformation
    source_doc = ET.fromstring(final_xml)
    output_doc = xslt_transform(source_doc)

    # Convert the transformed HTML output to PDF
    html_str = ET.tostring(output_doc, pretty_print=True, encoding="unicode")  # Get HTML as a string
    pdf = pdfkit.from_string(html_str, 'test2.pdf')  # Convert HTML string to PDF

