import requests
from bs4 import BeautifulSoup
import re
import time
import csv 
import sys
import psycopg2

def get_soup(url, write_file=False):
    page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    page.raise_for_status()
    soup = BeautifulSoup(page.text, "lxml")

    if write_file:
        file = open('page.html', 'w')
        file.write(page.text)
        file.close()

    return soup

def write_csv(name, company, image, summary, price_starting, price_topend, mileage_l, mileage_u, manual, automatic, petrol, diesel, cng, electric, seating):
    file = open('data.csv', 'a')
    csvWriter = csv.writer(file)
    csvWriter.writerow([name, company, image, summary, price_starting, price_topend, mileage_l, mileage_u, manual, automatic, petrol, diesel, cng, electric, seating])
    file.close()


def write_db(dbcon, name, company, image, summary, price_starting, price_topend, mileage_l, mileage_u, manual, automatic, petrol, diesel, cng, electric, seating):
    cur = dbcon.cursor()

    SQL = '''INSERT INTO cars(name, company, image, summary, price_starting, price_topend, mileage_l, mileage_u, manual, automatic, petrol, diesel, cng, electric, seating_capacity)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
    
    params = (name, company, image, summary, price_starting, price_topend, mileage_l, mileage_u, manual, automatic, petrol, diesel, cng, electric, seating)

    cur.execute(SQL, params)

    cur.close()

    dbcon.commit()

def export_xlsx(dbcon):
    pass

def log_done(company):
    file = open('log.txt', 'a')
    file.write('\nScraped: ' + company)
    file.close()

def scrape_car_company(dbcon, company_url, company, car=False):
    if not car:
        domain = 'https://www.carwale.com'

        print('Scraping ' + company)

        soup = get_soup(company_url)

        car_urls = []

        li_tags = soup.find_all('li', class_='o-fzptUA')
        for li_tag in li_tags: #o-cpnuEd o-SoIQT o-eZTujG o-fzpilz
            if li_tag.find(class_='o-fzoTov'):
                print('Skipping: ' + li_tag.find('a', class_='o-fzoHMp')['href'])
                continue

            if li_tag.find('a', class_='o-fzoHMp'):
                car_url = domain + li_tag.find('a', class_='o-fzoHMp')['href']
            elif li_tag.find('a', class_='o-fzpilz'):
                car_url = domain + li_tag.find('a', class_='o-fzpilz')['href']

            car_urls.append(car_url)
            print(car_url)
    else:
        car_urls = [company_url]

    for car_url in car_urls:    
        print('Scraping ' + car_url)
        soup = get_soup(car_url, write_file=True)

        name = soup.find('h1', class_="o-eqqVmt").find(text=True, recursive=False)

        image = soup.find('img', class_="o-bXKmQE")['src']

        summary = soup.find('div', class_="o-fzpilz").text

        priceRegex = re.compile(r'[0-9]+\.[0-9]+')

        price = priceRegex.findall(soup.find('p', class_='o-fyWCgU').text)
        price_starting = float(price[0])
        price_topend = float(price[1])

        table = soup.find('table',class_='o-bfyaNx')

        mileageHeader = table.find('span', text='Mileage')
        if mileageHeader:
            mileageRegex = re.compile(r'[0-9]+\.[0-9]+|[0-9]+')

            mileage = mileageRegex.findall(mileageHeader.parent.next_sibling.text)

            if len(mileage) == 1:
                mileage_l = float(mileage[0])
                mileage_u = float(mileage[0])
            else:
                mileage_l = float(mileage[0])
                mileage_u = float(mileage[1])
        else:
            mileage_l = 17.0
            mileage_u = 21.0


        transmissionHeader = table.find('span', text='Transmission')
        if transmissionHeader:
            automatic = False
            manual = False


            transmission_str = transmissionHeader.parent.next_sibling.text.lower()

            if 'automatic' in transmission_str or 'amt' in transmission_str:
                automatic = True

            if 'manual' in transmission_str:
                manual = True
        else:
            automatic = True
            manual = True

        fuelHeader = table.find('span', text='Fuel Type')
        if fuelHeader:
            fuel_str = fuelHeader.parent.next_sibling.text.lower()

            petrol = False
            diesel = False
            cng = False
            electric = False

            if 'petrol' in fuel_str:
                petrol = True

            if 'diesel' in fuel_str:
                diesel = True

            if 'cng' in fuel_str:
                cng = True

            if 'electric' in fuel_str:
                electric = True
        else:
            petrol = True
            diesel = True
            cng = False
            electric = False

        seatingHeader = table.find('span', text='Seating Capacity')
        if seatingHeader:
            seatingRegex = re.compile('[0-9]+')

            seating = int(seatingRegex.findall(seatingHeader.parent.next_sibling.text)[-1])
        else:
            seating = 5

        write_db(dbcon, name, company, image, summary, price_starting, price_topend, mileage_l, mileage_u, manual, automatic, petrol, diesel, cng, electric, seating)

        time.sleep(5)

    log_done(company)

if __name__ == "__main__":
    company_url = sys.argv[1]
    company = sys.argv[2]
    car = sys.argv[3]

    dbcon = psycopg2.connect(
        user='rwozksuc', 
        password='3nv4b-4aaJb5bx0--2hIAZeoYVXateTm',
        database='rwozksuc', 
        host='john.db.elephantsql.com')   

    if car is '0':
        scrape_car_company(dbcon, company_url, company, False)
    elif car is '1':
        scrape_car_company(dbcon, company_url, company, True)

    dbcon.close()