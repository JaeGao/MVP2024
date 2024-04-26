import streamlit as st
import datetime
from xhs import DataFetchError
from config.settings import text_models,image_models
from dotenv import load_dotenv
from time import sleep
from api.xhs_api import QRCode_sign_streamlit,cookie_sign,create_client
from api.openai_api import OpenAIClient
from api.langchain_api import LangChainClient,autoImageCategorize,get_image_description
from content.content_generator import *
from image.image_generator import get_image_langchain
from utils import *
from copy import deepcopy
from config.category import categoryTranslations
# load_dotenv(override=True)
# api_key = os.environ.get("OPENAI_API_KEY")
prompt_version = 'v1'
st.set_page_config(
    page_title="Image-pased post generation",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)
col1, col2 = st.columns([1,1]) 

if 'suggestion_input' not in st.session_state:
    st.session_state.suggestion_input = False    

if 'submit_button_clicked' not in st.session_state:
    st.session_state.submit_button_clicked = False

if 'title_generate_clicked' not in st.session_state:
    st.session_state.title_generate_clicked = False  # 初始化点击状态

if 'content_generate_clicked' not in st.session_state:
    st.session_state.content_generate_clicked = False  # 初始化点击状态

if 'post' not in st.session_state:
    st.session_state.post = None  

if 'title_list' not in st.session_state:
    st.session_state.title_list = []  

if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False

if 'xhs_client' not in st.session_state:
    st.session_state.xhs_client = create_client()  # 假定的初始化，根据你的实际情况调整

def submit_button_callback():

    st.session_state.submit_button_clicked = True

with open("data/tools.json", 'rb') as file:
    st.session_state.tools = json.load(file)

def create_langchain_client():

    if 'openai_api_key' in st.session_state and 'text_model' in st.session_state \
        and 'image_model' in st.session_state:
        # 创建新的LangChainClient实例

        st.session_state.langchain_client = LangChainClient(
            st.session_state.openai_api_key,
            st.session_state.image_model,
            st.session_state.text_model,
            st.session_state.tools
        ) 

    st.session_state.title_list = []  
    st.session_state.post = None 
    st.session_state.suggestion_input = False 
    st.session_state.title_generate_clicked = False
    st.session_state.content_generate_clicked = False

with st.sidebar: 

    st.title('Login to 小红书')


    if st.session_state.user_logged_in:
        st.success("Login success！")
    else:
        phone_tab, QR_tab = st.tabs(
            [
                "Phone number Login",
                "QR Code Login",
            ]
        )
        with phone_tab:
            with st.form(key='login_form'):
                phone = st.text_input("Please enter your Phone number", key='phone')
                submit_button = st.form_submit_button(label='Send verificaiton code',on_click = submit_button_callback)
                # 发送验证码
                if submit_button:
                    try:
                        res = st.session_state.xhs_client.send_code(phone)
                        st.success("Code sent!")
                    except DataFetchError as e:
                        st.error(f"Login Failed：{e}")
            if submit_button or st.session_state.submit_button_clicked:

                # 用户输入验证码
                with st.form(key='verify_form'):
                    code = st.text_input("Enter Code", key='code')
                    verify_button = st.form_submit_button(label='Login')

                    if verify_button:
                        # 检查验证码并登录
                        try:
                            check_res = st.session_state.xhs_client.check_code(phone, code)
                            token = check_res["mobile_token"]
                            login_res = st.session_state.xhs_client.login_code(phone, token)
                            st.session_state.user_logged_in = True
                            st.rerun()
                        except DataFetchError as e:
                            st.error(f"Login Failed：{e}")

        with QR_tab:            
            if st.button("Get QR Code"):
                qr_img, qr_res = QRCode_sign_streamlit(st.session_state.xhs_client)
                st.image(qr_img, caption='Please Scan the QR code',width =200)
                qr_id = qr_res["qr_id"]
                qr_code = qr_res["code"]
                code_status = 0
                while code_status != 2:
                    check_qrcode = st.session_state.xhs_client.check_qrcode(qr_id, qr_code)
                    code_status = check_qrcode["code_status"]
                    print(code_status)
                    sleep(1)
                    # if code_status == 2:
                    #     print(json.dumps(check_qrcode["login_info"], indent=4))
                    #     print("当前 cookie：" + st.session_state.xhs_client.cookie)
                st.session_state.user_logged_in = True
                st.rerun()
    if st.session_state.user_logged_in:
        openai_api_key = st.text_input(
            "OpenAI API Key", 
            type="password", 
            on_change=create_langchain_client,
            key='openai_api_key'  # 使用key参数确保值被正确存储在session_state中
        )

        text_model = st.selectbox(
            'Text Model', 
            text_models,
            on_change=create_langchain_client,
            key='text_model'
        )

        image_model = st.selectbox(
            'Image Model', 
            image_models,
            on_change=create_langchain_client,
            key='image_model'
        )

        categoryList = ["Auto-Select"]+list(categoryTranslations.keys())
        category = st.selectbox(
                'Post category', 
                categoryList,
                key='category',
            )

with col1:
    st.markdown("<h2 style='text-align: center; color: grey;'>🎬 Creator Studio</h2>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### ⬆️ Upload your photo", unsafe_allow_html=True)
        st.session_state.images = st.file_uploader("Multiple photos accepted", accept_multiple_files=True,disabled = not st.session_state.user_logged_in )

        if st.button("Create Title",disabled = len(st.session_state.images)==0) and st.session_state.user_logged_in:
            with st.spinner('Working on it...'):
                st.session_state.title_generate_clicked = True
                st.session_state.langchain_client.cleam_memory(0)
                description = get_image_description(st.session_state.images,st.session_state.openai_api_key)
                print(description)
                success = st.success("Image description generated successfully")

                if st.session_state.category=="Auto-Select" :
                    auto_selected_category = autoImageCategorize(description, st.session_state.text_model,st.session_state.openai_api_key)
                    st.success('Automatic selection successful! The category is：{}'.format(auto_selected_category if auto_selected_category else "default"))
                    print("Auto selected category is " + auto_selected_category if auto_selected_category else "No category selected")
                    if auto_selected_category in categoryTranslations.keys():
                        with open('data/prompt/image/{}.md'.format(categoryTranslations[auto_selected_category]), 'r', encoding='utf-8') as file:
                            st.session_state.system_prompt = file.read() 
                    else:
                        with open('data/prompt/image/{}.md'.format("Default"), 'r', encoding='utf-8') as file:
                            st.session_state.system_prompt = file.read() 
                else:
                    with open('data/prompt/image/{}.md'.format(categoryTranslations[st.session_state.category]), 'r', encoding='utf-8') as file:
                        st.session_state.system_prompt = file.read()
                st.session_state.title_list = get_title_image_langchain(st.session_state.langchain_client, st.session_state.system_prompt,description)
                success.empty()
            st.success('The title list has been updated, please select your favorite title.')

    with st.container(border=True):
    # st.write("---")
        st.markdown("### 🧭 Caption creation", unsafe_allow_html=True)

        option= st.selectbox('Choose your favorite title：', st.session_state.title_list if len(st.session_state.images)!=0 else [])
        # if selected_option:
        #     st.session_state.selected_title = selected_option
        st.session_state.selected_title  = st.text_area(
            "The title can be modified",
            option,disabled = not option
            )
        if st.button("Generate Post",disabled = not st.session_state.selected_title) and st.session_state.title_generate_clicked:
            with st.spinner('Working on it...'):
                st.session_state.content_generate_clicked = True
                st.session_state.langchain_client.cleam_memory(4)
                content = get_content_from_title_langchain(st.session_state.langchain_client,st.session_state.system_prompt, st.session_state.selected_title)

                success = st.success('Success！')

                st.session_state.save_path = create_directory_for_post()

                st.session_state.post = (content, st.session_state.images)
                success.empty()
            success = st.success('The post content has been generated and can be previewed and adjusted.')

    with st.container(border=True):
    # st.write("---") 
        st.markdown("### ✏️Editor", unsafe_allow_html=True)

        suggestion = st.text_input('What adjustments need to be made?',disabled = not st.session_state.content_generate_clicked)
        if suggestion:
            st.session_state.suggestion_input = True
        if st.button("Regenerate caption",disabled = not st.session_state.suggestion_input) and st.session_state.content_generate_clicked and st.session_state.suggestion_input:
            with st.spinner('working on it...'):
                content = get_content_from_suggestion_langchain(st.session_state.langchain_client,st.session_state.system_prompt,suggestion)
                st.session_state.post = (content, st.session_state.images)
            st.success('updated！')

    if st.session_state.post and len(st.session_state.images)!=0: 
        # note_data =  {
        #         "title": st.session_state.post[0]['标题'],
        #         "description": st.session_state.post[0]['正文'],
        #         "topics": st.session_state.post[0]['Tags']
        #     }          
        # note_md = trans_into_md(note_data)
        col2_1, col2_2,col2_3 = col2.columns([1,4,1])  
        with col2_2:
        # 将发布的贴文详情显示在主页面的右侧
            with st.container(border=True):
                st.markdown("<h2 style='text-align: center; color: grey;'>📚 Post preview</h2>", unsafe_allow_html=True)
                # for image_path in st.session_state.images:
                    # st.image(image_path, use_column_width=True)
                tabs = st.tabs(["图片{}".format(idx) for idx in range(1,len(st.session_state.post[1])+1)])
                for idx,tab in enumerate(tabs):
                    tab.image(st.session_state.post[1][idx], use_column_width=True)
                # st.markdown(note_md, unsafe_allow_html=True)
                title_tab, description_tab,topics_tab = st.tabs(
                    [
                        "Title editor",
                        "Caption editor",
                        "Tags editor"
                    ]
                )

                with title_tab:
                    st.session_state.final_title = st.text_area("None",st.session_state.post[0]['标题'],label_visibility = "collapsed")
                with description_tab:
                    st.session_state.final_description = st.text_area("None",st.session_state.post[0]['正文'],label_visibility = "collapsed",height=600)  
                with topics_tab:                
                    st.session_state.final_topics = st.text_area("None",st.session_state.post[0]['Tags'],label_visibility = "collapsed")

    with st.container(border=True):
    # st.write("---")
        st.markdown("### 📈  Preview and publish",unsafe_allow_html=True)
        if st.button("Send to 小红书",disabled = (not st.session_state.post) or (len(st.session_state.openai_api_key)==0)):
            with st.spinner('working on it...'):
                post_content = {'标题': st.session_state.final_title, '正文': st.session_state.final_description, 'Tags': st.session_state.final_topics}
                post_image = st.session_state.post[1]
                topics = get_topics(st.session_state.xhs_client, post_content['Tags'])
                topics_suffix = get_topics_suffix(topics)
                post_content['正文'] = post_content['正文'] + topics_suffix

                images_path = []
                for image in post_image:    
                    path = os.path.join(st.session_state.save_path, image.name)
                    images_path.append(path)
                    with open(path, "wb") as f:
                        f.write(image.getvalue())

                note_info = st.session_state.xhs_client.create_image_note(
                    post_content['标题'], post_content['正文'], images_path, topics=topics, 
                     post_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                beauty_print(note_info)

                note_data = {
                    "title": post_content['标题'],
                    "description": post_content['正文'],
                    "topics": topics_suffix,
                    # 添加其他任何您想保存的信息
                }

                save_post_to_file(note_data, st.session_state.save_path)
            st.success('Success! ')