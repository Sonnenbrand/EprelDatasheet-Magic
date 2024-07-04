# routes/upload.py
from flask import Blueprint, render_template, request, redirect, url_for, send_file
import pandas as pd
import requests
import os
import zipfile
from pdf2image import convert_from_path
from PIL import Image
import uuid
import time

upload = Blueprint('upload', __name__)

@upload.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            df = pd.read_excel(file)
            urls = ["https://eprel.ec.europa.eu/informationsheet/Fiche_" + str(row['ID']) + "_" + row['CountryCode'] + ".pdf" for index, row in df.iterrows()]
            return render_template('upload.html', urls=urls)
    return render_template('upload.html')

def cleanup_download_dir(base_path='downloads', max_age=24*60*60):
    """Delete directories older than a day."""
    now = time.time()
    for dirpath, dirnames, filenames in os.walk(base_path):
        if not filenames:  # check if directory is empty
            creation_time = os.path.getctime(dirpath)
            if now - creation_time > max_age:
                os.rmdir(dirpath)

@upload.route('/download', methods=['POST'])
def download_files():
    cleanup_download_dir() # Added this line to cleanup old directories
    urls = request.form.getlist('urls')
    convert_to_jpg = request.form.get('convert_to_jpg')
    # Generate a unique identifier for this download session
    download_id = str(uuid.uuid4())
    download_dir = 'downloads/' + download_id
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    else: #not needed as UUID folders should almost never be the same
        for filename in os.listdir(download_dir):
            os.remove(download_dir + '/' + filename)
    for url in urls:
        response = requests.get(url)
        if response.headers['Content-Type'] == 'application/pdf':
            open(download_dir + '/' + url.split('/')[-1], 'wb').write(response.content)
            if convert_to_jpg:
                images = convert_from_path(download_dir + '/' + url.split('/')[-1])
                widths, heights = zip(*(i.size for i in images))
                total_height = sum(heights)
                max_width = max(widths)
                new_img = Image.new('RGB', (max_width, total_height))
                y_offset = 0
                for img in images:
                    new_img.paste(img, (0, y_offset))
                    y_offset += img.height
                new_img.save(download_dir + '/' + url.split('/')[-1] + '.jpg', 'JPEG')
        else:
            with open(download_dir + '/' + url.split('/')[-1] + '.txt', 'w') as f: # Maybe other name for the not exit file?
                f.write(url.split('/')[-1] + ': PDF does not exist')
    zipf = zipfile.ZipFile(download_dir + '/Files.zip', 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(download_dir + '/'):
        for file in files:
            if file != 'Files.zip':
                zipf.write(os.path.join(root, file))
    zipf.close()
    return send_file(download_dir + '/Files.zip', as_attachment=True)