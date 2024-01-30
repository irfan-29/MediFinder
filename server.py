from PIL import Image
import pytesseract
from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory
from bson import ObjectId, json_util
from pymongo import MongoClient
import json
import os
import base64

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Irfan\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
app = Flask(__name__)


def get_data_from_mongodb(text1):
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client.MediData
        collection1 = db.collection1
        collection2 = db.collection2

        for x in text1:
            if " " in x:
                newText = x.split(" ")
                for y in newText:
                    # condition = {"Medicine Name": { "$regex": f"^{y}"}}
                    condition = {"Medicine Name": y}
                    data_from_mongodb = collection1.find_one(condition)
                    if(data_from_mongodb!=None):
                        return data_from_mongodb
            else:
                # condition = {"Medicine Name": { "$regex": f"^{x}"}}
                condition = {"Medicine Name": x}
                data_from_mongodb = collection1.find_one(condition)
                if(data_from_mongodb!=None):
                    return data_from_mongodb
        for x in text1:
            if " " in x:
                newText = x.split(" ")
                for y in newText:
                    condition = {"Medicine Name": { "$regex": f"^{y}"}}
                    # condition = {"Medicine Name": y}
                    data_from_mongodb = collection2.find_one(condition)
                    if(data_from_mongodb!=None):
                        return data_from_mongodb
            else:
                condition = {"Medicine Name": { "$regex": f"^{x}"}}
                # condition = {"Medicine Name": x}
                data_from_mongodb = collection2.find_one(condition)
                if(data_from_mongodb!=None):
                    return data_from_mongodb

    except Exception as e:
        print("Error connecting to MongoDB:", str(e))
        return None

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/perform_ocr', methods=['POST'])
def perform_ocr():
    try:
        image_file = request.files['image_file']

        if image_file and allowed_file(image_file.filename):
            old_name = extract_image_name()
            filename = old_name
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(file_path)

            img = Image.open(file_path)

            text = pytesseract.image_to_string(img)
            text=text.lower()

            text1=text.splitlines()
            print(text1)

            if text1 is not None and text1 != '':
                data_from_mongodb = get_data_from_mongodb(text1)

                image_old_name = extract_image_name()
                image_new_name = data_from_mongodb['Medicine Name']

                rename(image_old_name, image_new_name)

                # Convert ObjectId to string for serialization
                if data_from_mongodb:
                    data_from_mongodb['_id'] = str(data_from_mongodb['_id'])
                    return redirect(url_for('result', serialized_data=json.dumps(data_from_mongodb)))
                else:
                    # return jsonify({'error': 'No data found in MongoDB for OCR result'}), 500
                    return redirect(url_for('error'))
            else:
                # return jsonify({'error': 'OCR result is None or empty'}), 500
                return redirect(url_for('error'))
    except Exception as e:
        return redirect(url_for('error'))


@app.route('/error')
def error():
    return render_template('error.html')


@app.route('/text_input', methods=['GET', 'POST'])
def text_input():
    if request.method == "POST":
       text = request.form.get("text")
       text1=[]
       text1.append(text)
       print(text1)
       if text1 is not None and text1 != '':
                data_from_mongodb = get_data_from_mongodb(text1)

                if data_from_mongodb:
                    data_from_mongodb['_id'] = str(data_from_mongodb['_id'])
                    return redirect(url_for('result', serialized_data=json.dumps(data_from_mongodb)))
                else:
                    return redirect(url_for('error'))
       else:
            return redirect(url_for('error'))


def extract_image_name():
    try:
        files = os.listdir('./uploads')

        image_files = [file for file in files if file.lower().endswith(('.png', '.jpg'))]
        if len(image_files) == 1:
            print("old name", image_files[0])
            return image_files[0]
        elif len(image_files) == 0:
            print("No image files found in the folder.")

    except Exception as e:
        print(f"An error occurred: {e}")


def rename(old_name, new_name):
    try:
        os.rename('uploads/'+old_name, 'uploads/'+new_name+'.jpg')
    except FileNotFoundError:
        print("Error...")


# Image
@app.route('/result/<serialized_data>')
def result(serialized_data):
    return render_template('result.html', serialized_data=serialized_data)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(image)
        return extracted_text
    except Exception as e:
        return f'Error extracting text: {str(e)}'


FULL_PATH = r'C:\Users\Irfan\PycharmProjects\Medicine_Finder\venv\captures\captured_image.jpg'

@app.route('/capture', methods=['POST'])
def capture():
    try:
        # Get the captured image data from the POST request
        captured_image_data = request.form['captured_image']

        # Process the image data (base64 encoded) as needed
        image_data = base64.b64decode(captured_image_data.split(',')[1])

        # Save the image to the specified full path
        with open(FULL_PATH, 'wb') as f:
            f.write(image_data)

        # Extract text from the captured image using pytesseract
        extracted_text = extract_text_from_image(FULL_PATH)

        extracted_text=extracted_text.lower()
        text1=extracted_text.splitlines()
        print(text1)
        if len(text1) == 0:
            return redirect(url_for('error'))
        else:
            data_from_mongodb= get_data_from_mongodb(text1)
            if data_from_mongodb:
                data_from_mongodb['_id'] = str(data_from_mongodb['_id'])
                return redirect(url_for('result', serialized_data=json.dumps(data_from_mongodb)))
            else:
                return redirect(url_for('error'))
            return redirect(url_for('result', serialized_data=json.dumps(data_from_mongodb)))

    except Exception as e:
        return f'Error: {str(e)}'


if __name__ == '__main__':
    app.run(debug=True)

