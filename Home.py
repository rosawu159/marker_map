import streamlit as st
import leafmap.foliumap as leafmap
from pymongo import MongoClient
from folium import Icon
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
import requests
import re

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
    items = db.testCollection.find()
    items = list(items)
    return items

# 将地标添加到数据库
def add_landmark_to_db(latitude, longitude, city, country):
    db = client.get_database('testdb')
    try:
        collection = client['testdb']['testCollection']
        collection.insert_one({"latitude": latitude, "longitude": longitude, "city": city, "country": country})
        db.testCollection.insert({"latitude": latitude, "longitude": longitude, "city": city, "country": country})
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


# Customize the sidebar
markdown = """ This is a travel daily. """

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://cdn-icons-png.flaticon.com/512/3286/3286370.png"
st.sidebar.image(logo)

# Customize page title
st.title("跟 者 日 記 旅 遊 去！")
st.markdown(""" 不管是什麼樣的心情，記錄下來，可以給你對應的旅遊計畫喔～ """)
st.markdown(""" 1. 寫下自己的心情，會幫你選一個國家並給你推薦的旅遊計畫 """)
mood = st.text_area('請描述你的心情')

if st.button('添加心情'):
  prompt= f'''請根據以下的日記內容，生成一段具有安慰和鼓勵性的文字，並提供一個適合的旅遊推薦。

        日記內容：
        {mood}

        請生成的文字包含以下要素：
        1. 安慰和鼓勵：對日記中表達的負面情緒進行安慰和鼓勵。
        2. 旅遊推薦：根據日記中提到的需要放鬆，提供一個合適的旅遊城市推薦，並給我城市的名字和對應的latitude、longitude、。
        
        生成的文字示例：
        "我能感受到你這幾天承受了很多壓力。工作上的忙碌和疲憊有時候真的會讓人感到難以承受。但是請相信，這一切都會過去，你是如此堅強和有能力的人。給自己一點時間和空間，好好照顧自己。我建議你去[旅遊地點]旅行，那裡的[特點]非常適合放鬆和恢復精力。希望這次旅行能夠給你帶來平靜和快樂。加油，你一定可以的！"
        
        請按照json格式輸出：
        comfort_and_encouragement: 你的安慰和鼓勵文字,
        city_name: 推薦的旅遊城市,
        country_name: "這個城市的國家,
        latitude: 這個城市的經度,
        longitude: 這個城市的緯度,
        reason: 這個城市的推薦原因
  '''
  result = get_completion([ {"role": "user", "content": prompt }], model="gpt-3.5-turbo")
  st.info(result)
  data = json.loads(result)

  st.info(data['city_name'])
  st.info(data['comfort_and_encouragement'])
  st.info(data['reason'])
  add_landmark_to_db(data['latitude'], data['longitude'], data['city_name'], data['country_name'])
  st.success('地標和心情已保存！')

m = init_map()
cities = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_cities.csv"
#regions = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_regions.geojson"

#m.add_geojson(regions, layer_name="US Regions")

m.to_streamlit(height=320)
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

