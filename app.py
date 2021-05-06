import time
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--window-size=1920x1080")

from flask import Flask, request, url_for, redirect, render_template
from bson import ObjectId
import pymongo

client = pymongo.MongoClient("localhost:27017")
db = client['crawl']

def get_post_id(post_id):
    find = db.crawl.find({"$and":[{"_id": {"$ne": ObjectId(post_id)}}, {"label": {"$exists": False}}]}).limit(1)
    for v in find:
        return v["_id"]

app = Flask(__name__, static_url_path = "/img", static_folder = "/img")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def choose():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Crawl':
            return redirect(url_for('my_form_post'))
        elif request.form['submit_button'] == 'Label':
                return redirect(url_for('post', post_id=get_post_id("eeeeeeeeeeeeeeeeeeeeeeee")))

@app.route('/form')
def indexs():
    return render_template('form.html')


@app.route('/selenium')
def test():
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path="/home/misa/code/selenium_python/chromedriver")
    driver.get("https://www.google.com")
    field = driver.find_element_by_xpath("//input[@class='gLFyf gsfi']")
    field.send_keys("Màng Chống Thấm, Màng Chống Thấm HDPE")
    field.send_keys(Keys.ENTER)
    button = driver.find_element_by_xpath("//a[@class='hide-focus-ring']")
    button.click()
    count = 0 
    for src in driver.find_elements_by_xpath("//img[@class='rg_i Q4LuWd']"):
        img = src.get_attribute('src')
        urllib.request.urlretrieve(img,'/home/misa/code/flask-app/img/'+str(count)+'.jpg')
        if(count>2):
            break
        count+=1
    driver.close()


@app.route('/form', methods=['POST'])
def my_form_post():
    url = request.form['url']
    xpath = request.form['xpath']
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path="/home/misa/code/selenium_python/chromedriver")
    #url = "https://unsplash.com/s/photos/natural"
    #"//img[@class='_2UpQX']"
    driver.get(url)
    list_src = []
    for src in driver.find_elements_by_xpath(xpath):
      name = str(src.get_attribute('alt'))
      list_src.append({'name':name})
    driver.close()
    x = db.crawl.insert_many(list_src)
    return render_template('src.html', list_src = list_src)

@app.route("/test", methods = ['GET'])
def questions():
    try:
        questions = db.test.find({},{"name":1,"unit_clean":1})
        return render_template('test.html', questions = questions)
    except Exception as e:
        return dumps({'error' : str(e)})

@app.route('/<string:post_id>', methods = ['GET','POST'])
def post(post_id):
    if request.method == 'POST':
        if request.form['submit_button'] == 'Prev':
            return redirect(url_for('post', post_id=get_post_id(post_id)))
        elif request.form['submit_button'] == 'Next':
            return redirect(url_for('post', post_id=get_post_id(post_id)))
        elif request.form['submit_button'] == 'Class1':
            db.crawl.update({"_id": ObjectId(post_id)}, {"$set": {"label": "Class1"}})
            return redirect(url_for('post', post_id=get_post_id(post_id)))
        elif request.form['submit_button'] == 'Class2':
            db.crawl.update({"_id": ObjectId(post_id)}, {"$set": {"label": "Class2"}})
            return redirect(url_for('post', post_id=get_post_id(post_id)))
    posts = db.crawl.find({"_id":ObjectId(post_id)})
    return render_template('post.html', posts=posts)