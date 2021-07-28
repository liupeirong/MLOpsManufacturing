from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from dbcicdlib.some_func import some_func


def test_some_func(spark):
    data = [("James", 3000), ("Michael", 4000)]
    schema = StructType(
        [
            StructField("name", StringType(), True),
            StructField("salary", IntegerType(), True),
        ]
    )
    df_input = spark.createDataFrame(data=data, schema=schema)
    df_output = some_func(df_input)  # noqa: F405

    data_out = [("James", 3000, 30000), ("Michael", 4000, 40000)]
    schema_out = StructType(
        [
            StructField("name", StringType(), True),
            StructField("salary", IntegerType(), True),
            StructField("bonus", IntegerType(), True),
        ]
    )
    df_expected = spark.createDataFrame(data=data_out, schema=schema_out)

    assert df_output.collect() == df_expected.collect()
