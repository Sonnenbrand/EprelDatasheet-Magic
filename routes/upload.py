# routes/upload.py
from flask import Blueprint, render_template, request, redirect, url_for, send_file
import pandas as pd
import requests
import os
import zipfile
from pdf2image import convert_from_path

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

@upload.route('/download', methods=['POST'])
def download_files():
    urls = request.form.getlist('urls')
    convert_to_jpg = request.form.get('convert_to_jpg')
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    else:
        for filename in os.listdir('downloads'):
            os.remove('downloads/' + filename)
    for url in urls:
        response = requests.get(url)
        if response.headers['Content-Type'] == 'application/pdf':
            open('downloads/' + url.split('/')[-1], 'wb').write(response.content)
            if convert_to_jpg:
                images = convert_from_path('downloads/' + url.split('/')[-1])
                for i, image in enumerate(images):
                    image.save('downloads/' + url.split('/')[-1] + str(i) + '.jpg', 'JPEG')
        else:
            with open('downloads/' + url.split('/')[-1] + '.txt', 'w') as f: # Maybe other name for the not exit file?
                f.write(url.split('/')[-1] + ': PDF does not exist')
    zipf = zipfile.ZipFile('downloads/Files.zip', 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk('downloads/'):
        for file in files:
            if file != 'Files.zip':
                zipf.write(os.path.join(root, file))
    zipf.close()
    return send_file('downloads/Files.zip', as_attachment=True)