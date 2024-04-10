from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import PDFMinerLoader
from langchain_community.document_loaders import PDFMinerPDFasHTMLLoader
from bs4 import BeautifulSoup
import re
import time 
import psutil
import os
import fitz 

FILE_PATH = "input_data/test1.pdf"


def performance_decorator(func):
    """
    A decorator that measures the performance metrics of a function.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function.

    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_cpu = psutil.cpu_percent(interval=None)
        start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2

        result = func(*args, **kwargs)

        end_time = time.time()
        end_cpu = psutil.cpu_percent(interval=None)
        end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2

        metrics = f"Execution time: {end_time - start_time} seconds\n"
        metrics += f"CPU usage: {end_cpu - start_cpu} percent\n"
        metrics += f"Memory usage: {end_memory - start_memory} MB\n"

        with open('output_data/performance_metrics.txt', 'a') as f:
            f.write(f"Performance metrics for {func.__name__}:\n")
            f.write(metrics)
            f.write("\n")

        return result
    return wrapper


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
def process_pdf_file_UnstructuredPDF(file_path, output_file):
    loader = UnstructuredPDFLoader(file_path, mode="elements")
    pages = loader.load_and_split()
    
    # Save the data to a text file for inspection
    with open(output_file, "w", encoding='utf-8') as f:
        for i, page in enumerate(pages):
            f.write(page.page_content)
            f.write("\n")  # Optional: add a newline between pages


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

    doc = fitz.open(file_path) # open a document
    
    out = open(output_file, "wb") # create a text output
    
    for page in doc: # iterate the document pages
        text = page.get_text().encode("utf8") # get plain text (is in UTF-8)
        out.write(text) # write text of page
        out.write(bytes((12,))) # write page delimiter (form feed 0x0C)
    
    out.close()


def reset_performance_metrics_file():
    with open('output_data/performance_metrics.txt', 'w') as f:
        f.write("Performance metrics for each function:\n\n")


def run_all() -> None:
    """
    Runs all the PDF processing functions and saves the output to respective files.
    """
    reset_performance_metrics_file()
    process_pdf_file_PyPDF(FILE_PATH, "output_data/test1_PyPDF.txt")
    process_pdf_file_UnstructuredPDF(FILE_PATH, "output_data/test1_UnstructuredPDF.txt")
    process_pdf_file_PDFMiner(FILE_PATH, "output_data/test1_PDFMiner.txt")
    process_pdf_file_PDFMiner_as_HTML(FILE_PATH, "output_data/test1_PDFMiner_as_HTML.html")
    process_pdf_file_PyMuPDF(FILE_PATH, "output_data/test1_PyMuPDF.txt")
