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
from azureml.core.run import Run
import os
import argparse
import json
from train import split_data, train_model, get_model_metrics
from util.model_helper import get_or_register_dataset


def main():
    print("Running train_aml.py")

    parser = argparse.ArgumentParser("train")
    parser.add_argument(
        "--model_name",
        type=str,
        help="Name of the Model"
    )

    parser.add_argument(
        "--step_output",
        type=str,
        help=("output for passing data to next step")
    )

    parser.add_argument(
        "--data_file_path",
        type=str,
        help=("data file path, if specified,\
               a new version of the dataset will be registered")
    )

    parser.add_argument(
        "--dataset_name",
        type=str,
        help=("Dataset name. Dataset must be passed by name\
              to always get the desired dataset version\
              rather than the one used while the pipeline creation")
    )

    parser.add_argument(
        "--datastore_name",
        type=str,
        help=("Datastore name.")
    )
    args = parser.parse_args()

    print("Argument [model_name]: %s" % args.model_name)
    print("Argument [step_output]: %s" % args.step_output)
    print("Argument [data_file_path]: %s" % args.data_file_path)
    print("Argument [dataset_name]: %s" % args.dataset_name)
    print("Argument [datastore_name]: %s" % args.datastore_name)

    model_name = args.model_name
    step_output_path = args.step_output
    data_file_path = args.data_file_path
    dataset_name = args.dataset_name
    datastore_name = args.datastore_name

    run = Run.get_context()

    print("Getting training parameters")

    # Load the training parameters from the parameters file
    with open("parameters.json") as f:
        pars = json.load(f)
    try:
        preprocessing_args = pars["preprocessing"]
        train_args = pars["training"]
    except KeyError:
        print("Could not load preprocessing or training values from file")
        train_args = {}
        preprocessing_args = {}

    # Log the training parameters
    print(f"Parameters: {preprocessing_args}")
    for (k, v) in preprocessing_args.items():
        run.log(k, v)
        run.parent.log(k, v)
    print(f"Parameters: {train_args}")
    for (k, v) in train_args.items():
        run.log(k, v)
        run.parent.log(k, v)

    # Get the dataset
    dataset = get_or_register_dataset(
        dataset_name=dataset_name,
        datastore_name=datastore_name,
        data_file_path=data_file_path,
        aml_workspace=run.experiment.workspace
    )

    # Link dataset to the step run so it is trackable in the UI
    run.input_datasets['training_data'] = dataset
    run.parent.tag("dataset_id", value=dataset.id)

    # Train the model
    # mount the dynamic version of the dataset, which can't be determined at pipeline publish time  # NOQA: E501
    mount_context = dataset.mount()
    mount_context.start()
    print(f"mount_point is: {mount_context.mount_point}")
    data = split_data(mount_context.mount_point, preprocessing_args)
    model, history = train_model(data, train_args, preprocessing_args)
    mount_context.stop()

    # Evaluate and log the metrics returned from the train function
    metrics = get_model_metrics(history)
    for (k, v) in metrics.items():
        run.log(k, v)
        run.parent.log(k, v)

    # Pass model file to next step
    os.makedirs(step_output_path, exist_ok=True)
    model_output_path = os.path.join(step_output_path, model_name)
    model.save(model_output_path)
    with open(os.path.join(step_output_path, "run_id.txt"), "w") as text_file:
        print(f"{run.id}", file=text_file)

    # Also upload model file to run outputs for history
    os.makedirs('outputs', exist_ok=True)
    output_path = os.path.join('outputs', model_name)
    model.save(output_path)

    run.tag("run_type", value="train")
    print(f"tags now present for run: {run.tags}")

    run.complete()


if __name__ == '__main__':
    main()
