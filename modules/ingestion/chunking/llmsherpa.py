from llmsherpa.readers import LayoutPDFReader
from typing import List

class ChunkText:

    def __init__(self):
        
        super().__init__()

        # API support read pdf
        llmsherpa_api_url = "https://readers.llmsherpa.com/api/document/developer/parseDocument?renderFormat=all"
        self.pdf_reader = LayoutPDFReader(llmsherpa_api_url)
        

    def chunking(
            self, 
            name_file_pdf: str,
            get_section_header=True,
            get_small_chunks=True
    ) -> List[dict]:
            
            """
            LayoutPDFReader does smart chunking keeping related text due to document structure together:

            All list items are together including the paragraph that precedes the list.
            Items in a table are chuncked together
            Contextual information from section headers and nested section headers is included

            """

            filename = f'./data/{name_file_pdf}'

            # Reads PDF content and understands hierarchical layout of the document sections and structural components 
            docs = self.pdf_reader.read_pdf(filename)
            
            # Get a list of sections and chunks from documents
            # A Chunk is getting from splitting the document into paragraphs, lists, and tables
            # A section is a block of text. It can have children such as paragraphs, lists, and tables. A section has tag 'header'.
            list_sections, list_chunks = docs.sections(), docs.chunks()
            list_json_sections, list_json_chunks = [], []

            # If include_children True then the text of the children are also included
            # If recurse True then the text of the children's children are also included
            # Get text from sections
            for sec in list_sections:

                list_json_sections.append(
                    {
                        'tag': 'header',
                        'level': sec.level,
                        'page_idx': sec.page_idx,
                        'filename': name_file_pdf,
                        'text': sec.to_text(include_children=True, recurse=False),
                        'html_text': sec.to_html(include_children=True, recurse=False)
                    }
                )


            # Get text from chunks but ignore table class, only get text from list_item and paragraph
            for chunk in list_chunks:

                if chunk.tag in ['list_item', 'para']: #irgnore class table

                    list_json_chunks.append(
                        {
                            'tag': chunk.tag,
                            'level': chunk.level,
                            'page_idx': chunk.page_idx,
                            'filename': name_file_pdf,
                            'text': chunk.to_text(),
                            'html_text': chunk.to_html()
                        }
                    )

            if get_section_header and get_small_chunks:
                return list_json_sections + list_json_chunks
            elif get_section_header:
                return list_json_sections
            elif get_small_chunks:
                return list_json_chunks