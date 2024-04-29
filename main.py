import pdf_parser

INPUT_FOLDER_PATH = "input_data/pdf"
OUTPUT_FOLDER_PATH = "output_data"


def main():
    pdf_parser.run_all(INPUT_FOLDER_PATH, OUTPUT_FOLDER_PATH)


if __name__ == "__main__":
    main()
