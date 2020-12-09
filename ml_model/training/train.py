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

from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Dropout, Flatten, Dense
from keras import optimizers
from keras.preprocessing.image import ImageDataGenerator
from ml_service.util.logger.observability import observability


# Split the dataframe into test and train data
def split_data(data_folder, preprocessing_args):
    img_size = (
        preprocessing_args['image_size']['x'],
        preprocessing_args['image_size']['y'])
    batch_size = preprocessing_args['batch_size']

    observability.log("Getting Data...")
    datagen = ImageDataGenerator(
        rescale=1./255,  # normalize pixel values
        validation_split=0.3)  # hold back 30% of the images for validation

    observability.log("Preparing training dataset...")
    train_generator = datagen.flow_from_directory(
        data_folder,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        subset='training')  # set as training data

    observability.log("Preparing validation dataset...")
    validation_generator = datagen.flow_from_directory(
        data_folder,
        target_size=img_size,
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation')  # set as validation data

    classes = sorted(train_generator.class_indices.keys())
    observability.log(f"class names: {classes}")

    data = {"train": train_generator,
            "test": validation_generator,
            "classes": classes}
    return data


# Train the model, return the model
def train_model(data, train_args, preprocessing_args):
    train_generator = data['train']
    validation_generator = data['test']
    batch_size = preprocessing_args['batch_size']

    # Define a CNN classifier network
    # Define the model as a sequence of layers
    model = Sequential()

    # The input layer accepts an image and applies a convolution
    # that uses 32 6x6 filters and a rectified linear unit activation function
    model.add(Conv2D(
                24,
                (6, 6),
                input_shape=train_generator.image_shape,
                activation='relu'))

    # Next we'll add a max pooling layer with a 2x2 patch
    model.add(MaxPooling2D(pool_size=(2, 2)))

    # We can add as many layers as we think necessary -
    # here we'll add another convolution, max pooling, and dropout layer
    model.add(Conv2D(48, (6, 6), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    # We can add as many layers as we think necessary -
    # here we'll add another convolution, max pooling, and dropout layer
    model.add(Conv2D(96, (6, 6), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    # A dropout layer randomly drops some nodes to
    # reduce inter-dependencies (which can cause over-fitting)
    model.add(Dropout(0.5))

    # Now we'll flatten the feature maps and generate an output
    # layer with a predicted probability for each class
    model.add(Flatten())
    model.add(Dense(train_generator.num_classes, activation='softmax'))

    # With the layers defined, we can now compile the model
    # for categorical (multi-class) classification
    opt = optimizers.Adam(lr=0.001)
    model.compile(loss='categorical_crossentropy',
                  optimizer=opt,
                  metrics=['accuracy'])

    num_epochs = train_args['num_epochs']
    history = model.fit_generator(
        train_generator,
        steps_per_epoch=train_generator.samples // batch_size,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // batch_size,
        epochs=num_epochs)

    return model, history


# Evaluate the metrics for the model
def get_model_metrics(history):
    loss = history.history['loss'][-1]
    accuracy = history.history['accuracy'][-1]
    metrics = {
        'loss': loss,
        'accuracy': accuracy
    }
    return metrics


def main():
    observability.log("Running train.py")

    train_args = {"num_epochs": 10}
    preprocessing_args = {
        "image_size": {"x": 128, "y": 128},
        "batch_size": 30}

    data_dir = "data/processed"
    data = split_data(data_dir, preprocessing_args)
    model, history = train_model(data, train_args, preprocessing_args)

    metrics = get_model_metrics(history)
    for (k, v) in metrics.items():
        observability.log(f"{k}: {v}")


if __name__ == '__main__':
    observability.start_span('train')
    try:
        main()
    except Exception as exception:
        observability.exception(exception)
        raise exception
    finally:
        observability.end_span()
