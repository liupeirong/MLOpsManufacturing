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
from azureml.core import Run
import argparse
import json
from util.model_helper import get_model, get_aml_context


def evaluate_model_performs_better(model, run):
    metric_eval = "accuracy"
    production_model_accuracy = 0
    if (metric_eval in model.tags):
        production_model_accuracy = float(model.tags[metric_eval])
    new_model_accuracy = float(run.parent.get_metrics().get(metric_eval))
    if (production_model_accuracy is None or new_model_accuracy is None):
        raise Exception(f"Unable to find {metric_eval} metrics, exiting evaluation")  # NOQA: E501
    else:
        print(f"Current model accuracy: {production_model_accuracy}, new model accuracy: {new_model_accuracy}")  # NOQA: E501

    if (new_model_accuracy > production_model_accuracy):
        print("New model performs better")
        return True
    else:
        print("New model doesn't perform better")
        return False


def parse_ml_params(run, ml_params):
    if ml_params is None or ml_params == "":
        with open("parameters.json") as f:
            pars = json.load(f)
    else:
        pars = json.loads(ml_params)
    evaluate_args = pars["evaluation"]
    print(f"evaluation parameters {evaluate_args}")
    for (k, v) in evaluate_args.items():
        run.log(k, v)
        run.parent.log(k, v)

    cancel_if_perform_worse = \
        evaluate_args['cancel_if_perform_worse'].lower() == 'true'
    return cancel_if_perform_worse


def main():
    run = Run.get_context()
    ws, exp, run_id = get_aml_context(run)

    parser = argparse.ArgumentParser("evaluate")
    parser.add_argument(
        "--run_id",
        type=str,
        help="Training run ID",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        help="Name of the Model"
    )
    parser.add_argument(
        "--ml_params",
        type=str,
        help="Parameters for ML pipelne in json format with defaults defined in parameters.json",  # NOQA: E501
    )

    args = parser.parse_args()
    if (args.run_id is not None):
        run_id = args.run_id
    if (run_id == 'amlcompute'):
        run_id = run.parent.id
    model_name = args.model_name
    tag_name = 'experiment_name'

    cancel_if_perform_worse = parse_ml_params(run, args.ml_params)

    model = get_model(
                model_name=model_name,
                tag_name=tag_name,
                tag_value=exp.name,
                aml_workspace=ws)

    if (model is not None):
        should_register = evaluate_model_performs_better(model, run)
        if((not should_register) and cancel_if_perform_worse):
            run.parent.cancel()
    else:
        print("This is the first model, register it")


if __name__ == '__main__':
    main()
