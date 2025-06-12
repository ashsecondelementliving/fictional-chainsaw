import csv

def formatLeadpy(input_file):
    output_file = 'ParsedLeads.csv'

    try:
        with open(input_file, mode='r', encoding='utf-8-sig') as infile:  
            reader = csv.DictReader(infile)
            reader.fieldnames = [name.lstrip('\ufeff') if name else name for name in reader.fieldnames]

            fieldnames = ['Profile ID', 'LinkedIn Link', 'Name', 'Experiences', 'About']

            with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                if {'ProfileUrl', 'ProfileId', 'FirstName', 'LastName'}.issubset(reader.fieldnames):
                    file_type = "zopto"
                elif {'profile_link', 'id', 'first_name', 'last_name'}.issubset(reader.fieldnames):
                    file_type = "expandi"
                else:
                    print("Error: Unrecognized file format.")
                    return
                
                for row in reader:
                    if file_type == "zopto":
                        linkedin_link = row.get('ProfileUrl', '')
                        profile_id = row.get('ProfileId', '')
                        email_address = row.get('EmailAddress')
                        name = f"{row.get('FirstName', '').strip()} {row.get('LastName', '').strip()}"
                    else:
                        linkedin_link = row.get('profile_link', '')
                        profile_id = row.get('id', '')
                        email_address = row.get('email')
                        name = f"{row.get('first_name', '').strip()} {row.get('last_name', '').strip()}"

                    writer.writerow({
                        'Profile ID': profile_id,
                        'LinkedIn Link': linkedin_link,
                        'Name': name,
                        'Email Address': email_address,
                        'Experiences': '',
                        'About': ''
                    })

        print(f"Parsed data has been written to {output_file}.")
    except FileNotFoundError:
        print(f"Error: {input_file} not found.")
