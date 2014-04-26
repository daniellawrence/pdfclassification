#!/usr/bin/env python
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
from collections import defaultdict
import sys
import yaml

raw_classifications = open('classifications.yaml').read()
doctypes = yaml.load(raw_classifications)


def movefile(path, destination):
    print "Moving file %s to %s" % (path, destination)


def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    str = retstr.getvalue()
    retstr.close()
    return str


def make_classification(text):


    maybe_docs = defaultdict(int)

    for doctypes_name, docstrings in doctypes.items():
        for string in docstrings:
            if string in text:
                maybe_docs[doctypes_name] += text.count(string) * 10
                continue
            if string.lower() in text.lower():
                maybe_docs[doctypes_name] += text.count(string) * 5
                continue

    if not maybe_docs:
        classification = 'unknown'
        classification_score = -99
        return classification, classification_score

    classification, classification_score = sorted(maybe_docs.iteritems())[0]

    if classification_score < 50:
        classification = 'unsure'
        classification_score = -1
    
    return classification, classification_score


def findbarcode(pdf):
    import os
    os.popen("rm /tmp/x*.png").read()
    os.popen("convert -density 300 %s /tmp/x.png" % pdf).read()
    barcode = os.popen("zbarimg -q /tmp/x*.png").read().strip()
    if barcode:
        print "%s has a barcode of %s" % (pdf, barcode)


def main():
    import os

    pdffiles = []

    if len(sys.argv) == 1:
        for root, dirnames, filenames in os.walk("/home/dannyla"):
            for filename in filenames:
                if filename.lower().endswith('pdf'):
                    pdffiles.append(os.path.join(root, filename))
    else:
        pdffiles = sys.argv[1:]

    for pdf in pdffiles:
        pdf_strings = convert_pdf_to_txt(pdf)
        classification, classification_score = make_classification(pdf_strings)
        print "%s is a %s document (score:%d)" % (pdf, classification, classification_score)
        findbarcode(pdf)
        movefile(pdf, classification)

if __name__ == '__main__':
    main()
