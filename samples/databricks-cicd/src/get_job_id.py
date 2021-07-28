import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--job_name", help="target job name")  # noqa: E501
parser.add_argument(
    "--job_list", help="list of existing jobs from databricks cli"
)  # noqa: E501

args = parser.parse_args()
job_name = args.job_name.lower()

jobs = args.job_list.splitlines()
target_id = ""
for job in jobs:
    kv = job.split(" ", 1)
    id = kv[0]
    name = kv[1].strip()
    if name.lower() == job_name:
        if target_id == "":
            target_id = id
        else:
            raise Exception(
                f"job with same name already exists: {target_id} and {id}"
            )  # noqa: E501

print(target_id)
