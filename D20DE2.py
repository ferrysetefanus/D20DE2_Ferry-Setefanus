# import semua library yang dibutuhkan
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
import re
import psycopg2
from sqlalchemy import create_engine

# mendefinisikan instance webdrive google chrome
driver = webdriver.Chrome()

#mendefinisikan web yang akan di scrapping
url = "https://www.nike.com/id/w/shoes-y7ok"
driver.get(url)

#menentukan jumlah scroll yang diinginkan
scroll_count = 20

# looping untuk menjalankan scroll sebanyak jumlah yang sudah ditentukan
for _ in range(scroll_count):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Tunggu sebentar untuk konten tambahan dimuat

#mengambil halaman HTML yang sudah selesai di load berdasarkan jumlah scroll
html = driver.page_source

# menutup halaman browser
driver.quit()

# parsing html hasil dari scrapping
soup = BeautifulSoup(html, "html.parser")

# mencari data berdasarkan elemen div yang memiliki class product-card
shoes = soup.find_all("div", class_="product-card") 

# membuat array untuk menampung data hasil dari html yang sudah diparsing
name = []
type = []
num_of_colours = []
price = []

# melakukan looping untuk mencari elemen dan class yang mengandung data yang dibutuhkan
for shoe in shoes:
  name_tag = shoe.find("div", class_="product-card__title")
  type_tag = shoe.find("div", class_="product-card__subtitle") # dapet nama
  num_of_colours_tag = shoe.find("div", class_="product-card__product-count")
  price_tag = shoe.find("div",class_="product-price")
  
  # append setiap data yang dibutuhkan ke array yang sudah dibuat
  name.append(name_tag.text)
  type.append(type_tag.text)
  num_of_colours.append(num_of_colours_tag.text)
  price.append(price_tag.text)

# membuat dataframe berdasarkan array yang sudah berisikan data 
df = pd.DataFrame({
      "name": name,
      "type": type,
      "num_of_colours": num_of_colours,
      "price": price
})

# Menggunakan regex untuk mengekstrak angka dari awal string
df['num_of_colours'] = df['num_of_colours'].str.extract('(\d+)')

# Ubah kolom 'num_of_colours' menjadi tipe data integer
df['num_of_colours'] = df['num_of_colours'].astype(int)

# Menggunakan regex untuk menghapus "Rp", tanda koma, dan spasi
df['price'] = df['price'].apply(lambda x: re.sub(r'[^\d]', '', x))

# Mengubah tipe data kolom 'price' menjadi integer
df['price'] = df['price'].astype(int)

# membuat koneksi ke database postgresql
connection = psycopg2.connect(
    database="D20DE2",
    user="postgres",
    password="********",
    host="localhost", # biar gak ketahuan password saya
    port="5432"
)

engine = create_engine('postgresql://postgres:******@localhost:5432/D20DE2')

# load dataframe ke postgresql
df.to_sql('web_scrapping1', engine, if_exists='replace', index=False)
