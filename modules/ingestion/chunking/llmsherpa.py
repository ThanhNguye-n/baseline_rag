from llmsherpa.readers import LayoutPDFReader


def chunking_pdf(name_file_pdf:str):
    """
    LayoutPDFReader does smart chunking keeping related text due to document structure together:

    All list items are together including the paragraph that precedes the list.
    Items in a table are chuncked together
    Contextual information from section headers and nested section headers is included

    """
    
    filename = f'./data/{name_file_pdf}'
    # API support read pdf
    llmsherpa_api_url = "https://readers.llmsherpa.com/api/document/developer/parseDocument?renderFormat=all"
    pdf_reader = LayoutPDFReader(llmsherpa_api_url)

    # Reads PDF content and understands hierarchical layout of the document sections and structural components 
    doc = pdf_reader.read_pdf(filename)

    return doc.chunks()

