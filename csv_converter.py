#       A script for converting csv files exported by Firepoint crm into a format that can be imported into KWcommand
#        / \      ____
#       /*_*\    | ._.| 
#     < ____ >  \|__T_|/
#       V  V      L  L
#       Frank Senseney
#       Last updated: December 17th 2019

import csv, json, os, sys, re

csv_template = """First Name,Middle Name,Last Name,Prefix,Suffix,Full Legal Name,About,Country Code,Mobile Phone,Country Code,Home Phone,Country Code,Work Phone,Country Code,Other Phone,Email,Email 2,Street,City,State/Province,Postal Code,Street,City,State/Province,Postal Code,Company,Street,City,State/Province,Postal Code,Country Region,Title,Department,Birthday,Home Anniversary,"Qualified/Captured/Connected",Buyer,Seller,Bought,Sold,Agent,KW Agent,Allied Resource,Talent,Referral Partner,Downline,Tags,Notes,Source,Other Source,Facebook,Twitter,Linkedin,Google+,Pinterest,Instagram,Houzz
"""

#Error handling
if len(sys.argv) is 2:
    if os.path.exists(os.path.join(os.getcwd(),sys.argv[1])):
        import_path = os.path.join(os.getcwd(),sys.argv[1])
    else:
        print('Invalid path. "%s" does not exist in the current directory' % sys.argv[1])
        sys.exit(1)
else:
    print('Wrong number of arguments. Usage: %s <relative path to csv file>' % sys.argv[0])
    sys.exit(1)
kwfile_path = os.path.join(os.getcwd(),'firepoint_contacts_converted.csv')

#Reformat phone numbers
def format_phone_number(num):
    #remove words in parenthases
    num = re.sub(r'\(\w+\)| ', '', num)
    #remove whitespace
    num = re.sub(r'\(\w+ ?\w+\)|( )|(\| ?\d+) ', '',num)
    #if the number is longer than 10 digits remove the first one
    if len(num) is not 10:
        num = num[1:]
    #Convert numbers into a more readable format
    num = re.sub(r'(\d{3})(\d{3})(\d{4})', r'(\1) \2-\3', num)
    if num == "":
        num = "(000) 000-0000"
    return num

#Get phone info and return them organized in a dict
def get_phones(val):
    phones = val.split('|')
    data = {}
    for phone in phones:
        if re.search('Mobile', phone):
            data['Mobile Phone'] = format_phone_number(phone)
        elif re.search('Work', phone):
            data['Work Phone'] = format_phone_number(phone)
        elif re.search('Other', phone):
            data['Other Phone'] = format_phone_number(phone)
    return data

#Get emails and return them organized as a dict
def get_emails(val):
    emails = val.split('|')
    data = {}
    for email in emails:
        #remove word in parenthases
        email = re.sub(r'\(\w+\)', '', email)
        #remove whitespace
        email = re.sub(r'[ \t]+$', '', email)
        if len(data) is 0:
            data['Email'] = email
        elif len(data) is 1:
            data['Email 2'] = email
    return data

def get_notes(val):
    data = {}
    #replace new lines with spaces
    val = re.sub(r'[\n]', ' ', val)
    if len(val) > 0:
        data['Notes'] = val
    return data

#Create base csv with template
def create_base_csv():
    with open(kwfile_path, 'wb') as kwfile:
        bytstr = str.encode(csv_template)
        kwfile.write(bytstr)
        kwfile.close()

#Varify if a contact should be used or not
def valid_contact(dict):
    if 'First Name' in dict and dict['First Name'] == 'Unknown':
        print('Invalid contact: First Name is Unknown')
        return False
    elif 'Last Name' in dict and dict['Last Name'] == 'Unknown':
        return False
    else:
        return True

#Get the parts of contact information needed from firepoint csv
def get_firepoint_data():
    data = []
    with open(import_path) as fpfile:
        dr = csv.DictReader(fpfile)
        for row in dr:
            #emails = get_emails(row['Email Addresses'] + "|" + row['Email'])
            emails = get_emails(row['Email Addresses'])
            phones = get_phones(row['Phone Numbers'])
            notes = get_notes(row['Special Notes'] + row['Warnings'])
            contact = {
                'First Name' : row['First Name'].capitalize(),
                'Last Name' : row['Last Name'].capitalize()
            }
            contact.update(emails)
            contact.update(phones)
            contact.update(notes)
            if valid_contact(contact):
                data.append(contact)
    return data

#create final csv with data
def create_kw_csv():
    data = get_firepoint_data()
    with open(kwfile_path, 'r', newline="\n") as kw_read, open(kwfile_path, 'a', newline="\n") as kw_write:
        dr = csv.DictReader(kw_read)
        fields = dr.fieldnames
        dw = csv.DictWriter(kw_write, fieldnames=fields, extrasaction='ignore')
        for c in data:
            dw.writerow(c)
            print(c)
        kw_write.close()

if __name__ == '__main__':
    create_base_csv()
    create_kw_csv()
