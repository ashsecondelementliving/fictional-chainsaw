import openai
import csv
import threading
from Example import example
import re

def mainpy(senderName, input_file, output_file, socketio=None):
    openai.api_key = "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"

    def call_openai(prompt, result_holder):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            result_holder.append(response.choices[0].message.content)
        except Exception as e:
            result_holder.append(f"Error generating message: {e}")

    def generate_inmail(lead):
        try:
            prompt = f"""
Create a LinkedIn InMail message based on the following details:
Name: {lead['Name']}
Experiences (including current position): {lead['Experiences']}
About Section: {lead['About']}

follow this template:

The message should reference specific things that are extremely personalized with the tone sounding professional but approachable.
The message needs to be a concise and dense as possible, making sure there are no filler words and each word is placed for its own meticulous purpose

Each paragraph needs to have brackets around them ([example])

Here is what your response will look like:

At the beginning of your response include exactly (include the brackets and quotes): [SUBJECT: ""]
In between the quotation marks should be a subject line for the message that you create based on the following format: "Quick question about your <number of years at latest company if numbers of year more than 1, else include number of months at latest company> years at <latest company name>"

Then create the paragraph: "Hi (first name),"

Then create 1 condensed sentence (that is grammatically correct and not a run-on) that should be formatted like: “I saw ..., your...” outlining career progress and achievements, then mention their positive attributes.

Then add: "Are you achieving your career goals at (current company name)?"

Example Input:
Name: {example['Name']}
Experiences: {example['Experiences']}
About Section: {example['About']}
Example Output: {example['Output']}
"""
            result_holder = []
            thread = threading.Thread(target=call_openai, args=(prompt, result_holder))
            thread.start()
            thread.join()
            return result_holder[0]
        except Exception as e:
            print(f"Error generating message for {lead['Name']}: {e}")
            return "Error generating message"

    def getsubject(message, lead):
        if ('Tenure At Position' in lead and len(lead['Tenure At Position']) > 1) and ('Company' in lead and len(lead['Company']) > 1):
            return f"Quick question about your {lead['Tenure At Position']} in your current position at {lead['Company']}"
        else:
            match = re.search(r'\[SUBJECT: "(.*?)"\]', message)
            return match.group(1) if match else ""

    def createBody(message):
        messageArr = re.findall(r"\[(.*?)\]", message)
        if len(messageArr) > 1:
            messageArr = messageArr[1:]
            canned = [
                "We’ve helped hundreds of high-achieving professionals move into senior roles by identifying their leadership personalities, elevating their executive profiles, refining their brands, and guiding them to land top executive positions, either internally or elsewhere.",
                "Recently Debesh landed a CIO role in Retail; Susan secured an executive position in Pharma. (Their testimonials and many others are on my LinkedIn and our site.)",
                "Open to a quick call to discuss?",
                f"Best,\n{senderName}",
                "P.S. We’re not recruiters and not contacting you about a job opening. Reply with 'no thanks' If you don't want to receive emails from us."
            ]
            return messageArr + canned
        else:
            return [""]

    def createPlain(message):
        messageArr = re.findall(r"\[(.*?)\]", message)
        return messageArr[2:] if len(messageArr) > 1 else [""]

    try:
        with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            leads = list(reader)
            total = len(leads)

            with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
                fieldnames = ['Profile ID', 'LinkedIn Link', 'First Name', 'Last Name', 'Email Address', 'Subject', 'Ai Message', 'Full Message']
                writer = csv.DictWriter(outfile, fieldnames=fieldnames, extrasaction='ignore', quoting=csv.QUOTE_ALL)
                writer.writeheader()

                for idx, lead in enumerate(leads, start=1):
                    if len(lead['About']) + len(lead['Experiences']) > 200:
                        response = generate_inmail(lead)
                        body = createBody(response)
                        plain = createPlain(response)
                        subject = getsubject(response, lead)
                        parts = lead['Name'].split()
                        firstName = parts[0]
                        lastName = parts[-1]
                        row = {
                            'Profile ID': lead['Profile ID'],
                            'LinkedIn Link': lead['LinkedIn Link'],
                            'First Name': firstName,
                            'Last Name': lastName,
                            'Email Address': lead.get('Email Address', ''),
                            'Subject': subject,
                            'Ai Message': "\n\n".join(plain),
                            'Full Message': "\n\n".join(body)
                        }
                        writer.writerow(row)

                        if socketio:
                            socketio.emit("progress_update", {"current": idx, "total": total})

        print("InMail messages saved.")
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
