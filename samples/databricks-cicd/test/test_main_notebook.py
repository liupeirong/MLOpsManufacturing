import sys
import os
from dotenv import load_dotenv

sys.path.append("./")
from execute_notebook import *  # noqa: F403, E402


def test_main():
    load_dotenv()
    shard = os.environ["DATABRICKS_HOST"]
    token = os.environ["DATABRICKS_TOKEN"]
    workspace_path = os.environ["DATABRICKS_WORKSPACE_PATH"]
    library_path = os.environ["DATABRICKS_LIBRARY_PATH"]
    outfile_path = os.environ["DATABRICKS_OUTFILE_PATH"]
    notebook_name = "main_notebook.py"

    print(
        f"running notebook {notebook_name}, output will be in {outfile_path}"
    )  # noqa: E501

    json_output = execute_notebook(  # noqa: F405
        shard, token, library_path, notebook_name, workspace_path, outfile_path
    )

    assert json_output["state"]["result_state"] == "SUCCESS"


if __name__ == "__main__":
    test_main()
