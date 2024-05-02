import time
from openai import OpenAI
import os
import json
import pandas as pd
from os import getenv
from langsmith.wrappers import wrap_openai

client = OpenAI(base_url="https://openrouter.ai/api/v1",
                api_key=getenv("OPENROUTER_API_KEY"))

client = wrap_openai(client)

def get_questions(file_name, folder_path):
    try:
        # remove the extension from the file name
        file_name = file_name.split(".")[0]
        path = os.path.join(folder_path, file_name + "_questions.json")
        # load the json file
        content = None
        with open(path, "r") as file:
            content = json.load(file)

        return content
    except FileNotFoundError:
        print(f"File {path} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def prompt_model(model, messages, question):
    messages.append({"role": "user", "content": question})
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    messages.append({"role": "assistant", "content": response.choices[0].message.content})
    return response.choices[0].message.content


def run(output_folder_path, questions_folder_path):
    # get all the folders in the output folder 
    folders = [f for f in os.listdir(output_folder_path) if os.path.isdir(os.path.join(output_folder_path, f))]
    print(folders)

    models = ["gpt-3.5-turbo", "meta-llama/llama-3-8b-instruct:nitro"]

    data = {'Model': [], 'Folder': [], 'File': [], 'Question': [], 'Answer': [], 'Correct Answer': []}
    df = pd.DataFrame(data)

    for folder in folders:
        # get all the files in the folder 
        files = os.listdir(os.path.join(output_folder_path, folder))
        print(files)
        filedata = get_questions(folder, questions_folder_path)
        for file in files:
            path = os.path.join(output_folder_path, folder, file)
            
            content = None
            
            try:
                with open(path, "r", encoding="utf8", errors="ignore") as f:
                    content = f.read()
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                print("When reading the file: " + path)
                print("Press any key to continue...")
                input()
                continue

            for llm in models:
            
                conversation = [{"role": "system", "content": "Based on the information provided give short and concise answers to the following questions"},
                                {"role": "user", "content": content}]
            
                questions = filedata["questions"]
                for data in questions:
                    question = data["question"]
                    print("question:" + question)
                    response = prompt_model(llm, conversation, question)
                    print("response:" + response)
                    df = df._append({'Model': llm,
                                    'Folder': folder, 
                                    'File': file, 
                                    'Question': question, 
                                    'Answer': response,
                                    'Correct Answer': data["answer"]}, 
                                    ignore_index=True)

    # Create a results folder if it doesn't exist
    if not os.path.exists('results'):
        os.makedirs('results')

    # Get the current timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")

    # Save the dataframe to an Excel file with the timestamp as the filename
    while True:
        try:
            df.to_excel(f'results/responses_{timestamp}.xlsx', index=False)
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please close the file and press Enter to try again.")
            input()
            continue

run("output_data", "input_data/questions")