from azureml.core.environment import DockerSection, PythonSection


class MockedEnvironment:
    """Mock of azureml.core.Environment

    Arguments:
        workspace - AMLs Workspace
    """
    called_register = None

    def __init__(self, name, **kwargs):
        self.docker = DockerSection()
        self.python = PythonSection()
        self.name = name

    def register(self, workspace):
        if self.called_register is None:
            self.called_register = [workspace]
        return self

    @staticmethod
    def list(workspace):
        return environments


# Mock Accessors
environments = {"env_name2": MockedEnvironment("env_name2")}
