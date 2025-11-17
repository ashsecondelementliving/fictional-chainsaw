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

follow this template:

The message should reference specific things that are extremely personalized with the tone sounding professional but approachable.
The message needs to be a concise and dense as possible, making sure there are no filler words and each word is placed for its own meticulous purpose

Each paragraph needs to have brackets around them ([example])

Here is what your response will look like:

At the beginning of your response include exactly (include the brackets and quotes): [SUBJECT: ""]
In between the quotation marks should be a subject line for the message that you create based on the following format: "Quick question about your <number of years at latest company if numbers of year more than 1, else include number of months at latest company> years at <latest company name>"

Then create the paragraph: "Hi (first name),"

Then create 1 condensed sentence (that is grammatically correct and not a run-on) that should be formatted like: “I saw ..., your...” outlining career progress and achievements, then mention their positive attribute(s). This sentence should be dense with no filler words, exactly like the example. Do not make it wordy, make it concise and straight to the point in a natural way.


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
        canned = [
                "I am a Client Success Specialist here at Second Element Living. We partner with executives and senior leaders navigating career advancement or transitioning into new roles.",
                "Your background is similar to those of our top successful clients who have landed senior level positions. Many of their testimonials are on my LinkedIn profile page and our web site.",
                "If you are open to opportunities, I can arrange a call with one of our executive mentors to discuss your career aspirations and see if we can help. Let me know if you are interested.",
                "Let me know if you are interested.",
                f"Best,\n{senderName}"
            ]
        return messageArr + canned
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
        'Full Message': "\n\n".join(body)
    }

    print(name + " InMail message saved.")
