from azureml.pipeline.core import PublishedPipeline
from azureml.core import Experiment, Workspace
from ml_service.util.env_variables import Env
import argparse


def main():
    parser = argparse.ArgumentParser("register")
    parser.add_argument(
        "--output_pipeline_id_file",
        type=str,
        default="preprocessing_pipeline_id.txt",
        help="Name of a file to write pipeline ID to"
    )
    parser.add_argument(
        "--skip_preprocessing_execution",
        action="store_true",
        help=("Do not trigger the execution. "
              "Use this in Azure DevOps when using a server job to trigger")
    )
    args = parser.parse_args()

    e = Env()

    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group
    )

    # Find the pipeline that was published by the specified build ID
    pipelines = PublishedPipeline.list(aml_workspace)
    matched_pipes = []

    # TODO: delete latest_version logic
    latest_version = 0
    latest_pipe = None
    for p in pipelines:
        if p.name == e.preprocessing_pipeline_name:
            if p.version == e.build_id:
                matched_pipes.append(p)
            elif int(p.version) > latest_version:
                latest_version = int(p.version)
                latest_pipe = p

    if len(matched_pipes) == 0 and latest_version > 0:
        matched_pipes.append(latest_pipe)

    if(len(matched_pipes) > 1):
        published_pipeline = None
        raise Exception(f"Multiple active pipelines are published for build {e.build_id}.")  # NOQA: E501
    elif(len(matched_pipes) == 0):
        published_pipeline = None
        raise KeyError(f"Unable to find a published pipeline for this build {e.build_id}")  # NOQA: E501
    else:
        published_pipeline = matched_pipes[0]
        print("published pipeline id is", published_pipeline.id)

        # Save the Pipeline ID for other AzDO jobs after script is complete
        if args.output_pipeline_id_file is not None:
            with open(args.output_pipeline_id_file, "w") as out_file:
                out_file.write(published_pipeline.id)

        if(args.skip_preprocessing_execution is False):
            tags = {"BuildId": e.build_id}
            if (e.build_uri is not None):
                tags["BuildUri"] = e.build_uri
            experiment = Experiment(
                workspace=aml_workspace,
                name=e.experiment_name + "_preprocess")
            run = experiment.submit(
                published_pipeline,
                tags=tags)

            print("Pipeline run initiated ", run.id)


if __name__ == "__main__":
    main()
