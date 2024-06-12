import streamlit as st
import leafmap.foliumap as leafmap
from pymongo import MongoClient
from folium import Icon
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
import requests
import re
import pandas as pd
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

# Function to create a postcard
def create_postcard(attraction_name):
    getpic = False
    while not getpic:
        
        # Load the image from the URL
        t_url = 'https://api.unsplash.com/search/photos?page=1&query=Parc-Guell&client_id=' + st.secrets['client_id']
        response = requests.get(t_url)
        st.info(response)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            getpic = True
    
    # Resize the image to a postcard size (e.g., 400x400)
    image = image.resize((400, 400))
    image = np.array(image)

    # Create a blank white image for the quote
    quote_image = np.ones((400, 400, 3), dtype=np.uint8) * 255

    # Convert to PIL for text drawing
    quote_pil = Image.fromarray(quote_image)
    draw = ImageDraw.Draw(quote_pil)

    # Define the quote and font
    quote = "Dream big, work hard,\nand make it happen!"
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 24)

    # Calculate text size and position
    text_bbox = draw.textbbox((0, 0), quote, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (quote_image.shape[1] - text_width) // 2
    text_y = (quote_image.shape[0] - text_height) // 2

    # Draw the text on the image
    draw.text((text_x, text_y), quote, fill=(0, 0, 0), font=font)

    # Convert back to OpenCV format
    quote_image = np.array(quote_pil)

    # Combine the images side by side
    postcard = np.hstack((image, quote_image))

    return postcard


st.set_page_config(layout="wide")
API=st.secrets['api_key']

def get_completion(messages, model="gpt-3.5-turbo", temperature=0, max_tokens=1000):
  payload = { "model": model, "temperature": temperature, "messages": messages, "max_tokens": max_tokens }
  headers = { "Authorization": f'Bearer {API}', "Content-Type": "application/json" }
  response = requests.post('https://api.openai.com/v1/chat/completions', headers = headers, data = json.dumps(payload) )
  obj = json.loads(response.text)
  if response.status_code == 200 :
    return obj["choices"][0]["message"]["content"]
  else :
    return obj["error"]

def init_connection():
    connection_string = "mongodb+srv://"+st.secrets['db_username']+":"+st.secrets['db_pswd']+"@cluster0.zskuvse.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    return MongoClient(connection_string, server_api=ServerApi('1'))
        
client = init_connection()



def get_data():
    db = client.get_database('testdb')
    items = db.aCollection.find()
    items = list(items)
    return items

# 将地标添加到数据库
def add_landmark_to_db(latitude, longitude, city, country):
    db = client.get_database('testdb')
    try:
        collection = client['testdb']['aCollection']
        collection.insert_one({"latitude": latitude, "longitude": longitude, "city": city, "country": country})
    except Exception as e:
        st.markdown(e)

# 从数据库获取所有地标
def get_landmarks_from_db():
    db = get_db()
    return list(db.find({}, {'_id': 0, 'latitude': 1, 'longitude': 1, 'mood': 1}))

# 初始化地图
def init_map():
    m = leafmap.Map(center=[40, -100], zoom=4)
    return m

# Function to save the image to MongoDB
def save_to_mongodb(image):
    is_success, buffer = cv2.imencode(".jpg", image)
    if is_success:
        fs.put(buffer.tobytes(), filename="postcard.jpg")
        st.success("Image saved to MongoDB.")
    else:
        st.error("Failed to encode the image.")


# Customize the sidebar
markdown = """ This is a travel daily. """

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://cdn-icons-png.flaticon.com/512/3286/3286370.png"
st.sidebar.image(logo)




# Customize page title
st.title("跟 者 日 記 旅 遊 去！")


m = init_map()
cities = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_cities.csv"
items = get_data()
df = pd.DataFrame(items)
m.add_points_from_xy(
    df,
    x="longitude",
    y="latitude",
    icon_names=["gear", "map", "leaf", "globe"],
    spin=True,
    add_legend=True,
)
m.to_streamlit(height=320)
cities = df.get('city')
st.markdown(""" 1. 寫下自己的心情，會幫你選一個國家並給你推薦的旅遊計畫 """)
mood = st.text_area('請描述你的心情')
if st.button('添加心情'):
  prompt= f'''請根據以下的日記內容，生成一段具有安慰和鼓勵性的文字，並提供一個適合的旅遊推薦。以下是不要重複出現的城市：{cities}

        日記內容：
        {mood}

        請生成的文字包含以下要素：
        1. 安慰和鼓勵：對日記中表達的負面情緒進行安慰和鼓勵。
        2. 旅遊推薦：根據日記中提到的需要放鬆，提供一個合適的旅遊城市推薦，並給我城市的名字和對應的latitude、longitude、。
        
        請按照json格式輸出：
        comfort_and_encouragement: 你的安慰和鼓勵文字,
        city_name: 推薦的旅遊城市,
        country_name: "這個城市的國家,
        latitude: 這個城市的經度,
        longitude: 這個城市的緯度,
        reason: 這個城市的推薦原因
  '''
  result = get_completion([ {"role": "user", "content": prompt }], model="gpt-3.5-turbo")
  data = json.loads(result)

  st.info(data['comfort_and_encouragement'])
  st.info(data['reason'])
  add_landmark_to_db(data['latitude'], data['longitude'], data['city_name'], data['country_name'])
  st.success('地標和心情已保存！')
  data_city = data['city_name']
  prompt= f'''請根據{data_city}給我一個推薦的景點
        
        請按照json格式輸出：
        attraction_name: 推薦景點
  '''
  result = get_completion([ {"role": "user", "content": prompt }], model="gpt-3.5-turbo")
  data = json.loads(result)

  # Create the postcard
  postcard = create_postcard(data['attraction_name'])
  
  # Display the postcard using Streamlit
  st.image(postcard, caption="Postcard with Louvre Museum and Inspirational Quote", use_column_width=True)
    
  # Display the postcard using Streamlit
  if postcard is not None:
      st.image(postcard, caption="Postcard with Louvre Museum and Inspirational Quote", use_column_width=True)
      save_button = st.button("Save to MongoDB")
      if save_button:
          save_to_mongodb(postcard)
  
