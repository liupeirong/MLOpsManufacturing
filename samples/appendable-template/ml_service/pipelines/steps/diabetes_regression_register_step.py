from azureml.pipeline.steps import PythonScriptStep


class RegisterStep:
    def __init__(self, workspace, env, compute, config, pipeline_parameters,
                 input_pipelinedata):
        self.workspace = workspace
        self.env = env
        self.compute = compute
        self.config = config
        self.pipeline_parameters = pipeline_parameters
        self.input_pipelinedata = input_pipelinedata

    def append_step(self, step_list):
        register_step = PythonScriptStep(
            name="Register Model",
            compute_target=self.compute,
            source_directory=self.env.sources_directory_train,
            script_name=self.env.register_script_path,
            inputs=[self.input_pipelinedata],
            arguments=[
                "--model_name",
                self.pipeline_parameters["model_name"],
                "--step_input",
                self.input_pipelinedata,
            ],
            runconfig=self.config,
            allow_reuse=False,
        )

        if len(step_list) > 0:
            previous_step = step_list[-1]
            register_step.run_after(previous_step)

        step_list.append(register_step)
