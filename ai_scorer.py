import pandas as pd
from openai import OpenAI
from os import getenv
from concurrent.futures import ThreadPoolExecutor

file_path = "responses_20240508-141247.xlsx"

df = pd.read_excel(file_path)
df_ai = pd.DataFrame(index=df.index)

# Get the columns with the title: 'Question' and 'Correct Answer'

answers = df['Answer']
correct_answers = df['Correct Answer']

client = OpenAI(base_url="https://openrouter.ai/api/v1",
                api_key=getenv("OPENROUTER_API_KEY"))

def process_answer(idx, answer, correct_answer):
    try: 
        response = client.chat.completions.create(
            temperature=0.0,
            model="meta-llama/llama-3-70b-instruct",
            # model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": """**You validate whether the provided answer correctly contains the specific correct answer, and ensure that it does not contain any prohibited 
                 information as specified. You will either confirm the answer as correct (1) or incorrect (0).**

                **Instructions:**
                1. You will be given two pieces of text: "answer" and "correct answer". Optionally, a "not_mention" field may be provided.
                2. Review the "answer" text to determine if it contains the "correct answer" exactly as stated and does not include any content listed in "not_mention".
                3. Respond only with '1' if the "answer" text correctly contains the "correct answer" and adheres to the "not_mention" condition (if applicable). 
                Respond with '0' if it does not meet these criteria.

                **Criteria for Response:**
                - Your output must strictly be a single character: '1' or '0'.
                - The response '1' should only be returned if the "correct answer" appears exactly within the "answer" text, and the "answer" 
                    text does not contain any text specified in "not_mention".
                - The "correct answer" should not consider variations in formatting or phrasing such as:
                  - Date formats (e.g., '1 Jan 2023' vs. 'January 1, 2023')
                  - Number formats (e.g., 'ten' vs. '10')
                  - The order of the information do not matter in the answer april 18 and 18 april are the same
                  - Abbreviations and full forms (e.g., 'St.' vs. 'Street')
                  - Synonyms and closely related terms (e.g., 'car' vs. 'automobile')
                - If "not_mention" is provided, ensure that none of the terms or information listed are included in the "answer".

                **Handling Ambiguities:**
                - If the correctness of an "answer" with respect to the "correct answer" is ambiguous, or if the "not_mention" condition 
                 is unclear due to interpretation or incomplete information in the text, default to a response of '0'.

                **Final Note:** Your response must remain consistent and reliable, focusing strictly on matching the "correct answer" and 
                 adhering to the "not_mention" condition (if provided). Avoid assumptions and ensure accuracy in detection of the correct answer."""},
                {"role": "user", "content": f"answer: {answer}, correct_answer: {correct_answer}"},
            ]
        )
        # print the current index 
        print(f"Index: {idx}")

        # Add the response to the dataframe in the colum 'AI Answer'
        df_ai.loc[idx, 'AI Answer'] = response.choices[0].message.content.replace('\n', '').replace(' ', '')

    except Exception as e:
        print(f"An error occurred: {str(e)}")

with ThreadPoolExecutor(max_workers=15) as executor:
    executor.map(process_answer, range(len(answers)), answers, correct_answers)

# Save the dataframe to a new excel file
df = pd.concat([df, df_ai], axis=1)
df.to_excel("res_test_with_ai.xlsx", index=False)
