import openai
import csv
import re
from Example2 import example

openai.api_key = "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"

def generate_ai_message(ID, link, name, about, experience):
    prompt = f"""
Create a LinkedIn InMail message based on the following:

Name: {name}
About: {about}
Experience: {experience}

Follow this template:

The message should reference specific things that are extremely personalized with the tone sounding professional but approachable and human.
The message needs to be a concise and dense as possible, making sure there are no filler words and each word is placed for its own meticulous purpose.

Each paragraph needs to have brackets around them ([example])

Here is what your response will look like:

IMPORTANT: You must start your response with the subject line using this **exact format**:
[SUBJECT: "Quick question about your <duration> at <latest company name>"]

Rules:
- Keep the square brackets and the word SUBJECT.
- Inside the quotes, replace <duration> with the number of years or months at the most recent company.
  - If greater than 1 year, use: "X years"
  - If less than 1 year, use: "X months"
- Replace <latest company name> with the name of the most recent company in their experience.
- Do not change or remove the square brackets, the colon, or the quotes.
- This must always be the **first line** in the response or the output is invalid.


Then create the paragraph: "Hi (first name),"

Then create 1 condensed sentence (that is grammatically correct and not a run-on) for the following: 
Start this paragraph with “I'm reaching out because I noticed” then begins to outline career progress and/or achievements throughout their career while subtly praising them for their accomplishment mentioned while also non explicitly, subtly implying ackowledgment of positive atributes that let them accomplish what was mentioned. This paragraph needs to be specific, specifically referencing company name(s) and/or specific achievements. 
This should be very short, with the absolute maximum word limit being 40 words

Then create a paragraph containing: "Are you achieving your career goals at (current company name)?"


Ideal example based on provided input data:
        Name: {example['Name']}
        Experiences (including current position): {example['Experiences']}
        About Section: {example['About']}
        Example Output: {example['Output']}


    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating message for {name}: {e}")
        return "Error generating message"

def getsubject(message): 
    match = re.search(r"\[SUBJECT: \"(.*?)\"\]", message)
    return match.group(1) if match else ""

def createBody(message, senderName):
    messageArr = re.findall(r"\[(.*?)\]", message)  
    if len(messageArr) > 1:
        messageArr = messageArr[1:]

        canned_message_1 = "The reason I ask is that we have mentored hundreds of high-achieving professionals like you, helping them rise to more senior levels."
        canned_message_2 = "We were able to help Debesh land a CIO job in the Retail industry. We also recently helped Susan land an executive position in the pharma industry. (Their testimonials along with many others are on our website and my LinkedIn profile.)"
        canned_message_3 = "Would you like to schedule a complimentary consultation to discuss your career?"
        canned_message_4 = f"Best, \n{senderName}"
        canned_message_5 = "P.S. Please note that we are not recruiters and are not reaching out for any specific job openings."

        messageArr += [canned_message_1, canned_message_2, canned_message_3, canned_message_4, canned_message_5]
        return messageArr
    else:
        return [""]

def main(ID, link, name, email, about, experience, senderName):
    response = generate_ai_message(ID, link, name, about, experience)
    subject = getsubject(response)
    body = createBody(response, senderName)

    return {
        'Profile ID': ID,
        'LinkedIn Link': link,
        'Name': name,
        'Email Address': email,
        'Subject': subject,
        'InMail Message': "\n\n".join(body)
    }

    print(name + " InMail message saved.")
