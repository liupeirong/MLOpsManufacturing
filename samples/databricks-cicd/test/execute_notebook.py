import json
import requests
import os
import time


def execute_notebook(
    shard,
    token,
    library_path,
    notebook_name,
    workspace_path,
    outfile_path,  # noqa: E501
):
    full_workspace_path = os.path.join(workspace_path, notebook_name)

    print("Running job for:" + notebook_name)
    values = {
        "run_name": notebook_name,
        "new_cluster": {
            "spark_version": "7.3.x-scala2.12",
            "spark_conf": {
                "spark.master": "local[*, 4]",
                "spark.databricks.cluster.profile": "singleNode",
            },
            "num_workers": 1,
            "azure_attributes": {
                "availability": "ON_DEMAND_AZURE",
                "first_on_demand": 1,
                "spot_bid_max_price": -1,
            },
            "node_type_id": "Standard_DS3_v2",
            "custom_tags": {"ResourceClass": "SingleNode"},
            "spark_env_vars": {
                "PYSPARK_PYTHON": "/databricks/python3/bin/python3"
            },  # noqa: E501
            "enable_elastic_disk": True,
        },
        "libraries": [{"whl": library_path}],
        "timeout_seconds": 3600,
        "notebook_task": {"notebook_path": full_workspace_path},
    }

    assert not shard.endswith("/")
    resp = requests.post(
        shard + "/api/2.0/jobs/runs/submit",
        data=json.dumps(values),
        auth=("token", token),
    )
    runjson = resp.text
    print("runjson:" + runjson)
    d = json.loads(runjson)
    runid = d["run_id"]

    i = 0
    waiting = True
    while waiting:
        time.sleep(10)
        jobresp = requests.get(
            shard + "/api/2.0/jobs/runs/get?run_id=" + str(runid),
            data=json.dumps(values),
            auth=("token", token),
        )
        jobjson = jobresp.text
        print("jobjson:" + jobjson)
        j = json.loads(jobjson)
        current_state = j["state"]["life_cycle_state"]
        runid = j["run_id"]
        if (
            current_state in ["TERMINATED", "INTERNAL_ERROR", "SKIPPED"]
            or i >= 60  # noqa: E501
        ):
            break
        i = i + 1

    if outfile_path != "":
        file = open(outfile_path + "/" + str(runid) + ".json", "w")
        file.write(json.dumps(j))
        file.close()

    return j
