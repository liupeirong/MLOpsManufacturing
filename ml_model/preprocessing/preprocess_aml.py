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
import argparse
import json
from ml_model.preprocessing.preprocess_images import resize_images
from ml_model.util.model_helper import get_or_register_dataset, get_aml_context
from ml_service.util.logger.observability import Observability

observability = Observability()


def main():
    observability.start_span()
    observability.log("Running preprocess.py")

    parser = argparse.ArgumentParser("preprocess")
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
        help=("Datastore name. If none, use the default datastore")
    )

    parser.add_argument(
        "--data_file_path",
        type=str,
        help=("data file path, if specified,\
               a new version of the dataset will be registered")
    )

    parser.add_argument(
        "--output_dataset",
        type=str,
        help=("output of processed data")
    )

    parser.add_argument(
        "--preprocessing_param",
        type=str,
        help=("image pre-processing parameters")
    )

    args = parser.parse_args()

    print("Argument [dataset_name]: %s" % args.dataset_name)
    print("Argument [datastore_name]: %s" % args.datastore_name)
    print("Argument [data_file_path]: %s" % args.data_file_path)
    print("Argument [output_dataset]: %s" % args.output_dataset)
    print("Argument [preprocessing_param]: %s" % args.preprocessing_param)

    data_file_path = args.data_file_path
    dataset_name = args.dataset_name
    datastore_name = args.datastore_name
    output_dataset = args.output_dataset
    preprocessing_param = args.preprocessing_param

    run = Run.get_context()
    aml_workspace, *_ = get_aml_context(run)

    if preprocessing_param is None or preprocessing_param == "":
        with open("parameters.json") as f:
            pars = json.load(f)
            preprocessing_args = pars["preprocessing"]
    else:
        preprocessing_args = json.loads(preprocessing_param)
    observability.log(f"preprocessing parameters {preprocessing_args}")
    for (k, v) in preprocessing_args.items():
        run.log(k, v)
        run.parent.log(k, v)

    dataset = get_or_register_dataset(
        dataset_name,
        datastore_name,
        data_file_path,
        aml_workspace)

    # Link dataset to the step run so it is trackable in the UI
    run.input_datasets['flower_dataset_raw'] = dataset

    # Process data
    mount_context = dataset.mount()
    mount_context.start()
    observability.log(f"mount_point is: {mount_context.mount_point}")
    resize_images(mount_context.mount_point, output_dataset, preprocessing_args)  # NOQA: E501
    mount_context.stop()

    run.tag("run_type", value="preprocess")
    observability.log(f"tags now present for run: {run.tags}")

    run.complete()

    observability.end_span()


if __name__ == '__main__':
    try:
        main()
    except Exception as exception:
        observability.exception(exception)
        raise exception
