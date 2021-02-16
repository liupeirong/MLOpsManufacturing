import time
from azureml.core \
    import Workspace, ScriptRunConfig, Experiment, Environment # noqa E402

# comment below when package is installed from PyPI
import sys
import os
libpath = os.path.join(sys.path[0], '..')
sys.path.append(libpath)

from azureml_appinsights_logger.observability \
    import Observability, Severity # noqa E402


logger = Observability()
run_on_local = False


def main():
    """
    Minimum sample to use the Observability logger
    in Azure ML Run or alone
    """

    pwd = sys.path[0]
    # Submit an Azure ML Run which uses the logger
    aml_ws = Workspace.from_config()
    aml_exp = Experiment(aml_ws, 'test_logger')
    aml_env = Environment.from_conda_specification(
        'test_logger_env', f'{pwd}/conda_dependency.yml')
    # if aml_cluster isn't specified, it'll run locally but
    # will still log to AML and AppInsights
    if run_on_local:
        aml_config = ScriptRunConfig(source_directory=pwd,
                                     script='train.py',
                                     environment=aml_env)
    else:
        aicxn = 'APPLICATIONINSIGHTS_CONNECTION_STRING'
        aml_env.environment_variables[aicxn] = os.environ[aicxn]
        aml_cluster = aml_ws.compute_targets['train-cluster']
        aml_config = ScriptRunConfig(source_directory=pwd,
                                     script='train.py',
                                     environment=aml_env,
                                     compute_target=aml_cluster)
    aml_exp.submit(aml_config)

    # Use the logger directly
    logger.log("Shouldn't log INFO if default severity is WARNING")
    logger.log("Run into ERROR", severity=Severity.ERROR)
    logger.log_metric(name="metric1_no_parent", value=100)
    logger.log_metric(name="metric2_with_parent", value=200, log_parent=True)
    try:
        raise Exception("Run into EXCEPTION")
    except Exception as ex:
        logger.exception(ex)
    # allow time for appinsights exporter to send metrics
    time.sleep(30)


if __name__ == "__main__":
    logger.start_span("demo_span")
    try:
        main()
    except Exception as ex:
        logger.exception(ex)
    finally:
        logger.end_span()
