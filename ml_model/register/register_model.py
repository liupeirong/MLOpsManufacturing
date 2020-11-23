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
import os
import sys
import argparse
import traceback
from azureml.core import Run
from azureml.core.model import Model as AMLModel
from ml_model.util.model_helper import get_aml_context


def find_child_run(parent_run, child_run_id):
    found_run = None
    runs = parent_run.get_children()
    for r in runs:
        if r.id == child_run_id:
            found_run = r
            break
    return found_run


def find_run(experiment, run_id):
    found_run = None
    runs = experiment.get_runs()
    for r in runs:
        if r.id == run_id:
            found_run = r
            break
    return found_run


def main():
    run = Run.get_context()
    ws, exp, run_id = get_aml_context(run)

    parser = argparse.ArgumentParser("register")

    parser.add_argument(
        "--run_id",
        type=str,
        help="Parent run ID for the training pipeline",
    )

    parser.add_argument(
        "--model_name",
        type=str,
        help="Name of the Model",
    )

    parser.add_argument(
        "--step_input",
        type=str,
        help=("input from previous steps")
    )

    args = parser.parse_args()
    if (args.run_id is not None):
        run_id = args.run_id
        run = find_run(exp, run_id)
    if (run_id == 'amlcompute'):
        run_id = run.parent.id
        run = run.parent
    print(f"parent run_id is {run_id}")
    model_name = args.model_name
    model_path = args.step_input

    print("Getting registration parameters")

    # Load the registration parameters from the parameters file
    with open("parameters.json") as f:
        pars = json.load(f)
    try:
        register_args = pars["registration"]
    except KeyError:
        print("Could not load registration values from file")
        register_args = {"tags": []}

    model_tags = {}
    for tag in register_args["tags"]:
        try:
            mtag = run.get_metrics()[tag]
            model_tags[tag] = mtag
        except KeyError:
            print(f"Could not find {tag} metric on parent run.")

    parent_tags = run.get_tags()
    try:
        build_id = parent_tags["BuildId"]
    except KeyError:
        build_id = None
        print("BuildId tag not found on parent run.")
        print(f"Tags present: {parent_tags}")
    try:
        build_uri = parent_tags["BuildUri"]
    except KeyError:
        build_uri = None
        print("BuildUri tag not found on parent run.")
        print(f"Tags present: {parent_tags}")

    print(f"Loading training run_id from {model_path}")
    run_id_file = os.path.join(model_path, "run_id.txt")
    with open(run_id_file, "r") as text_file:
        training_run_id = text_file.read().replace('\n', '')

    # the parent pipeline run consists of training, evaluation, and registration  # NOQA: E501
    training_run = find_child_run(run, training_run_id)

    if training_run is not None:
        if (build_id is None):
            register_aml_model(
                model_name,
                model_tags,
                exp,
                training_run)
        elif (build_uri is None):
            register_aml_model(
                model_name,
                model_tags,
                exp,
                training_run,
                build_id)
        else:
            register_aml_model(
                model_name,
                model_tags,
                exp,
                training_run,
                build_id,
                build_uri)
    else:
        print("Training run not found. Skipping model registration.")
        sys.exit(0)


def model_already_registered(model_name, exp, run_id):
    model_list = AMLModel.list(exp.workspace, name=model_name, run_id=run_id)
    if len(model_list) >= 1:
        raise Exception(f"Model name: {model_name} in workspace {exp.workspace} with run_id {run_id} is already registered.")  # NOQA: E501
    else:
        print("Model is not registered for this run.")


def register_aml_model(
    model_name,
    model_tags,
    exp,
    run,
    build_id: str = 'none',
    build_uri=None
):
    try:
        tagsValue = {}
        tagsValue.update(model_tags)
        if (build_id != 'none'):
            model_already_registered(model_name, exp, run.id)
            tagsValue["BuildId"] = build_id
            if (build_uri is not None):
                tagsValue["BuildUri"] = build_uri

        model = run.register_model(
            model_name=model_name,
            model_path=os.path.join("outputs", model_name),
            tags=tagsValue)
        print(
            "Model registered: {} \nModel Description: {} "
            "\nModel Version: {}".format(
                model.name, model.description, model.version
            )
        )
    except Exception:
        traceback.print_exc(limit=None, file=None, chain=True)
        print("Model registration failed")
        raise


if __name__ == '__main__':
    main()
