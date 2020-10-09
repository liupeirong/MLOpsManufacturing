"""
Copyright (C) Microsoft Corporation. All rights reserved.​
 ​
Microsoft Corporation (“Microsoft”) grants you a nonexclusive, perpetual,
royalty-free right to use, copy, and modify the software code provided by us
("Software Code"). You may not sublicense the Software Code or any use of it
(except to your affiliates and to vendors to perform work on your behalf)
through distribution, network access, service agreement, lease, rental, or
otherwise. This license does not purport to express any claim of ownership over
data you may have shared with Microsoft in the creation of the Software Code.
Unless applicable law gives you more rights, Microsoft reserves all other
rights not expressly granted herein, whether by implication, estoppel or
otherwise. ​
 ​
THE SOFTWARE CODE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
MICROSOFT OR ITS LICENSORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THE SOFTWARE CODE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
import json
import numpy as np
from keras.models import load_model
from azureml.core.model import Model
from azureml.contrib.services.aml_request import rawhttp
import gzip


def init():
    global model

    # we assume that we have just one model
    model_path = Model.get_model_path('flower_classifier')
    model = load_model(model_path)


@rawhttp
def run(request):
    try:
        # raw_data is gziped
        raw_data = request.get_data()
        return internal_run(raw_data)

    except Exception as e:
        result = str(e)
        return json.dumps({"error": result})


def internal_run(raw_data):
    json_data = gzip.decompress(raw_data).decode('utf-8')
    data = np.array(json.loads(json_data)['data'])
    predicted_classes = predict_image(model, data)
    json_result = json.dumps(predicted_classes)
    return json_result


def predict_image(classifier, image_array):
    imgfeatures = image_array.astype('float32')
    imgfeatures /= 255

    # These are the classes our model can predict
    classnames = ['daisy', 'dandelion', 'roses', 'sunflowers', 'tulips']

    # Predict the class of each input image
    predictions = classifier.predict(imgfeatures)

    predicted_classes = []
    for prediction in predictions:
        class_idx = np.argmax(prediction)
        predicted_classes.append(classnames[int(class_idx)])
    return predicted_classes


if __name__ == "__main__":
    import requests
    from io import BytesIO
    from PIL import Image
    from preprocessing.preprocess_images import resize_image
    from dotenv import load_dotenv
    import os

    # Test scoring
    load_dotenv()
    url_str = os.environ.get("TEST_IMAGE_URLS")
    class_str = os.environ.get("TEST_IMAGE_CLASSES")
    image_urls = url_str.split(',') 
    image_classes = class_str.split(',')
    if len(image_urls) != len(image_classes):
        raise "number of urls is not same as number of classes"

    with open("parameters.json") as f:
        pars = json.load(f)
        image_size = pars["preprocessing"]["image_size"]
        size = (image_size["x"], image_size["y"])

    init()
    img_array = []
    for url_idx in range(len(image_urls)):
        response = requests.get(image_urls[url_idx])
        img = Image.open(BytesIO(response.content))
        img = np.array(resize_image(img, size))
        img_array.append(img.tolist())

    input_json = json.dumps({"data": img_array})
    compressed = gzip.compress(input_json.encode('utf-8'))
    predictions = internal_run(compressed)
    predicted_classes = json.loads(predictions)
    for (p, a) in zip(predicted_classes, image_classes):
        if p != a:
            raise f"prediction {p} is not same as actual {a}"
    print("Test result: ", predicted_classes)
