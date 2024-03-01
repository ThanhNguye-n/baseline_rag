from llmsherpa.readers import LayoutPDFReader
from typing import List

def chunking_to_get_text(name_file_pdf: str) -> List[str]:
        
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
        docs = pdf_reader.read_pdf(filename)

        # Get a list of sections and chunks from documents
        # A Chunk is getting from splitting the document into paragraphs, lists, and tables
        # A section is a block of text. It can have children such as paragraphs, lists, and tables. A section has tag 'header'.
        list_sections, list_chunks = docs.sections(), docs.chunks()

        # If include_children True then the text of the children are also included
        # If recurse True then the text of the children's children are also included
        text_from_sections = [list_sections[i].to_text(include_children=True, recurse=False) for i in range(len(list_sections))]

        # Get text from chunks but ignore table class, only get text from list_item and paragraph
        text_from_chunks = []
        for i in range(len(list_chunks)):
            if list_chunks[i].tag in ['list_item', 'para']: #irgnore class table
                text_from_chunks.append(list_chunks[i].to_text())


        return text_from_sections + text_from_chunks