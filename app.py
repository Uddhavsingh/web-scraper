from flask import Response, request, jsonify, Flask
import requests
from bs4 import BeautifulSoup
import csv 
from flask_cors import CORS, cross_origin
import sys
import json

fields = ['Name', 'Price', 'Source', 'Search'] 
rows = []
app = Flask(__name__)
CORS(app)

@app.route('/', methods=["GET"])
def welcome_msg():
   return 'WELCOME TO BACKEND'

@app.route('/', methods=["POST"])
def scrap_products():
  print('request data ::  ',request.data)
  search_string = request.data.decode('utf-8')
  search_dict = json.loads(search_string)
  search_term = search_dict['search']
  print('search_term :: ', search_term)
  if request.method == "POST":
    flipkart_url = 'https://www.flipkart.com/search?q='
    amazon_url = 'https://www.amazon.in/s?k='
    # ebay_url = 'https://www.ebay.com/sch/i.html?_nkw='
    ## settings.py
    USER_AGENT = 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'
    HEADERS = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }


    # headers = { 'User-Agent': USER_AGENT}

    # Set up search terms and concatenate with URLs
    # search_terms = ['iphone', 'iphone', 'laptop']
    flipkart_search = flipkart_url + search_term
    amazon_search = amazon_url + search_term
    # ebay_search = ebay_url + search_terms[2]

    # Make requests and parse HTML with BeautifulSoup
    flipkart_response = requests.get(flipkart_search, headers=HEADERS)
    amazon_response = requests.get(amazon_search, headers=HEADERS)
    # ebay_response = requests.get(ebay_search, headers=headers)
    # print('amazon_response :: ', amazon_response)
    flipkart_soup = BeautifulSoup(flipkart_response.content, 'html.parser')
    amazon_soup = BeautifulSoup(amazon_response.content, 'html.parser')
    # ebay_soup = BeautifulSoup(ebay_response.content, 'html.parser')
    # print('amazon_soup :: ', amazon_soup)
    # Find product data on each site
    flipkart_products = flipkart_soup.find_all('div', {'class': '_2kHMtA'})
    amazonVProds = ''
    flipkartVProds = ''
    if amazon_soup.find_all('div', {'class': 'sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16'}) :
      amazonVProds = True
      amazon_products = amazon_soup.find_all('div', {'class': 'sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16'})
    
    if amazon_soup.find_all('div', {'class': 'sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 AdHolder sg-col s-widget-spacing-small sg-col-4-of-20'}) :
      amazon_products = amazon_soup.find_all('div', {'class': 'sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 AdHolder sg-col s-widget-spacing-small sg-col-4-of-20'})
      amazonVProds = False

    if flipkart_soup.find_all('div', {'class': '_2kHMtA'}):
      flipkartVProds = True
      flipkart_products = flipkart_soup.find_all('div', {'class': '_2kHMtA'})
    if flipkart_soup.find_all('div', {'class': '_4ddWXP'}):
      flipkartVProds = False
      flipkart_products = flipkart_soup.find_all('div', {'class': '_4ddWXP'})
    
    
    # ebay_products = ebay_soup.find_all('div', {'class': 's-item__wrapper'})
    # print(f'Flipkart total products: {flipkart_products.len()}')
    # print(f'Amazon total products: {type(amazon_products)}')
    # print(f'Ebay total products: {ebay_products.len()}')
    
    allFlipkartProds = []
    allAmazonProds = []
    allEbayProds = []
    # allProducts = {'flipkart': allFlipkartProds, 'amazon': allAmazonProds, 'ebay': allEbayProds} 
    allProducts = {'flipkart': allFlipkartProds, 'amazon': allAmazonProds}
    price = 'Not Avaliable'
    img='https://projectfba.com/wp-content/uploads/2021/07/no-image-logo.jpg'
    rating = 'Not Avaliable'
    # Extract product information
    for product in flipkart_products:
        name = 'Not Avaliable'
        if flipkartVProds == True:
          if product.find('div', {'class': '_4rR01T'}):
            name = product.find('div', {'class': '_4rR01T'}).text.strip()
        if flipkartVProds == False:
          if product.find('a', {'class': 's1Q9rs'}) :
            name = product.find('a', {'class': 's1Q9rs'}).text.strip()
        # print(f'Flipkart: {name}')
        
        if name != 'Not Avaliable' :
          if flipkartVProds == True:
            if product.find('div', {'class': '_3I9_wc _27UcVY'}):
              price = product.find('div', {'class': '_3I9_wc _27UcVY'}).text.strip()
          if flipkartVProds == False:
            if product.find('div', {'class': '_30jeq3'}):
              price = product.find('div', {'class': '_30jeq3'}).text.strip()
            
        if product.find('img', {'class': '_396cs4'}):
          img = product.find('img', {'class': '_396cs4'})['src']
        if product.find('div', {'class': '_3LWZlK'}):
          rating = product.find('div', {'class': '_3LWZlK'}).text.strip() 
        # print(f'Flipkart: {name} - {price}')
        allFlipkartProds.append({'name': name, 'price': price, 'img': img, 'rating': rating})
        row = [name, price[1:], 'Flipkart', search_term]
        rows.append(row)

          
    for (index, product) in enumerate(amazon_products):
        # print(f'Amazon: index {product}')
        name = 'Not Avaliable'
        
        if amazonVProds == True :
          name = product.find('span', {'class': 'a-size-medium a-color-base a-text-normal'}).text.strip()
        if amazonVProds == False :
          name =  product.find('span', {'class': 'a-size-base-plus a-color-base a-text-normal'}).text.strip()
     
        # price = product.find('span', {'class': 'a-offscreen'}).text.strip()
        if(name != 'Not Avaliable') :
          price = 'Not Avaliable'
          
          if amazonVProds == True :
            if product.find('span', {'class': 'a-offscreen'}):
              price = product.find('span', {'class': 'a-offscreen'}).text.strip() 
          if amazonVProds == False :
            if product.find('span', {'class': 'a-price-whole'}):
              price = product.find('span', {'class': 'a-price-whole'}).text.strip() 
              price = '₹'+price

          # img
          if product.find('img', {'class': 's-image'}):
            img = product.find('img', {'class': 's-image'})['src']

          # rating
          if product.find('span', {'class': 'a-icon-alt'}):
            rating = product.find('span', {'class': 'a-icon-alt'}).text.strip() 

          # print(f'Amazon: {name} - {price}')
          allAmazonProds.append({'name': name, 'price': price, 'img': img, 'rating': rating})
          row = [name, price[1:], 'Amazon', search_term]
          rows.append(row)

      
    # for product in ebay_products:
    #     print(f'Ebay: {product}')
    #     name = product.find('h3', {'class': 's-item__title'}).text.strip()
    #     # print(f'Ebay: {name}')
    #     price = product.find('span', {'class': 's-item__price'}).text.strip()
    #     # print(f'Ebay: {name} - {price}')
    #     allEbayProds.append({name: name, price: price})

    # name of csv file 
    filename = "products.csv"
    # writing to csv file 
    # 'a', newline=''
    with open(filename, 'a', encoding="utf-8") as csvfile: 
      # creating a csv writer object 
      csvwriter = csv.writer(csvfile) 
      # writing the fields 
      csvwriter.writerow(fields) 
      # writing the data rows 
      csvwriter.writerows(rows)

    print(f'allProducts: {allProducts}')
    response = jsonify(allProducts)
    # Enable Access-Control-Allow-Origin
    # response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == "__main__":
  app.run(debug=True)
