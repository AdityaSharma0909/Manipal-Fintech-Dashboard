import dicttoxml
import lxml.etree as ET
import pdfkit
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from application.models import LoanDocument


def convert_cibil_json_to_pdf(data, file_name,application):
    try:
        # Convert JSON to XML
        xml_data = dicttoxml.dicttoxml(data)

        # Parse the XML string
        root = ET.fromstring(xml_data)
        newroot = ET.Element("Root")
        newroot.insert(0, root)
        tree = ET.ElementTree(newroot)

        # Convert the ElementTree to a pretty-printed XML string
        final_xml = ET.tostring(tree.getroot(), encoding="utf-8", xml_declaration=True, method="xml", pretty_print=True)

        # Parse the XSLT file
        xslt_doc = ET.parse("./python_cir_JSONConverter_v2.xslt")
        xslt_transform = ET.XSLT(xslt_doc)

        # Parse the XML string for transformation
        source_doc = ET.fromstring(final_xml)
        output_doc = xslt_transform(source_doc)

        # Convert the transformed HTML output to PDF
        html_str = ET.tostring(output_doc, pretty_print=True, encoding="unicode")  # Get HTML as a string
        pdf = pdfkit.from_string(html_str,False)  # Convert HTML string to PDF
        try:
            document = LoanDocument.objects.get(application=application,document_type='CIBIL_REPORT')
            document.file.delete()  # Delete the old file if it exists

            document.file.save(file_name, ContentFile(pdf))
            document.save()
        except ObjectDoesNotExist:
            document = LoanDocument(document_type='CIBIL_REPORT',
                                    file_name=file_name,
                                    application=application)
            document.file.save(file_name, ContentFile(pdf))
            document.save()

        # Prepare the HTTP response
        response = HttpResponse(pdf,content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename={file_name}'
        response["Access-Control-Expose-Headers"] = 'Content-Disposition'

        print("Report created Successfully")

        return response

    except Exception as e:
        print(f"An error occurred: {e}")
        return HttpResponse(status=500, content="An error occurred while generating the PDF.")
