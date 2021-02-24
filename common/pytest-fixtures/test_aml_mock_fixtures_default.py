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
import pytest
from pytest_mock import MockFixture
from unittest.mock import MagicMock, mock_open
from azureml.core.workspace import Workspace
from azureml.core.compute.amlcompute import AmlCompute
from azureml.data.abstract_datastore import AbstractDatastore


@pytest.fixture
def aml_pipeline_mocks(mocker: MockFixture):
    """ aml_pipeline
        Fixture - needs to be "imported" by test case via parameters

        Sets mocks for AML SDK related to AML Pipeline build scripts:
            - Workspace.Get
            - PythonScriptStep
            - Pipeline
            - Pipeline.publish
            - ComputeTarget (AmlCompute only)
            - Environment

        returns tuple of mock objects
        (workspace, amlcompute, mock_workspace_get, mock_pipeline_publish)
    """
    # Specify default values
    compute_name = 'utest_computename'
    subscription_id = 'utest_subid'
    resource_group = 'utest_rg'
    workspace_name = 'utest_workspace'
    datastore_name = 'utest_datastore'

    # Mock file read in Conda Dependencies
    mocker.patch('azureml.core.conda_dependencies.open',
                 mock_open(read_data='name: unit_test'))

    # Mock external dependencies in workspace retrieval
    mocker.patch('azureml.core.authentication.perform_interactive_login')
    mocker.patch('azureml.core.authentication.InteractiveLoginAuthentication.'
                 '_check_if_subscription_exists', return_value=True)

    # Mock workspace retrieval
    # Object of azureml.core.workspace.Workspace
    workspace = Workspace(subscription_id=subscription_id,
                          resource_group=resource_group,
                          workspace_name=workspace_name,
                          _disable_service_check=True)

    mock_workspace_get = mocker.patch('azureml.core.Workspace.get',
                                      return_value=workspace)

    # Object of azureml.core.compute.amlcompute.AmlCompute
    amlcd = {
             "name": compute_name, "location": "mocklocation", "tags": "",
             "properties": {
                            "properties": {}, "provisioningErrors": "",
                            "provisioningState": "", "resourceId": "",
                            "description": "", "computeType": "AmlCompute",
                            "isAttachedCompute": "false"
                           }
            }

    mocker.patch('azureml.core.compute.compute.ComputeTarget._get',
                 return_value=amlcd)
    amlcompute = AmlCompute(workspace=workspace, name=compute_name)
    ct = {compute_name: amlcompute}
    mocker.patch('azureml.core.Workspace.compute_targets',
                 return_value=ct)

    # Mock ComputeTarget create
    mocker.patch('azureml.core.compute.compute.ComputeTarget.create',
                 return_value=amlcompute)

    # Mock External dependency in azureml.core.compute.amlcompute.AmlCompute
    mocker.patch('azureml.core.compute.amlcompute.AmlCompute._wait_for_nodes',
                 return_value=(True, False, False, False))

    # Mock the environment to return a already existing environment
    mocker.patch('azureml.core.Environment.list',
                 return_value={"mock_env_name":
                               MagicMock(spec='azureml.core.Environment')
                               })

    # Skip real registering of Environment
    mocker.patch('azureml.core.Environment.register')

    # Mock for Datastore
    ds = AbstractDatastore(workspace=workspace, name=datastore_name,
                           datastore_type='mocked')
    mocker.patch('azureml.core.Datastore.__new__',
                 return_value=ds)

    # Additional dependency mocks for Pipeline object
    # to be created successfully
    mocker.patch('azureml.core.workspace.Workspace.service_context')
    mocker.patch('azureml.core.workspace.Workspace.get_default_datastore',
                 return_value=ds)
    # Enables the Pipeline object to be CREATED without external call
    mocker.patch('azureml.pipeline.core._aeva_provider'
                 '._AevaWorkflowProvider.create_provider')

    mock_pipeline_publish = mocker.patch('azureml.pipeline.core.'
                                         'Pipeline.publish')

    return (workspace, amlcompute, mock_workspace_get, mock_pipeline_publish)
