import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    spark = SparkSession.builder.appName(
        "databricks connect tests"
    ).getOrCreate()  # noqa: E501
    return spark
