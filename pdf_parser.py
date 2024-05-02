from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredPDFLoader,
    PDFMinerLoader,
    PDFMinerPDFasHTMLLoader,
)
from io import StringIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
import time
import psutil
import os
import fitz
from tqdm import tqdm
from bs4 import BeautifulSoup
import re
import shutil


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

    doc = fitz.open(file_path) # open a document
    
    out = open(output_file, "wb") # create a text output
    
    for page in doc: # iterate the document pages
        text = page.get_text().encode("utf8") # get plain text (is in UTF-8)
        out.write(text) # write text of page
        out.write(bytes((12,))) # write page delimiter (form feed 0x0C)
    
    out.close()


def process_pdf_file_pdfminerSix(file_path, output_file):
    output_string = StringIO()
    with open(file_path, 'rb') as f:
        extract_text_to_fp(f, output_string, laparams=LAParams())

    # Save the data to a text file for inspection
    with open(output_file, "w", encoding='utf-8') as f:
        f.write(output_string.getvalue().strip())


def reset_performance_metrics_file():
    """
    Resets the performance metrics file by clearing its contents and adding a header.
    """
    with open('output_data/performance_metrics.txt', 'w') as f:
        f.write("Performance metrics for each function:\n\n")


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
            (process_pdf_file_UnstructuredPDF_hig_res_strategy, (input_path, os.path.join(output_path, "UnstructuredPDF_hi_res.txt"))),
            (process_pdf_file_UnstructuredPDF_default_strategy, (input_path, os.path.join(output_path, "UnstructuredPDF.txt"))),
            (process_pdf_file_UnstructuredPDF_OCR_only_strategy, (input_path, os.path.join(output_path, "UnstructuredPDF_OCR.txt"))),
            (process_pdf_file_PDFMiner, (input_path, os.path.join(output_path, "PDFMiner.txt"))),
            (process_pdf_file_PDFMiner_as_HTML, (input_path, os.path.join(output_path, "PDFMiner_as_HTML.html"))),
            (process_pdf_file_PyMuPDF, (input_path, os.path.join(output_path, "PyMuPDF.txt"))),
            (process_pdf_file_pdfminerSix, (input_path, os.path.join(output_path, "pdfminerSix.txt")))
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
