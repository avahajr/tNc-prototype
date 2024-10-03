import re

from thefuzz import process

from openai import OpenAI
from termcolor import cprint

from openai_secrets import SECRET_KEY
from privacy_policy import PrivacyPolicy

company_name = ""


def split_into_blocks(text, n):
    words = text.split()  # Split the string into words (space-separated)
    # Group words into blocks of 'n'
    blocks = [' '.join(words[i:i + n]) for i in range(0, len(words), n)]
    return blocks


while True:
    company_name = input("Enter the name of the company whose privacy policy you want to review: ")
    if company_name.lower() not in ['apple', 'google', 'proton', 'reddit', 'openai']:
        print("Please enter a valid company name.")
    else:
        break

# Create a PrivacyPolicy object
policy = PrivacyPolicy(company_name)
print("Path to policy:", policy.path)

system_message = (f"You are a trying to help user understand the privacy policy of a service ({company_name}) they "
                  "want to use. Provide minimal answers.")

print()
cprint(f"Suggested questions for {company_name.title()}'s privacy policy:", "green")
client = OpenAI(api_key=SECRET_KEY)
question_suggestions = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system",
         "content": system_message},
        {"role": "user",
         "content": "Suggest 5 questions about this privacy policy that a person trying to safeguard their "
                    f"data would want answered. Separate the questions by a newline character.\n{policy.policy_text}"},
    ]
)

print(question_suggestions.choices[0].message.content)

print("=" * 100)

question_to_answer = input("Input the question you want answered (1-5) or ask a different question: ")

if question_to_answer in ['1', '2', '3', '4', '5']:
    question = question_suggestions.choices[0].message.content.split("\n")[int(question_to_answer) - 1]
else:
    question = question_to_answer

cprint(f"Question: {question}", "green")
print()

answer = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system",
         "content": system_message},
        {"role": "assistant",
         "content": policy.policy_text},
        {"role": "user",
         "content": f"{question}\nThe structure of the answer should be a summary, followed by one or more quotations "
                    f"from the summary where you got that information. Wrap the quotes in "
                    "quotation marks. Sample answer:\nThe policy states that <company_name> collects data on "
                    "users.\n\"We collect data on users.\""}
    ]
)
for i in range(len(answer.choices)):
    print(f"Model's answer (index {i}):")
    print('=' * 100)
    answer_text = answer.choices[0].message.content
    print(answer_text)
    quotes = re.findall(r'\"(.*?)\"', answer_text)

    blocks = split_into_blocks(policy.policy_text, 10)

    number_of_matches = 0
    print("Quotes found in the answer:")

    for j, quote in enumerate(quotes, start=1):
        print(f'{j}. {quote}')
        print("="*100)
        match, score = process.extractOne(quote, blocks)
        if score > 80:
            number_of_matches += 1
            sentences = re.findall(r'[^.!?]*' + re.escape(match) + r'[^.!?]*[.!?]', policy.policy_text)
            for sentence in sentences:
                print(f"Match found:\n \"{sentence.strip()}\" (score: {score})")
                print("-" * 100)
    if number_of_matches == len(quotes):
        cprint("All quotes found in the policy text.", "green")
        break
