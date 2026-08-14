# from io import BytesIO
# from django.http import HttpResponse
# from django.template.loader import get_template
# from xhtml2pdf import pisa


# def render_to_pdf(context_dict: dict):
#     template = get_template("pdf2.html")
#     html = template.render(context_dict)
#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
#
#     if not pdf.err:
#         return HttpResponse(result.getvalue(), content_type="application/pdf")
#     return None

    

    # template_path = 'pdf2.html'
    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'filename="pledge_report.pdf"'
    # template = get_template(template_path)
    # html = template.render(context_dict)
    # # create a pdf
    # pisa_status = pisa.CreatePDF(
    #    html, dest=response)
    # # if error then show some funy view
    # if pisa_status.err:
    #    return HttpResponse('We had some errors <pre>' + html + '</pre>')
    # return response
