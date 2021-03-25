from azureml.train.hyperdrive import RandomParameterSampling, BanditPolicy, HyperDriveConfig, PrimaryMetricGoal
from azureml.train.hyperdrive import uniform


class HyperParams:

    def __init(self):
        print(f'HyperParams.Created. version = {VERSION}')

    def get_param_sampling(self):
        return RandomParameterSampling(PARAMETER_SAMPLING)

    def get_bandit_policy(self):
        return BanditPolicy(evaluation_interval=EVALUATION_INTERVAL, slack_factor=SLACK_FACTOR)

    def get_hd_config(self, config):
        hd_config = HyperDriveConfig(
            run_config=config,
            hyperparameter_sampling=self.get_param_sampling(),
            policy=self.get_bandit_policy(),
            primary_metric_name=PRIMARY_METRIC_NAME,
            primary_metric_goal=PRIMARY_METRIC_GOAL,
            max_total_runs=MAX_TOTAL_RUNS,
            max_concurrent_runs=MAX_CONCURRENT_RUNS)
        return hd_config


# https://docs.microsoft.com/azure/machine-learning/how-to-tune-hyperparameters
VERSION = '2021.02.26'
PARAMETER_SAMPLING = {
    '--alpha': uniform(0.05, 1.0)
}
PRIMARY_METRIC_NAME = 'r2'
PRIMARY_METRIC_GOAL = PrimaryMetricGoal.MAXIMIZE
EVALUATION_INTERVAL = 2
SLACK_FACTOR = 0.1
MAX_TOTAL_RUNS = 4
MAX_CONCURRENT_RUNS = 2
