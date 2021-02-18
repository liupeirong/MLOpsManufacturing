import click
import subprocess
from logging import getLogger, INFO, StreamHandler, Formatter
from azureml.core import Run, Dataset


def run(input_dataset_name: str, waves_dataset_name: str):
    logger.info('start the process')
    logger.info(f"input dataset name: {input_dataset_name}")
    logger.info(f"waves dataset name: {waves_dataset_name}")

    run = Run.get_context()
    workspace = run.experiment.workspace
    input_dataset = Dataset.get_by_name(workspace=workspace, name=input_dataset_name)
    input_dataset.download(target_path='input', overwrite=True)
    wave_dataset = Dataset.get_by_name(workspace=workspace, name=waves_dataset_name)
    wave_dataset.download(target_path='waves_yesno', overwrite=True)

    # Run run.sh 
    results = subprocess.run(['bash', 'run.sh'], capture_output=True, encoding='utf-8')

    logger.info(results.stdout)
    logger.info(results.stderr)

    # Get generated model and register it to Azure ML model store
    model_name = 'yesno_model'
    upload_folder_name = 'models'

    run.upload_folder(name=upload_folder_name, path='exp/mono0a')
    model = run.register_model(model_name=model_name,
                               model_path=upload_folder_name,
                               description='Generted model in Azure ML')
    logger.info(f'Model registered: {model.name}')
    logger.info(f'Model version: {model.version}')


@click.command()
@click.option("--input_dataset_name", type=str, help="Name of input dataset", default="input")
@click.option("--waves_dataset_name", type=str, help="Name of waves dataset", default="waves")
def main(input_dataset_name: str, waves_dataset_name: str):
    run(input_dataset_name, waves_dataset_name)


if __name__ == "__main__":
    logger = getLogger(__name__)
    logger.setLevel(INFO)
    logger.propagate = False
    sh = StreamHandler()
    sh.setFormatter(Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(sh)
    main()
