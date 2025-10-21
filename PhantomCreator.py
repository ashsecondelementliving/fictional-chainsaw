# description, allSkills
# company, jobTitle, jobDateRange, jobStartedSince, jobIsCurrent, jobDuration
# company2, jobTitle2, jobDateRange2, jobStartedSince2, jobIsCurrent2, jobDuration2

import csv
import autoCreator

def creatorMain(input_file, senderName, output_file, socketio=None):
    group1 = ['description', 'allSkills']
    group2 = [
        'company', 'companyUrl', 'jobTitle', 'jobDescription',
        'jobDateRange', 'jobStartedSince', 'jobIsCurrent', 'jobDuration'
    ]
    group3 = [
        'company2', 'companyUrl2', 'jobTitle2', 'jobDescription2',
        'jobDateRange2', 'jobStartedSince2', 'jobIsCurrent2', 'jobDuration2'
    ]

    print("formatting...")

    try:
        with open(input_file, newline='', encoding='utf-8') as csvfile, \
             open(output_file, mode='w', newline='', encoding='utf-8') as outfile:

            reader = csv.DictReader(csvfile)
            leads = list(reader)
            total = len(leads)

            fieldnames = ['Profile ID', 'LinkedIn Link', 'Name', 'Email Address', 'Subject', 'Full Message']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for idx, row in enumerate(leads, start=1):
                try:
                    description_value = row.get('description', '').strip()
                    skills_value = row.get('allSkills', '').strip()
                    description = f"{description_value}. \nMy skills are: {skills_value}"

                    str2 = ''.join(f'\n{h}: {row[h]}' for h in group2 if h in row and row[h])
                    str3 = ''.join(f'\n{h}: {row[h]}' for h in group3 if h in row and row[h])
                    Jobs = f"Latest Job: {str2} \n\nPrevious Job: {str3}"

                    message_data = autoCreator.main(
                        row.get('Profile ID', ''),
                        row.get('LinkedIn Link', ''),
                        row.get('Name', ''),
                        row.get('Email Address', ''),
                        description,
                        Jobs,
                        senderName
                    )
                    writer.writerow(message_data)

                    # ✅ Emit progress update to client
                    if socketio:
                        socketio.emit("progress_update", {"current": idx, "total": total})

                except Exception as e:
                    print(f"Error processing row {idx}: {e}")
                    continue  # Skip bad rows but continue safely

        print("✅ OutputMessages.csv written with all leads.")

    except FileNotFoundError:
        print(f"❌ Error: {input_file} not found.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
