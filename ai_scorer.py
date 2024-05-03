import pandas as pd
from openai import OpenAI
from os import getenv

file_path = "res_test.xlsx"

df = pd.read_excel(file_path)
df_ai = pd.DataFrame(index=df.index)

# Get the columns with the title: 'Question' and 'Correct Answer'

answers = df['Answer']
correct_answers = df['Correct Answer']

client = OpenAI()

for idx, (answer, correct_answer) in enumerate(zip(answers, correct_answers)):
    response = client.chat.completions.create(
        temperature=0.0,
        # model="gpt-4"
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": """YOU Validate whether the provided answer correctly contains the specific correct answer, irrespective of additional contextual information. You will either confirm the answer as correct (1) or incorrect (0).

        **Instructions:**
        1. You will be given two pieces of text: "answer" and "correct answer".
        2. Review the "answer" text to determine if it contains the "correct answer" correctly.
        3. Respond only with '1' if the "answer" text correctly contains the "correct answer". Respond with '0' if it does not.

        **Criteria for Response:**
        - Your output must strictly be '1' or '0'. 
        - The response '1' should only be returned if the "correct answer" appears in some variation within the "answer" text.
        - Do not consider different formatting or phrasing of the "correct answer" in the "answer" text like: , spacing and order.
            - Date formats (e.g., '1 Jan 2023' vs. 'January 1, 2023')
            - Number formats (e.g., 'ten' vs. '10')
            - Abbreviations and full forms (e.g., 'St.' vs. 'Street')
            - Synonyms and closely related terms (e.g., 'car' vs. 'automobile')
        - Ensure the assessment is only based on the presence and correctness of the "correct answer" within the "answer" text, and not on any external factors or additional information provided.

        **Prompt Example:**
        - answer: "Mickey Mouse's number is 69."
        - correct answer: "69"
        - LLM response: `1`

        - answer: "Stockholm is not mentioned in the table."
        - correct answer: "988,943"
        - LLM response: `0`

        **Handling Ambiguities:**
        - If the correctness of an "answer" with respect to the "correct answer" is ambiguous due to interpretation or incomplete information in the text, default to a response of '0'.

        **Final Note:** Your response must remain consistent and reliable, focusing strictly on matching the "correct answer" with the information provided in the "answer". Avoid assumptions and ensure accuracy in detection of the correct answer."""},
            {"role": "user", "content": f"answer: {answer}, correct_answer: {correct_answer}"},
        ]
    )

    print(f"Answer: {answer}")
    print(f"Correct Answer: {correct_answer}")
    print(f"AI Answer: {response.choices[0].message.content}")
    print("\n")

    # Add the response to the dataframe in the colum 'AI Answer'
    df_ai.loc[idx, 'AI Answer'] = response.choices[0].message.content

# Save the dataframe to a new excel file
df = pd.concat([df, df_ai], axis=1)
df.to_excel("res_test_with_ai.xlsx", index=False)
