# Importning nececerry librarys 
from lxml import etree
import requests
from bs4 import BeautifulSoup
import pandas as pd 



url = 'https://www.ebay.com/sch/i.html?_from=R40&_nkw=iphone+xr&_sacat=0&LH_Sold=1&LH_Complete=1&Model=Apple%2520iPhone%2520XR&_dcat=9355&rt=nc&_udlo=25&_ipg=240'

# creating a pandas dataframe 
df = pd.DataFrame(columns=['heading',
                        'item_price',
                        'logistic_price',
                        'item_location',
                        'item_score',
                        'time',
                        'purchase_option',
                        'number_bids',
                        'item_color',
                        'item_specific',
                        'seller_name',])

# Create a function to make a requst
def make_request(url, respond = False):
    # since Ebay is a pretty smart website and they don't allow non-humans to access ther website 
    # we aslo have to assing the user agent 
    headers = ({'User-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'})
 

    if respond == True:
        requested_obj = requests.get(url,headers=headers)
        respond = requests.get(url,headers=headers).status_code
        soup = BeautifulSoup(requested_obj.text, 'html.parser')
        return soup, respond

    else :
        
        requested_obj = requests.get(url,headers=headers)
        soup = BeautifulSoup(requested_obj.text, 'html.parser')
        return soup


    

# create a fanction that will find a number of existing pages and return a list of all page liks 
def pagination(url): 
    
    # since ebay returns at max 10.000 records and we are searching withing a page of 240 records each, our very last reachable page can be 42 
    # Ebay returns the most last page possible , even if we call page which number is higher then the last existing, that's we will call the last page and get it's number 
    last_page= url + '&_pgn=' + str(42)
    soup = make_request(last_page)
    
    # ol -> li -> a -> attrs = aria-curent 
    page_number  = soup.find('ol').find_all('li')
   

    # going through page tags to find the current one
    for i in page_number:
    
        try: 
            page_status = i.find('a').attrs['aria-current']
            

            if page_status == 'page':
                page_last = i.find('a').text
        except: 
            continue
    # for every page number between 1 and last one create it's link
    page_list = [url + '&_pgn=' + str(i) for i in range(1, int(page_last) + 1)]

    return page_list

# Defining function to get all needed data form item page 
def get_data_product_page(product_link):
    
   
    # get a page html 
    page = make_request(product_link)

    # get ending data and time of selling
    try:
        time  = page.find('span', id = 'bb_tlft').text
    except:
        time = None


    # seller name 
    try:
        seller_name = page.find('span', class_ = 'mbg-nw').text
    except:
        seller_name = None

    # item color
    try: 
        item_color = page.find('span', itemprop = 'color').text
    except:
        item_color = None

    return time, seller_name, item_color
  
# Design a function to get all the data 
def get_data(link, df):

    
    #get an html object 
    raw , response = make_request(link, respond=True)

    #get products object 
    products  = raw.find_all('li', class_ = 's-item s-item__pl-on-bottom')
    
    # get to individual item 
    for item in products[1:]:
        
        

        #dom = etree.HTML(str(item))
        # item heading 
        heading  = item.find('span', role = 'heading').text
        

        # item specifications 
        item_specific  = item.find('div', class_ = 's-item__subtitle').text
        

        # review score 
        try:
            item_score = item.find('div', class_ ='s-item__reviews').find('span', class_ = 'clipped').text
            
        except:
            item_score = None 
         

        # item price 
        item_price = item.find('span', class_ = 's-item__price').text
       

        # item logistic price 
        try:
            logistic_price = item.find('span', class_ = 's-item__shipping s-item__logisticsCost').text
        except:
            logistic_price = None
             
        # getting base item location 
        item_location = item.find('span',class_ = 's-item__location s-item__itemLocation').text

        # get base time 
        time = item.find('div', class_ = 's-item__title--tag').text
        

        # we can have either purchase option or number of bids , so we put them in 'try - exept' statment 
        try: 
            # item purchase option
            purchase_option = item.find('span' , class_ = 's-item__purchase-options-with-icon').text
            number_bids = 0 
        except :
            purchase_option = 'acution'
            number_bids = item.find('span', class_ = 's-item__bids s-item__bidCount').text
       
        # item link 
        item_link  = item.find('a', class_ = 's-item__link').attrs['href']

        time_new,  seller_name, item_color = get_data_product_page(item_link)

        
        
        print(item_location)

        # check if extended time if availbable 
        if time_new != None:
            time = time_new
        

        #print(f'item heading: {heading}\n item specifications: {item_specific}\n item price: {item_price} \n logistic price: {logistic_price} \n purchase_option{purchase_option}, \n time: {time} \n location: {item_location} \n seller_name{seller_name} \n item color: {item_color}')

        # saving values to dataframe
        df = df.append([{'heading': heading,
                        'item_price': item_price,
                        'logistic_price': logistic_price,
                        'item_location': item_location,
                        'item_score':item_score,
                        'time':time,
                        'purchase_option': purchase_option,
                        'number_bids':number_bids,
                        'item_color': item_color,
                        'item_specific':item_specific,
                        'seller_name': seller_name,
            }])

    return df

def main(url):
    # creating a pandas dataframe 
    df = pd.DataFrame(columns=['heading',
                        'item_price',
                        'logistic_price',
                        'item_location',
                        'item_score',
                        'time',
                        'purchase_option',
                        'number_bids',
                        'item_color',
                        'item_specific',
                        'seller_name',])
    for link in  pagination(url):
        p = get_data(link,df)
        df =p
        print(len(df))
        print('Data is updated in the db')
    df.to_csv('Ipone_xr_sales_2')

    

main(url)



        

    


        






    

    




