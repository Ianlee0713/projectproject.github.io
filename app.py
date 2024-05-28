from flask import Flask, request, render_template, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def crawl_books_com_tw(keyword, max_results=10):
    url = f"https://search.books.com.tw/search/query/key/{keyword}/cat/all"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    items = soup.find_all('div', class_='table-td')
    data = []
    count = 0
    for item in items:
        if count >= max_results:
            break
        try:
            title_tag = item.find('h4').find('a')
            title = title_tag.get_text(strip=True)
            language = item.find('div', class_='type clearfix').find('p').text.strip()
            authors = [a.text for a in item.find('p', class_='author').find_all('a')]
            author = ', '.join(authors)
            price_info = item.find('ul', class_='price clearfix').find('li').get_text(strip=True)
            price = price_info.split(',')[-1].strip()
            image_url = item.find('div', class_='box').find('img')['data-src']

            temp_data = {
                "Title": title,
                "Language": language,
                "Author": author,
                "Price": price,
                "Image URL": image_url
            }
            data.append(temp_data)
            count += 1
        except Exception as e:
            print(e)
            continue
    return data

def crawl_kingstone_com_tw(keyword, max_results=10):
    url = f"https://www.kingstone.com.tw/search/key/{keyword}/sort/qty"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    items = soup.find_all('li', class_='displayunit')
    data = []
    count = 0
    for item in items:
        if count >= max_results:
            break
        try:
            title_tag = item.find('h3', class_='pdnamebox').find('a')
            title = title_tag.get_text(strip=True)
            price = item.find('div', class_='buymixbox').find('span').next_sibling.get_text(strip=True).replace('元', '').strip()
            image_url = item.find('div', class_='coverbox').find('img')['src']

            temp_data = {
                "Title": title,
                "Price": price,
                "Image URL": image_url
            }
            data.append(temp_data)
            count += 1
        except Exception as e:
            print(e)
            continue
    return data

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    keyword = request.form['keyword']

    books_com_tw_data = crawl_books_com_tw(keyword)
    kingstone_com_tw_data = crawl_kingstone_com_tw(keyword)

    result = {
        "books_com_tw": {
            "title": "博客來綜合排序前十名",
            "books": books_com_tw_data
        },
        "kingstone_com_tw": {
            "title": "金石堂銷售排序前十名",
            "books": kingstone_com_tw_data
        }
    }

    return jsonify(result)
#網址 http://localhost:5000
if __name__ == '__main__':
    app.run(debug=True)