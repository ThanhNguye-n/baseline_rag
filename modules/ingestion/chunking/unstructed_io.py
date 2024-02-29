from unstructured.chunking.title import chunk_by_title
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.doc import partition_docx
from unstructured.documents.elements import Element
from typing import Optional, List



def partition_pdf_to_element(name_file_pdf: str, file_type):
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
            infer_table_structure=True
        )


def chunking_pdf(
        name_file_pdf: str, 
        file_type: str,
        max_characters: int = 10**5,
        new_after_n_chars: Optional[int] = None,
        overlap: int = 0,
        overlap_all: bool = False,
) -> List[Element]:
    
    """
    Uses title elements to identify sections within the document for chunking.
    Chunking produces a sequence of CompositeElement, Table, or TableChunk elements.
    """

    elements_pdf = partition_pdf_to_element(name_file_pdf, file_type)

    return chunk_by_title(
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