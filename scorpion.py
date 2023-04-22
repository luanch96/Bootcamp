#!/usr/bin/env python3
# Project: arachnida
# Student: Biktor Garcia
# Module: scorpion.py
# Expected cmdline: scorpion.py file1 [file2] [file3]...
#
# NOTE: If running this script in MacOS, you'll need the exif module. If you don't have administrator
# privileges, you can install it in a venv with:
# python3 -m venv [/path/to/venv] && source [/path/to/venv]/bin/activate && 
# pip3 install exif pikepdf python-docx
# El segundo programa scorpion recibirá archivos de imagen como parámetros y será
# capaz de analizarlos en busca datos EXIF y otros metadatos, mostrándolos en pantalla.
# El programa será compatible, al menos, con las mismas extensiones que gestiona spider.
# Deberá mostrar atributos básicos como la fecha de creación, así como otros datos EXIF.
# El formato en el que se muestren los metadatos queda a tu elección.

# Images
from exif import Image
# Word documents
import docx
# PDF
import pikepdf

# Mime types to find 
import mimetypes
import sys

supported_file_formats = [
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/bmp",
    "image/gif",
]

def extract_word_doc_metadata(filename):
    try:
        docfile = docx.Document(filename)
    except:
        print("Error opening the file")
        return
    
    print("- Type: Word file")
    prop = docfile.core_properties
    for d in dir(prop):
        if not d.startswith('_'):
            print('  - ', d, ": ", getattr(prop, d))
            

def extract_pdf_metadata(filename):
    try:
        pdf = pikepdf.Pdf.open(filename)
    except:
        print("Error opening the file")
        return    

    print("- Type: PDF file")
    docinfo = pdf.docinfo
    for key, value in docinfo.items():
        print('  - ', key, ":", value)

def extract_image_metadata(filename):
    print('- Type: Image')
    try:
        fp = open(filename, "rb")
    except:
        print("Error opening the file")
        return
    img = Image(fp)
    if img.has_exif:
        for field in img.list_all():
            try:
                print('  - ', field, ": ", img.get(field))
            except:
                print("Failed to get", field, "exif data")
    else:
        print(" - This image doesn't seem to have EXIF metadata")

def find_file_type(filename):
    # Use MIME type to guess the filetype
    print("[FILE]: ", filename, end="")
    mime_type = mimetypes.guess_type(filename)[0]
    if mime_type not in supported_file_formats:
        print(": Unsupported file type: ", mime_type)
        return
    
    print("")
    if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        extract_word_doc_metadata(filename)
    elif mime_type == "application/pdf":
        extract_pdf_metadata(filename)
    else:
        extract_image_metadata(filename)


def main():
    if len(sys.argv) < 2:
        quit("Please, enter at least one filename as an argument!")
    else:
        for file in sys.argv[1:]:
            find_file_type(file)

if __name__ == "__main__":
    main()