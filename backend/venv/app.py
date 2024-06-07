from flask import Flask, request, jsonify
import requests
import json
from web3 import Web3
import re
from flask_cors import CORS

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from flask_sqlalchemy import SQLAlchemy

# Çağrı Altınüzengi - 28100
# Sine Mete - 33486
# Mustafa Cem Büyükalpelli - 29507

app = Flask(__name__)
CORS(app)

#DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///content.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Content(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_hash = db.Column(db.String, nullable=False)
    tx_hash = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()

# Ethereum node connection
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# Contract abi and address from contract's json
with open('ContentRegistry.json') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']
    contract_address = contract_json['networks']['5777']['address']
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

@app.route('/register', methods=['POST'])
def register_content():
    data = request.json
    url = data['url']
    content = scrape_content(url)  # Bu fonksiyon URL'den içeriği çekmeli
    content_hash = w3.keccak(text=content['Content']).hex()

    # info to contract
    tx_hash = contract.functions.registerContent(
        content['id'],
        content['Title'],
        content['Author'],
        content['Date'],
        content['Content'][:200],
        content_hash
    ).transact({'from': w3.eth.accounts[0]})

    # Return id from tx_hash
    # tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
    # logs = contract.events.ContentAdded().processReceipt(tx_receipt)
    # content_id = logs[0]['args']['id']
    # , 'tx_hash': tx_hash.hex()
    #{'contentId': content_id}

    # Add to DB
    new_content = Content(
        id=content['id'],
        title=content['Title'],
        author=content['Author'],
        date=content['Date'],
        content=content['Content'][:200],
        content_hash=content_hash,
        tx_hash=tx_hash.hex()
    )
    db.session.add(new_content)
    db.session.commit()

    return jsonify({'tx_hash': tx_hash.hex()})

@app.route('/contents', methods=['GET'])
def get_contents():
    contents = Content.query.all()
    results = [
        {
            "id": content.id,
            "title": content.title,
            "author": content.author,
            "date": content.date,
            "content": content.content,
            "content_hash": content.content_hash,
            "tx_hash": content.tx_hash
        } for content in contents]

    return jsonify(results)

def scrape_content(url):
    # Web scrabing code
    # response = requests.get(url)
    urlcontent = identify_website(url)
    # Parsing
    # content = {
    #     'id': 'unique_id',
    #     'title': 'Title of the article',
    #     'text': 'Full content of the article',
    #     'tags': ['news', 'blockchain']
    # }
    return urlcontent

def extract_tweet_info_with_selenium(tweet_url):
    driver = webdriver.Chrome()  
    driver.get(tweet_url)

    tweet_info = {}

    try:
        try:
            tweet_text_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="tweetText"]'))
            )
            tweet_info['id'] = tweet_url,
            tweet_info['Title'] = "A tweet"
            tweet_info['Content'] = tweet_text_element.text
        except:
            tweet_info['Content'] = 'Text not found'

        # Extract the author's username from the URL
        try:
            author_username = tweet_url.split('/')[3]
            tweet_info['Author'] = author_username
        except:
            tweet_info['Author'] = 'Author not found'

        try:
            tweet_date_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'time'))
            )
            tweet_info['Date'] = tweet_date_element.get_attribute('datetime')
        except:
            tweet_info['Date'] = 'Date not found'

        # Extract number of likes, retweets, and replies
        # tweet_info['likes'] = tweet_info['retweets'] = tweet_info['replies'] = 0
        engagement_info_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-testid]'))
        )
        for info in engagement_info_elements:
            aria_label = info.get_attribute('aria-label')
 
    finally:
        driver.quit()

    return tweet_info


def extract_article_details_hur(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the title of the article
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else 'No title found'

        # Extract the publication date from several possible locations
        pub_date_tag = soup.find('span', class_='date') or \
                       soup.find('div', class_='date') or \
                       soup.find('time')
        pub_date = pub_date_tag.text.strip() if pub_date_tag else 'No publication date found'

        # Extract the author of the article
        author_tag = soup.find('a', class_='rprt_name')
        author = author_tag.text.strip() if author_tag else 'No author found'

        # Extract the main content of the article
        content_tags = soup.find_all('div', class_='news-content')
        article_content = ' '.join([paragraph.text.strip() for paragraph in content_tags])

        # Debug output to help diagnose the issue if no content found
        if not article_content.strip():
            print("No content found. Here are the div elements for debugging:")
            for div in soup.find_all('div'):
                print(div.get('class'), div.text[:100])  # Print first 100 characters of each div for inspection


        if author == "No author found":
          author = "huriyet"
        return {
            'id': url,
            'Title': title,
            'Author': author,
            'Date': pub_date,
            'Content': article_content.strip()
        }
    else:
        return 'Failed to retrieve the article'

def get_bbc_article_details(url):
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch the page: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the title
    title_tag = soup.find('h1')
    title = title_tag.get_text() if title_tag else 'N/A'

    # Extract the author
    author_tag = soup.find('span', {'data-testid': 'byline-name'})
    author = author_tag.get_text() if author_tag else 'N/A'

    # Extract the publication date
    date_tag = soup.find('time')
    if date_tag:
        publication_date = date_tag.get('datetime', 'N/A')
    else:
        date_tag = soup.find('div', {'data-testid': 'timestamp'})
        publication_date = date_tag.get_text() if date_tag else 'N/A'

    # Extract the content
    content = ""
    content_tags = soup.find_all('div', {'data-component': 'text-block'})
    for tag in content_tags:
        content += tag.get_text() + "\n"

    return {
        'id': url,
        'Title': title,
        'Author': author,
        'Date': publication_date,
        'Content': content.strip()
    }

def identify_website(url):
    # Define patterns for BBC, Hurriyet, and X/Twitter URLs
    patterns = {
        "BBC": r"https?://(www\.)?bbc\.(com|co\.uk)/",
        "Hurriyet": r"https?://(www\.)?hurriyet\.com\.tr/",
        "X/Twitter": r"https?://(www\.)?(x|twitter)\.com/"
    }
    
    # Check the URL against each pattern
    for site, pattern in patterns.items():
        if re.match(pattern, url):
            if site == "BBC" :
                return get_bbc_article_details(url)
            elif site == "Hurriyet":
                return  extract_article_details_hur(url)
            elif site == "X/Twitter":
                return extract_tweet_info_with_selenium(url)
    
    return "Unknown site"

if __name__ == '__main__':
    app.run(debug=True)
