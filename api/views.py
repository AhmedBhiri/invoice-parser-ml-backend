from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, FileResponse
from django.middleware.csrf import get_token
from PIL import Image
import os
import io
import zipfile
import json
import base64
from roboflow import Roboflow
import pytesseract
from pytesseract import Output
from django.core.files.uploadedfile import UploadedFile
from pdf2image import convert_from_bytes

ROOT_PATH = os.path.dirname(os.path.abspath(__file__+"/.."))

# loading The invoice model
rfInv = Roboflow(api_key="8rvFh2AP2Wi8X3IhC6kW")
projectInv = rfInv.workspace().project("pfefact")
modelInv = projectInv.version(5).model

# loading The reciept model
rfRec = Roboflow(api_key="8rvFh2AP2Wi8X3IhC6kW")
projectRec = rfRec.workspace().project("pfe-vzxx2")
modelRec = projectRec.version(9).model


def convert_images(image_files):
    converted_images = []
    non_pdf_files = []

    for uploaded_file in image_files:
        if uploaded_file.name.endswith('.pdf'):
            # If the file is a PDF, convert it to images
            pdf_data = uploaded_file.read()
            images = convert_from_bytes(pdf_data)

            for image in images:
                # Create an in-memory file object to simulate an uploaded file
                img_io = io.BytesIO()
                # Save the image to the in-memory file
                image.save(img_io, format='JPEG')
                img_io.seek(0)  # Reset the file position to the beginning

                # Create an UploadedFile instance for the image
                converted_image = UploadedFile(
                    file=img_io,
                    name=uploaded_file.name.replace(
                        '.pdf', f'_page{images.index(image) + 1}.jpg'),
                    content_type='image/jpeg'  # Adjust content type as needed
                )
                converted_images.append(converted_image)
        else:
            # If it's not a PDF, add it to the non-PDF files list
            non_pdf_files.append(uploaded_file)

    # Combine the converted images and non-PDF files into a single list
    image_files = converted_images + non_pdf_files
    return image_files


def OCR_call(image_paths, bounding_boxes):
    detected_text = {}  # Initialize detected_text dictionary
    for image_path, boxes in zip(image_paths, bounding_boxes):
        image_filename = os.path.basename(image_path)
        print(f"Image filename: {image_filename}")
        raw_image_extensions = ['png', 'jpg', 'jpeg']
        raw_image_path = None
        for extension in raw_image_extensions:
            # Remove the extension from image_filename
            filename_without_extension = os.path.splitext(image_filename)[
                0]

            possible_raw_image_path = os.path.join(
                ROOT_PATH, 'raw', f"{filename_without_extension}.{extension}")

            if os.path.exists(possible_raw_image_path):
                raw_image_path = possible_raw_image_path
                print(raw_image_path + " found !")
                break
        if raw_image_path is None:
            continue
        image = Image.open(raw_image_path)

        detected_text_for_image = {}  # Initialize detected text for the current image
        for box in boxes:
            x_center, y_center, width, height = box['x'], box['y'], box['width'], box['height']
            x_top_left = x_center - width / 2
            y_top_left = y_center - height / 2

            x_bottom_right = x_center + width / 2
            y_bottom_right = y_center + height / 2

            cropped_image = image.crop(
                (x_top_left, y_top_left, x_bottom_right, y_bottom_right))
            cropped_image.show()
            # Apply additional preprocessing if needed

            text = pytesseract.image_to_string(
                cropped_image,
                config='--psm 6',  # Page segmentation mode
                output_type=Output.STRING
            )

            class_name = box['class']
            if text.strip():  # Only add non-empty text
                if class_name not in detected_text_for_image:
                    detected_text_for_image[class_name] = []
                detected_text_for_image[class_name].append(text.strip())

        # Assign the detected text for the current image to the dictionary
        detected_text[image_filename] = detected_text_for_image

    return detected_text


def handle_inv_request(request):

    def process_and_predict_image(image_file, save_folder):
        current_directory = ROOT_PATH

        image0 = Image.open(image_file)

        image = image0.resize((640, 640))

        # Get the original filename without the extension
        original_filename = os.path.splitext(image_file.name)[0]

        output_path = os.path.join(
            current_directory, save_folder, f"{original_filename}.png")

        image.save(output_path, format="png")

        prediction = modelInv.predict(
            output_path, confidence=40, overlap=30).json()

        # Save the prediction image
        prediction_image = modelInv.predict(
            output_path, confidence=40, overlap=30)
        predict_path = os.path.join(
            current_directory, "pred", f"{original_filename}.jpg")
        prediction_image.save(predict_path)

        return prediction, predict_path

    def Box_call():
        detected_text = {}
        bounding_boxes = []

        for image_file in image_files:
            prediction, predict_path = process_and_predict_image(
                image_file, "raw")
            # print(prediction)

            response_data.append({
                'prediction': prediction,
                'predict_path': predict_path
            })
            prediction_paths.append(os.path.abspath(
                predict_path))  # Collect the paths

            bounding_boxes.append(prediction['predictions'])

        detected_text = OCR_call(prediction_paths, bounding_boxes)
        # print(bounding_boxes)
        # print(prediction_paths)
        # print(detected_text)
        return detected_text

    if request.method == 'POST':
        response_data = []
        prediction_paths = []  # Collect prediction image paths
        detected_text = {}  # Initialize detected_text dictionary

        # Assuming the input field name is 'images'
        image_files = request.FILES.getlist('images')

        # Convert PDFs to images

        image_files = convert_images(image_files)

        # detection
        detected_text = Box_call()

        combined_response_data = []

        for path in prediction_paths:
            # Add the detected text to the response for each image
            image_filename = os.path.basename(path)
            detected_text_for_image = detected_text.get(image_filename, {})

            # Read and base64-encode the image
            with open(path, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Create a dictionary for each image containing the image data and detected text
            image_response_data = {
                'image_base64': image_base64,
                'detected_text': detected_text_for_image
            }

            combined_response_data.append(image_response_data)

        # Return the combined response data as JSON
        return JsonResponse(combined_response_data, safe=False)
    response_data = []
    prediction_paths = []
    detected_text = {}


def handle_rec_request(request):

    def process_and_predict_image(image_file, save_folder):
        current_directory = ROOT_PATH

        image0 = Image.open(image_file)

        image = image0.resize((640, 640))

        # Get the original filename without the extension
        original_filename = os.path.splitext(image_file.name)[0]

        output_path = os.path.join(
            current_directory, save_folder, f"{original_filename}.png")

        image.save(output_path, format="png")

        prediction = modelRec.predict(
            output_path, confidence=40, overlap=30).json()

        # Save the prediction image
        prediction_image = modelRec.predict(
            output_path, confidence=40, overlap=30)
        predict_path = os.path.join(
            current_directory, "pred", f"{original_filename}.jpg")
        prediction_image.save(predict_path)

        return prediction, predict_path

    def Box_call():
        detected_text = {}
        bounding_boxes = []

        for image_file in image_files:
            prediction, predict_path = process_and_predict_image(
                image_file, "raw")
            # print(prediction)

            response_data.append({
                'prediction': prediction,
                'predict_path': predict_path
            })
            prediction_paths.append(os.path.abspath(
                predict_path))  # Collect the paths

            bounding_boxes.append(prediction['predictions'])

        detected_text = OCR_call(prediction_paths, bounding_boxes)
        # print(bounding_boxes)
        # print(prediction_paths)
        # print(detected_text)
        return detected_text

    if request.method == 'POST':
        response_data = []
        prediction_paths = []  # Collect prediction image paths
        detected_text = {}  # Initialize detected_text dictionary

        image_files = request.FILES.getlist('images')
        # convert pdf to images

        image_files = convert_images(image_files)

        # detection
        detected_text = Box_call()

        combined_response_data = []

        for path in prediction_paths:
            # Add the detected text to the response for each image
            image_filename = os.path.basename(path)
            detected_text_for_image = detected_text.get(image_filename, {})

            # Read and base64-encode the image
            with open(path, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Create a dictionary for each image containing the image data and detected text
            image_response_data = {
                'image_base64': image_base64,
                'detected_text': detected_text_for_image
            }

            combined_response_data.append(image_response_data)

        # Return the combined response data as JSON
        return JsonResponse(combined_response_data, safe=False)
    response_data = []
    prediction_paths = []  # Collect prediction image paths
    detected_text = {}  # Initialize detected_text dictionary


def index(request):
    return render(request, 'index.html')


def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})
