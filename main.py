import pdf_parser
import question_handler

INPUT_PDF_FOLDER_PATH = "input_data/pdf"
INPUT_QUESTIONS_FOLDER_PATH = "input_data/questions"
OUTPUT_FOLDER_PATH = "output_data"


def main():
    pdf_parser.run_all(INPUT_PDF_FOLDER_PATH, OUTPUT_FOLDER_PATH)
    question_handler.run(OUTPUT_FOLDER_PATH, INPUT_QUESTIONS_FOLDER_PATH)


if __name__ == "__main__":
    main()
