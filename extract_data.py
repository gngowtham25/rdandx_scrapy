import json
import sys
import pymongo
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase
from email import encoders

logger = logging.getLogger('extract_data')

#Initialise Database Connection
mongoClient = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=10)
try:
    mongoClient.server_info()
except Exception as e:
    raise e
mongoDB = mongoClient["rdandx"]
contentCollection = mongoDB['contentMaster']

def extract_data(send_mail_with_content, receiver_mail):
    all_contents = contentCollection.find()
    with open('./content_data.jsonl', 'w') as _writefile:
        for each_content in all_contents:
            del each_content['_id']
            if str(send_mail_with_content) != 'true':
                del each_content['content_text']
            json.dump(each_content, _writefile)
            _writefile.write('\n')

        send_mail(receiver_mail)

def send_mail(receiver_mail):
    from_address = "rdandx.gowtham@gmail.com"
    password = "test@1234"
    #to_address = "hr@rdand.com"
    to_address = receiver_mail

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = "Content Extraction Data"
    body = "Firstpost Data Content JSON file is attached below"
    msg.attach(MIMEText(body, 'plain'))

    filename = "content_data.jsonl"
    attachment = open("./content_data.jsonl", "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(from_address, password)
    text = msg.as_string()
    s.sendmail(from_address, to_address, text)
    s.quit()

if __name__ == "__main__":
    arguments = sys.argv[1:]
    send_mail_with_content = "false"
    receiver_mail = "hr@rdand.com"
    for each_argument in arguments:
        if 'content' in each_argument:
            send_mail_with_content = each_argument.split('=')[1]
        elif 'receiver_mail' in each_argument:
            receiver_mail = each_argument.split('=')[1]
        else:
            print("Invalid Arguments. Possible Arguments --content=false --receiver_mail=hr@rdand.com")
            sys.exit()
    
    extract_data(send_mail_with_content, receiver_mail)