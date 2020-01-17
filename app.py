from flask import Flask, request, jsonify

from google.cloud import vision

import re

import base64

from convertTo import get_by_country, get_all, verify_is_value, verify_is_symbol

from PIL import Image, ImageOps
from io import BytesIO

from currency_converter import CurrencyConverter

import io
import os
import re

app = Flask(__name__)


# root
@app.route("/")
def index():
    return "This is root!!!!"


# set GOOGLE_APPLICATION_CREDENTIALS=C:\Users\ioanm\PycharmProjects\CurrencyverterServerPy\CurrencyverterApp-16f9ccdf4597.json
# CurrencyverterApp-16f9ccdf4597.json


# POST
@app.route('/api/post_some_data', methods=['POST'])
def get_text_prediction():
    json = request.get_json()
    print(json)

    if len(json['text']) == 0:
        return jsonify({'error': 'invalid input'})

    return jsonify({'you sent this': json['text']})


# POST
@app.route('/api/message/', methods=['POST'])
def api_save_base64_image():
    data = request.get_json()

    data2 = request.json

    print(data2)

    message = data['message']

    print(message)

    return message


@app.route('/saver/', methods=['POST'])
def api_save_image():
    data=request.get_json()
    file= data['image']
    starter = file.find(',')
    image_data = file[starter + 1:]
    image_data = bytes(image_data, encoding="ascii")
    im = Image.open(BytesIO(base64.b64decode(image_data)))
    im.save('opa.jpg')
    return 'ok'


def is_number(s):
    aux = re.sub(r'[.$¥€]', '', s)
    return aux.isdigit() and s.find('.') != -1


@app.route('/get_currencys/', methods=['GET'])
def get_currencys():
    return jsonify(get_all())


@app.route('/get_currency_local/', methods=['POST'])
def get_currency():
    data = request.get_json()
    countryCode = data['countryCode']

    convertFrom = get_by_country(countryCode, None)

    if convertFrom is None:
        return 'RON'
    else:
        return 'RON'


@app.route('/api/vision/', methods=['POST'])
def image_vision_converter():
    numbersFound = []
    data = request.get_json()
    file = data['image']
    starter = file.find(',')
    image_data = file[starter + 1:]
    image_data = bytes(image_data, encoding="ascii")
    im = Image.open(BytesIO(base64.b64decode(image_data)))
    im.save('image.jpg')

    img = Image.open("image.jpg")
    area = (200, 50, 500, 430)
    cropped_img = img.crop(area)
    cropped_img.save('save.jpg')

    client = vision.ImageAnnotatorClient()

    # The name of the image file to annotate
    file_name = os.path.join(
        os.path.dirname(__file__),
        'save.jpg')

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)

    texts = response.text_annotations
    print('Texts:')
    for text in texts:
        if len(text.description) != 0:
            print(text.description)
            if is_number(text.description):
                numbersFound.append(re.sub(r'[$¥€]', '', text.description))
            else:
                aux = re.sub(r'[0-9 ]', '', text.description)

                if verify_is_value(aux):
                    data['convertFrom'] = aux

                if verify_is_symbol(aux) is not None:
                    data['convertFrom'] = verify_is_symbol(aux)

    c = CurrencyConverter()

    convertTo = data['convertTo']
    convertFrom = data['convertFrom']

    print('convert from: ' + data['convertFrom'])
    print('convert to: ' + data['convertTo'])

    if len(numbersFound) != 0:
        converted = c.convert(float(numbersFound[0]), convertFrom, convertTo)
        return 'Converted ' + str(numbersFound[0]) + ' ' + convertFrom + ' to ' + str("{:.2f}".format(converted)) + ' ' + convertTo
    else:
        return 'No number detected'


# running web app in local machine
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
