#!/bin/bash

# prereq
python -m build --wheel src
name=$(cd src/dist; ls databrickscicd*.whl)
databricks fs mkdirs ${DATABRICKS_DBFS_PATH}

# setup
export DATABRICKS_LIBRARY_PATH=${DATABRICKS_DBFS_PATH}/${name}
databricks fs cp --overwrite src/dist/${name} ${DATABRICKS_DBFS_PATH}
databricks workspace import --overwrite src/main_notebook.py --language PYTHON ${DATABRICKS_WORKSPACE_PATH}/main_notebook.py

# execute
pytest --cache-clear test/test_main_notebook.py

# tear down 
databricks fs rm ${DATABRICKS_DBFS_PATH}/${name}
databricks workspace delete ${DATABRICKS_WORKSPACE_PATH}/main_notebook.py