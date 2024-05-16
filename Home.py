import streamlit as st
import leafmap.foliumap as leafmap
import pymongo
from folium import Icon

@st.cache_resource
def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])

client = init_connection()

@st.cache_data(ttl=600)
def get_db():
    db = client.admin
    items = db.mycollection.find()
    items = list(items)  # make hashable for st.cache_data
    return items

# 将地标添加到数据库
def add_landmark_to_db(latitude, longitude, mood):
    db = get_db()
    db.insert_one({'latitude': latitude, 'longitude': longitude, 'mood': mood})

# 从数据库获取所有地标
def get_landmarks_from_db():
    db = get_db()
    return list(db.find({}, {'_id': 0, 'latitude': 1, 'longitude': 1, 'mood': 1}))

# 初始化地图
def init_map():
    m = leafmap.Map(center=[40, -100], zoom=4)
    return m

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
This is about
"""

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://cdn-icons-png.flaticon.com/512/3286/3286370.png"
st.sidebar.image(logo)

# Customize page title
st.title("Streamlit for Geospatial Applications")

st.markdown(
    """
    This multipage app template demonstrates various interactive web apps created using [streamlit](https://streamlit.io) and [leafmap](https://leafmap.org). It is an open-source project and you are very welcome to contribute to the [GitHub repository](https://github.com/opengeos/streamlit-map-template).
    """
)

st.header("Instructions")

markdown = """
1. For the [GitHub repository](https://github.com/opengeos/streamlit-map-template) or [use it as a template](https://github.com/opengeos/streamlit-map-template/generate) for your own project.
2. Customize the sidebar by changing the sidebar text and logo in each Python files.
3. Find your favorite emoji from https://emojipedia.org.
4. Add a new app to the `pages/` directory with an emoji in the file name, e.g., `1_🚀_Chart.py`.

"""

st.markdown(markdown)

coordinates = st.text_input('請輸入地標坐標 (格式如 40,-100)')
mood = st.text_input('請描述你的心情')
if st.button('添加地標'):
    if coordinates:
        lat, lon = [float(coord) for coord in coordinates.split(',')]
        add_landmark_to_db(lat, lon, mood)
        st.success('地標和心情已保存到数据库！')

# 显示地图和所有数据库中的地标
m = init_map()
landmarks = get_landmarks_from_db()
for item in landmarks:
    st.write(f"{item['latitude']} has a :{item['mood']}:")
for landmark in landmarks:
    icon = Icon(icon="heart", color="red", prefix="fa") 
    m.add_marker(location=(landmark['latitude'], landmark['longitude']), icon=icon)
m.to_streamlit(height=320)

