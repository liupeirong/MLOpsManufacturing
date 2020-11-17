import unittest
from unittest.mock import patch, mock_open, MagicMock
from ml_service.mocks.azureml.core.environment import MockedEnvironment,\
    environments
from ml_service.util.manage_environment import get_environment


class TestManageEnvironment(unittest.TestCase):

    # Using mock open to mock all file reads in
    # ml_service.util.manage_environment
    @patch('ml_service.util.manage_environment.open',
           mock_open(read_data='FROM ubuntu'))
    # Function decorator mock for Workspace
    @patch('azureml.core.Workspace')
    # Function decorator mock for staticmethod Environment.list
    @patch('azureml.core.Environment.list',
           return_value=environments)
    # Function decorator mock for instantiation
    # of custom MockedEnvironment objects
    @patch('azureml.core.Environment.__new__',
           lambda x, name: MockedEnvironment(name))
    def test_manage_environment_dockerfile_custommock(self,
                                                      mock_list_environment,
                                                      mocked_workspace):
        """Create a new AML environment with referencing a Dockerfile

        Framework: unittest.mock
                    (https://docs.python.org/3/library/unittest.mock.html)

        Differentiator: Is using a custom mock class for Environment to have
            most control possible. However tracking method calls involves
            custom code.

        Arguments:
            mock_list_environment -- function decorator created mock object
            mocked_workspace -- function decorator created mock object
        """

        result = get_environment(
            mocked_workspace,
            'env_name',
            create_new=True,
            enable_docker=True,
            dockerfile='Dockerfile'
        )  #

        # Assertions
        self.assertIsInstance(result, MockedEnvironment)
        self.assertTrue(result.docker.enabled)
        self.assertEqual(result.name, 'env_name')
        self.assertEqual(result.docker.base_dockerfile,
                         'FROM ubuntu')
        self.assertTrue(result.python.user_managed_dependencies)
        self.assertTrue(mock_list_environment.called)
        self.assertEqual(len(result.called_register), 1)

    # Using mock open to mock all file reads in
    # ml_service.util.manage_environment
    @patch('ml_service.util.manage_environment.open',
           mock_open(read_data='FROM ubuntu'))
    # Function decorator mock for Workspace
    @patch('azureml.core.Workspace')
    # Function decorator mock for staticmethod Environment.list
    @patch('azureml.core.Environment.list',
           return_value=environments)
    # Function decorator mock for instantiation
    # of Environment mock objects
    @patch('azureml.core.Environment.__new__')
    def test_manage_environment_dockerfile_automock(self,
                                                    mock_environment,
                                                    mock_list_environment,
                                                    mocked_workspace):
        """Create a new AML environment with referencing a Dockerfile

        Framework: unittest.mock
                    (https://docs.python.org/3/library/unittest.mock.html)

        Differentiator: Not using any custom mock. While slightly less
            control it is more convenient to track method calls to the cost
            that not all attributes can be asserted.

        Arguments:
            mock_list_environment -- function decorator created mock object
            mocked_workspace -- function decorator created mock object
        """

        result = get_environment(
            mocked_workspace,
            'env_name',
            create_new=True,
            enable_docker=True,
            dockerfile='Dockerfile'
        )  #

        # Assertions
        self.assertIsInstance(result, MagicMock)
        self.assertTrue(result.docker.enabled)
        # Due to nature of Environment mock does not assign name attribute
        # self.assertEqual(result.name, 'env_name')
        self.assertEqual(result.docker.base_dockerfile,
                         'FROM ubuntu')
        self.assertTrue(result.python.user_managed_dependencies)
        self.assertTrue(mock_list_environment.called)
        self.assertTrue(result.register.called)


if __name__ == '__main__':
    unittest.main()
