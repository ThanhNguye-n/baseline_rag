from unstructured.chunking.title import chunk_by_title
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.doc import partition_docx
from typing import Optional, List



def _partition_to_element(
        name_file_pdf: str, 
        file_type: str = 'pdf'
):
    """
    Partitioning functions in unstructured allow users to extract structured content from a raw unstructured document. 
    These functions break a document down into elements such as Title, NarrativeText, and ListItem, enabling users 
    to decide what content they’d like to keep for their particular application
    """

    if file_type == 'pdf':

        return  partition_pdf(
            # Path of file pdf
            filename= f'./data/{name_file_pdf}',
            # "hi_res" strategy, the function use a layout detection model to identify document elements
            strategy = 'hi_res',
            # Use layout model (YOLOX) to get bounding boxes (for tables) and find titles
            # If True, any Table elements have a metadata field named "text_as_html" where the table's content is rendered into an html string 
            infer_table_structure = True, 
            # Using pdf format to find embedded image blocks to save and image dir 
            extract_images_in_pdf=True,
            # Path of image dir
            extract_image_block_output_dir=f'./image/{name_file_pdf}',
        )
    

    elif file_type == 'docx':
        
        return partition_docx(
            # Path of file pdf
            filename= f'./data/{name_file_pdf}',
            # Use layout model (YOLOX) to get bounding boxes (for tables) and find titles
            # If True, any Table elements have a metadata field named "text_as_html" where the table's content is rendered into an html string 
            infer_table_structure = True,
            include_page_breaks=True
        )


def chunking_to_get_table_image(
        name_file_pdf: str, 
        file_type: str,
        max_characters: int = 10**8,
        new_after_n_chars: Optional[int] = None,
        overlap: int = 0,
        overlap_all: bool = False
) -> List[dict]:
    
    """
    Uses title elements to identify sections within the document for chunking.
    Chunking produces a sequence of CompositeElement, Table, or TableChunk elements.

    But this function only return a string of html of table class. And extract Image to image'path.
    We only extract table so set default max_characters as 10**8 to not making table chunks
    """

    elements_pdf = _partition_to_element(name_file_pdf, file_type)

    list_chunks = chunk_by_title(
        # A list of unstructured elements. Usually the output of a partition function.
        elements=elements_pdf,
        # If True, sections can span multiple pages.
        multipage_sections=True,
        # The hard maximum size for a chunk. No chunk will exceed this number of characters
        max_characters=max_characters,
        # The “soft” maximum size for a chunk
        # This can be used in conjunction with max_characters to set a “preferred” size, 
        # like “I prefer chunks of around 1000 characters (soft size), but I’d rather have a chunk of 1500 (hard size) than resort to text-splitting
        new_after_n_chars=new_after_n_chars,
        # Only when using text-splitting to break up an oversized chunk,
        overlap = overlap,
        # Also apply overlap between “normal” chunks, not just when text-splitting
        overlap_all = overlap_all
    )

    list_json_table = []
    
    for chunk in list_chunks:

        if chunk.category == 'Table':

            list_json_table.append(
                {
                    'tag': 'table',
                    'level': -1,
                    'page_idx': chunk.metadata.page_number,
                    'filename': name_file_pdf,
                    'text': chunk.text,
                    'html_text': chunk.metadata.text_as_html

                }
            )
        
    return list_json_table
