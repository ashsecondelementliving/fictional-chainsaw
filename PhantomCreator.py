# description, allSkills
# company, jobTitle, jobDateRange, jobStartedSince, jobIsCurrent, jobDuration
# company2, jobTitle2, jobDateRange2, jobStartedSince2, jobIsCurrent2, jobDuration2

import csv
import autoCreator

def creatorMain (input_file, senderName, output_file, socketio=None ):
    
    # def autoCreator(ID,link, name, about, experience):
    #     print(ID)
    #     print('................\n')
    #     print(link)
    #     print('................\n')
    #     print(name)
    #     print('................\n')
    #     print("About:", about)
    #     print('................\n')
    #     print("Experience:", experience)
    #     print("\n-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")

    group1 = ['description', 'allSkills']
    group2 = ['company', 'companyUrl', 'jobTitle', 'jobDescription', 'jobDateRange', 'jobStartedSince', 'jobIsCurrent', 'jobDuration']
    group3 = ['company2', 'companyUrl2', 'jobTitle2', 'jobDescription2', 'jobDateRange2', 'jobStartedSince2', 'jobIsCurrent2', 'jobDuration2']

    print("formatting...")

    with open(input_file, newline='', encoding='utf-8') as csvfile, \
         open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
             
        reader = csv.DictReader(csvfile)
        fieldnames = ['Profile ID', 'LinkedIn Link', 'Name', 'Email Address', 'Subject', 'InMail Message']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            description = f"{row['description']}. \nMy skills are: {row['allSkills']}"
            str2 = ''.join(f'\n{h}: {row[h]}' for h in group2 if h in row and row[h])
            str3 = ''.join(f'\n{h}: {row[h]}' for h in group3 if h in row and row[h])
            Jobs = f"Latest Job: {str2} \n\nPrevious Job: {str3}"

            message_data = autoCreator.main(
                row['Profile ID'],
                row['LinkedIn Link'],
                row['Name'],
                row['Email Address'],
                description,
                Jobs,
                senderName
            )
            writer.writerow(message_data)

    print("✅ OutputMessages.csv written with all leads.")
