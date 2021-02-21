from azureml.pipeline.steps import PythonScriptStep


class TrainStep:
    def __init__(self, workspace, env, compute, config, pipeline_parameters,
                 output_pipelinedata):
        self.workspace = workspace
        self.env = env
        self.compute = compute
        self.config = config
        self.pipeline_parameters = pipeline_parameters
        self.output_pipelinedata = output_pipelinedata

    def append_step(self, step_list):
        train_step = PythonScriptStep(
            name="Train Model",
            compute_target=self.compute,
            source_directory=self.env.sources_directory_train,
            script_name=self.env.train_script_path,
            outputs=[self.output_pipelinedata],
            arguments=[
                "--model_name",
                self.pipeline_parameters["model_name"],
                "--step_output",
                self.output_pipelinedata,
                "--dataset_version",
                self.pipeline_parameters["dataset_version"],
                "--data_file_path",
                self.pipeline_parameters["data_file_path"],
                "--caller_run_id",
                self.pipeline_parameters["caller_run_id"],
                "--dataset_name",
                self.env.dataset_name,
            ],
            runconfig=self.config,
            allow_reuse=True,
        )

        if len(step_list) > 0:
            previous_step = step_list[-1]
            train_step.run_after(previous_step)

        step_list.append(train_step)
