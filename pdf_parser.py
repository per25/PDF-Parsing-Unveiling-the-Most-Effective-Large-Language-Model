from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredPDFLoader,
    PDFMinerLoader,
    PDFMinerPDFasHTMLLoader,
)
from io import StringIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
import os
import fitz as PyMuPDF
from tqdm import tqdm
from bs4 import BeautifulSoup
import re
import shutil


def performance_decorator(func):
    """
    A decorator that measures the performance metrics of a function and saves them to an Excel file.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function.

    """
    import time
    import psutil
    import pandas as pd
    import numpy as np
    import os

    def wrapper(*args, **kwargs):
        file_path = 'output_data/performance_metrics.xlsx'
        start_time = time.time()
        start_cpu = psutil.cpu_percent(interval=None)
        start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2

        result = func(*args, **kwargs)

        end_time = time.time()
        end_cpu = psutil.cpu_percent(interval=None)
        end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2

        if result is None: # is from the rest of them 
            # the additional metrics is a dict that have that can be llm_tokens, embedding_tokens and pages calls or just one of them
            llm_tokens = np.nan
            embedding_tokens = np.nan
            pages_calls = np.nan

            metrics = {
                'Tool': [func.__name__],
                'Execution Time (seconds)': [end_time - start_time],
                'CPU Usage (percent)': [end_cpu - start_cpu],
                'Memory Usage (MB)': [end_memory - start_memory],
                'llm_tokens': [llm_tokens],
                'embedding_tokens': [embedding_tokens],
                'pages_calls': [pages_calls]
            }
            df = pd.DataFrame(metrics)

            # Check if the file already exists
            if os.path.exists(file_path):
                with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                    df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
            else:
                df.to_excel(file_path, index=False)

        elif isinstance(result, list): # is from llama tesseract
            for item in result:
                df = pd.DataFrame(item, index=[0])  # Add index=[0] if item is a dictionary with scalar values
                df.insert(0, 'Tool', func.__name__)

                # Check if the file already exists
                if os.path.exists(file_path):
                    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                        df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
                else:
                    df.to_excel(file_path, index=False)
    

        else: # is from llama index 
                        # the additional metrics is a dict that have that can be llm_tokens, embedding_tokens and pages calls or just one of them
            llm_tokens = result.get('llm_tokens', 'N/A')
            embedding_tokens = result.get('embedding_tokens', 'N/A')
            pages_calls = result.get('pages_calls', 'N/A')

            metrics = {
                'Tool': [func.__name__],
                'Execution Time (seconds)': [end_time - start_time],
                'CPU Usage (percent)': [end_cpu - start_cpu],
                'Memory Usage (MB)': [end_memory - start_memory],
                'llm_tokens': [llm_tokens],
                'embedding_tokens': [embedding_tokens],
                'pages_calls': [pages_calls]
            }
            df = pd.DataFrame(metrics)

            # Check if the file already exists
            if os.path.exists(file_path):
                with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                    df.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
            else:
                df.to_excel(file_path, index=False)
        
        return result

    return wrapper


import PyPDF2

def get_number_of_pages(file_path):
    # Open the PDF file
    with open(file_path, "rb") as file:
        # Create PDF reader object
        pdf_reader = PyPDF2.PdfReader(file)
        # Get the number of pages
        number_of_pages = len(pdf_reader.pages)
        return number_of_pages


@performance_decorator
def process_pdf_file_PyPDF(file_path, output_file):
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    
    # Save the data to a text file for inspection
    with open(output_file, "w", encoding='utf-8') as f:
        for i, page in enumerate(pages):
            f.write(page.page_content)
            f.write("\n")  # Optional: add a newline between pages


@performance_decorator
def process_pdf_file_UnstructuredPDF_default_strategy(file_path, output_file):
    loader = UnstructuredPDFLoader(file_path, mode="elements")
    pages = loader.load_and_split()
    
    # Save the data to a text file for inspection
    with open(output_file, "w", encoding='utf-8') as f:
        for i, page in enumerate(pages):
            f.write(page.page_content)
            f.write("\n")  # Optional: add a newline between pages


@performance_decorator
def process_pdf_file_UnstructuredPDF_OCR_only_strategy(file_path, output_file):
    loader = UnstructuredPDFLoader(file_path, mode="elements", strategy='ocr_only')
    pages = loader.load_and_split()
    
    # Save the data to a text file for inspection
    with open(output_file, "w", encoding='utf-8') as f:
        for i, page in enumerate(pages):
            f.write(page.page_content)
            f.write("\n")


@performance_decorator
def process_pdf_file_UnstructuredPDF_hig_res_strategy(file_path, output_file):
    loader = UnstructuredPDFLoader(file_path, mode="elements", strategy='hi_res')
    pages = loader.load_and_split()
    
    # Save the data to a text file for inspection
    with open(output_file, "w", encoding='utf-8') as f:
        for i, page in enumerate(pages):
            f.write(page.page_content)
            f.write("\n")


@performance_decorator
def process_pdf_file_PDFMiner(file_path, output_file):
    loader = PDFMinerLoader(file_path)
    data = loader.load()

    # Save the data to a text file for inspection
    with open(output_file, "w", encoding='utf-8') as f:
        for i, page in enumerate(data):
            f.write(page.page_content)
            f.write("\n")


@performance_decorator
def process_pdf_file_PDFMiner_as_HTML(file_path, output_file):
    loader = PDFMinerPDFasHTMLLoader(file_path)
    data = loader.load()[0]   # entire PDF is loaded as a single Document
    # print(data)
    soup = BeautifulSoup(data.page_content,'html.parser')
    content = soup.find_all('div')

    # save the content to a html file 
    with open(output_file, "w", encoding='utf-8') as f:
        f.write(str(content))

    cur_fs = None
    cur_text = ''
    snippets = []   # first collect all snippets that have the same font size
    for c in content:
        sp = c.find('span')
        if not sp:
            continue
        st = sp.get('style')
        if not st:
            continue
        fs = re.findall('font-size:(\d+)px',st)
        if not fs:
            continue
        fs = int(fs[0])
        if not cur_fs:
            cur_fs = fs
        if fs == cur_fs:
            cur_text += c.text
        else:
            snippets.append((cur_text,cur_fs))
            cur_fs = fs
            cur_text = c.text
    snippets.append((cur_text,cur_fs))

    # print the snippets
    for s in snippets:
        # print(s)
        pass

@performance_decorator
def process_pdf_file_PyMuPDF(file_path, output_file):
    # TODO Add the ocr 

    doc = PyMuPDF.open(file_path) # open a document
    
    out = open(output_file, "wb") # create a text output
    
    for page in doc: # iterate the document pages
        text = page.get_text().encode("utf8") # get plain text (is in UTF-8)
        out.write(text) # write text of page
        out.write(bytes((12,))) # write page delimiter (form feed 0x0C)
    
    out.close()


@performance_decorator
def process_pdf_file_pdfminerSix(file_path, output_file):
    output_string = StringIO()
    with open(file_path, 'rb') as f:
        extract_text_to_fp(f, output_string, laparams=LAParams())

    # Save the data to a text file for inspection
    with open(output_file, "w", encoding='utf-8') as f:
        f.write(output_string.getvalue().strip())


@performance_decorator
def process_pdf_file_textract_with_correction(file_path, output_file):
    import tesseract_with_llama2_corrections as tesseract_with_llama2
    raw_ocr, corrected_text, filter_text, performance_metrics= tesseract_with_llama2.tesseract_with_llm_correction(file_path)
    with open(output_file + "_raw_ocr.md", "w", encoding='utf-8') as f:
        f.write(raw_ocr)
    with open(output_file + "_corrected", "w", encoding='utf-8') as f:
        f.write(corrected_text)
    with open(output_file + "_fileted.md", "w", encoding='utf-8') as f:
        f.write(filter_text)

    return performance_metrics    

@performance_decorator
def process_pdf_file_llama_index_md(file_path, output_file):
    import nest_asyncio 
    from llama_parse import LlamaParse
    from os import getenv

    nest_asyncio.apply()

    key = getenv("LlamaIndex")

    parser = LlamaParse(
        api_key=key,
        result_type="markdown",
        num_workers=4,
        verbose=True,
        language="en"
    )

    # sync 
    document = parser.load_data(file_path)

    with open(output_file, "w", encoding='utf-8') as f:
        f.write(document[0].text)


@performance_decorator
def process_pdf_file_llama_index_md(file_path, output_file):
    import nest_asyncio 
    from llama_parse import LlamaParse
    from os import getenv

    nest_asyncio.apply()

    key = getenv("LlamaIndex")

    parser = LlamaParse(
        api_key=key,
        result_type="markdown",
        num_workers=4,
        verbose=True,
        language="en"
    )

    # sync 
    document = parser.load_data(file_path)

    with open(output_file, "w", encoding='utf-8') as f:
        f.write(document[0].text)
    
    return {'pages_calls': get_number_of_pages(file_path)}


@performance_decorator
def process_pdf_file_llama_index_txt(file_path, output_file):
    import nest_asyncio 
    from llama_parse import LlamaParse
    from os import getenv

    nest_asyncio.apply()

    key = getenv("LlamaIndex")

    parser = LlamaParse(
        api_key=key,
        result_type="text",
        num_workers=4,
        verbose=True,
        language="en"
    )

    # sync 
    document = parser.load_data(file_path)
    
    with open(output_file, "w", encoding='utf-8') as f:
        f.write(document[0].text)

    return {'pages_calls': get_number_of_pages(file_path)}


def reset_performance_metrics_file():
    """
    Resets the performance metrics file by clearing its contents and adding a header.
    """
    with open('output_data/performance_metrics.txt', 'w') as f:
        f.write("Performance metrics for each function:\n\n")

    # clear the excel file
    if os.path.exists('output_data/performance_metrics.xlsx'):
        os.remove('output_data/performance_metrics.xlsx')

    import pandas as pd

    df = pd.DataFrame(columns=['Tool', 'Execution Time (seconds)', 'CPU Usage (percent)', 'Memory Usage (MB)', 'llm_tokens', 'embedding_tokens', 'pages_calls'])
    df.to_excel('output_data/performance_metrics.xlsx', index=False)


def clear_output_files(path):
    """
    Clears all the files and folders in path directory with extensions '.txt', '.html', and '.md'.
    """
    for file in os.listdir(path):
        if file.endswith(".txt") or file.endswith(".html") or file.endswith(".md"):
            os.remove(os.path.join(path, file))
        elif os.path.isdir(os.path.join(path, file)):
            shutil.rmtree(os.path.join(path, file))


def run_all(input_folder_path, output_folder_path) -> None:
    """
    Runs all the PDF processing functions and saves the output to respective files.
    """
    
    # get all the files in the folder
    files = os.listdir(input_folder_path)
    
    clear_output_files(output_folder_path)
    reset_performance_metrics_file()

    for file in files:
        print("file: ", file)
        output_path = os.path.join(output_folder_path, file.split(".")[0])
        input_path = os.path.join(input_folder_path, file)
        print("output_path: ", output_path)
        # create a folder for the output data in the output folder
        if not os.path.exists(file.split(".")[0]):
            path = os.path.join(output_folder_path, file.split(".")[0])
            os.makedirs(path)

        tasks = [
            (process_pdf_file_PyPDF, (input_path, os.path.join(output_path, "PyPDF.txt"))),
            (process_pdf_file_UnstructuredPDF_hig_res_strategy, (input_path, os.path.join(output_path, "Unstructured_hi_res.txt"))),
            (process_pdf_file_UnstructuredPDF_default_strategy, (input_path, os.path.join(output_path, "Unstructured.txt"))),
            (process_pdf_file_UnstructuredPDF_OCR_only_strategy, (input_path, os.path.join(output_path, "Unstructured_OCR.txt"))),
            (process_pdf_file_PDFMiner, (input_path, os.path.join(output_path, "PDFMiner.txt"))),
            (process_pdf_file_PDFMiner_as_HTML, (input_path, os.path.join(output_path, "PDFMiner_HTML.html"))),
            (process_pdf_file_PyMuPDF, (input_path, os.path.join(output_path, "PyMuPDF.txt"))),
            (process_pdf_file_pdfminerSix, (input_path, os.path.join(output_path, "pdfminerSix.txt"))),
            (process_pdf_file_textract_with_correction, (input_path, os.path.join(output_path, "textract"))),       
            (process_pdf_file_llama_index_md, (input_path, os.path.join(output_path, "llama_index.md"))),
            (process_pdf_file_llama_index_txt, (input_path, os.path.join(output_path, "llama_index.txt")))
        ]

        with tqdm(total=len(tasks)) as pbar:
            for task in tasks:
                func, args = task
                pbar.set_description(f"Processing {args[1]}")
                try:
                    func(*args)
                except Exception as e:
                    print(f"\nAn error occurred while processing {args[1]}: {str(e)}")
                    print("Press any key to continue...")
                    input()
                pbar.update()
