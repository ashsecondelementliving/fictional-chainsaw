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
                "Are you looking to move to a new and more senior role?",
                "We’ve helped hundreds of high-achieving professionals move into senior roles by identifying their leadership personalities, elevating their executive profiles, refining their brands, and guiding them to land top executive positions, either internally or elsewhere.",
                "Recently Debesh landed a CIO role in Retail; Susan secured an executive position in Pharma. (Their testimonials and many others are on my LinkedIn and our site.)",
                "Open to a quick call with our career specialist?",
                f"Best,\n{senderName}",
                "P.S. We’re not recruiters and not contacting you about a job opening. Reply with 'no thanks' If you don't want to receive emails from us."
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
        'InMail Message': "\n\n".join(body)
    }

    print(name + " InMail message saved.")
