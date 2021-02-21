from azureml.pipeline.steps import PythonScriptStep


class EvaluateStep:
    def __init__(self, workspace, env, compute, config, pipeline_parameters):
        self.workspace = workspace
        self.env = env
        self.compute = compute
        self.config = config
        self.pipeline_parameters = pipeline_parameters

    def append_step(self, step_list):
        evaluate_step = PythonScriptStep(
            name="Evaluate Model",
            compute_target=self.compute,
            source_directory=self.env.sources_directory_train,
            script_name=self.env.evaluate_script_path,
            arguments=[
                "--model_name",
                self.pipeline_parameters["model_name"],
                "--allow_run_cancel",
                self.env.allow_run_cancel,
            ],
            runconfig=self.config,
            allow_reuse=False,
        )

        if len(step_list) > 0:
            previous_step = step_list[-1]
            evaluate_step.run_after(previous_step)

        step_list.append(evaluate_step)
