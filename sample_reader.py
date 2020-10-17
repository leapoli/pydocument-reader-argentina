# -*- coding: utf-8 -*-

from document_reader import Document

while True:
    document = Document(input())
    if document.tipo_documento:
        print("Tipo documento: "+document.tipo_documento.value+" - Idioma teclado: "+document.teclado)
        print(document)
    else:
        print("Tipo de documento no reconocido")
    print("--------------------")
