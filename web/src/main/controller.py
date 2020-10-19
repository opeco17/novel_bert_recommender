import json
import re

from flask import flash, redirect, request, render_template
from flask_mail import Message
import requests

from config import Config
from forms import ContactForm, TextUploadForm, URLUploadForm
from logger import logger
from model import RecommendItemsGetter
from run import app, auth, mail


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    logger.info('Web: index called.')
    return render_template('index.html')


@app.route('/search_by_text', methods=['GET', 'POST'])
def search_by_text():
    logger.info('Web: search_by_text called.')
    text_upload_form = TextUploadForm()
    
    if request.method == 'GET':
        return render_template('search_by_text.html', form=text_upload_form, success=False)

    is_correct_input = text_upload_form.validate()
    if not is_correct_input:
        flash('小説の本文を入力して下さい。')
        return render_template('search_by_text.html', form=text_upload_form, success=False)

    text = text_upload_form.text.data
    logger.info(f"Uploaded text: {text}")
    recommend_items = RecommendItemsGetter.get_recommend_items_by_text(text)
    
    if not recommend_items:
        return render_template('error.html')
    
    logger.info(f"Reccomend result", extra={'search_method': 'text'})
    return render_template('result.html', recommend_items=recommend_items)

    
@app.route('/search_by_url', methods=['GET', 'POST'])
def search_by_url():
    logger.info('Web: search_by_url called.')
    url_upload_form = URLUploadForm()
    
    if request.method == 'GET':
        return render_template('search_by_url.html', form=url_upload_form, success=False)
    
    is_correct_input = url_upload_form.validate()
    is_correct_url = re.fullmatch(r'https://ncode.syosetu.com/[nN].{6}/?', url:=url_upload_form.url.data)
    if (not is_correct_input) or (not is_correct_url):
        flash('小説家になろうの小説URLを入力して下さい。')
        return render_template('search_by_url.html', form=url_upload_form, success=False)
    
    ncode = url[26:33].upper()
    logger.info(f"Uploaded ncode: {ncode}")
    recommend_items = RecommendItemsGetter.get_recommend_items_by_ncode(ncode)
    
    if not recommend_items:
        return render_template('error.html')
    
    logger.info(f"Reccomend result", extra={'search_method': 'url'})
    return render_template('result.html', recommend_items=recommend_items)


@app.route('/narou_redirect/<ncode>/<int:rank>', methods=['GET'])
def narou_redirect(ncode, rank):
    logger.info('Web: narou_redirect called.')
    url = f"https://ncode.syosetu.com/{ncode}/"
    logger.info(f"Reccomend item result", extra={'rank': rank})
    return redirect(url, code=302)
            
            
@app.route('/about', methods=['GET'])
def about():
    logger.info('Web: about called.')
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    logger.info('Web: contact called.')
    contact_form = ContactForm()

    if request.method == 'GET':
        return render_template('contact.html', form=contact_form, success=False)
    
    is_correct_input = contact_form.validate()
    if not is_correct_input:
        flash('全て入力して下さい。')
        return render_template('contact.html', form=contact_form, success=False)
    
    msg = Message(contact_form.subject.data, sender=Config.MAIL_USERNAME, recipients=[contact_form.email.data])
    msg.body = f"Contact Information \n Name: {contact_form.name.data} \n Mail: {contact_form.email.data}  \n Content: {contact_form.message.data}"
    mail.send(msg)
    return render_template('contact.html', success=True)


@auth.get_password
def get_password(username):
    if username in Config.ADMIN_INFO:
        return Config.ADMIN_INFO.get(username)
    return None


@app.route('/admin', methods=['GET'])
@auth.login_required
def admin():
    return render_template('admin.html', kibana_url=Config.KIBANA_URL, grafana_url=Config.GRAFANA_URL)