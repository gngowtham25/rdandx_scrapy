# Scrapy Parser
Scrapy Parser is used to scrape all pages of firstpost and store contents, links and image_links, title and other metadata in our local MongoDB. 

### Pre-requisites:
- Python 2.7 and pip (Install using this link https://pip.pypa.io/en/stable/installing/)
- Install virtualenv `pip install virtualenv`
- Mongo DB Community Edition 4.4 ( https://docs.mongodb.com/manual/tutorial/install-mongodb-on-os-x/ )
- Start Mongo DB server. For Mac, `brew services start mongodb-community@4.4`. For Linux, `sudo systemctl start mongod` 

### Setup:
After cloning the repository, run following commands
1. Create virtualenv `python2.7 -m virtualenv venv`
2. Activate virutalenv `source venv/bin/activate` 
2. Run `pip install -r requirements.txt` 

### Task 1 : Run Scrapy Script:
1.  Execute following command `scrapy crawl firstpost` 


### Task 2 : Run Data Extraction in JSON format Script:

1. Execute `python extract_data.py --content=false --receiver_mail=hr@rdand.com`

**Arguments**:
- --content : Send mail with all text content (Huge size - 10x). Default value is false. If it is set to true, files will be sent with all text content of the page.
- --receiver_mail : Mail address of the receiver.