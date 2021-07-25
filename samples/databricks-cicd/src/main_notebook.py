from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from dbcicdlib.some_func import some_func


def create_df(spark):
    data = [("James", 3000), ("Michael", 4000)]
    schema = StructType(
        [
            StructField("name", StringType(), True),
            StructField("salary", IntegerType(), True),
        ]
    )

    return spark.createDataFrame(data=data, schema=schema)


def main():
    spark = SparkSession.builder.appName(
        "Databricks Connect for testing"
    ).getOrCreate()  # noqa: E501
    df = create_df(spark)
    df_new = some_func(df)  # noqa: F405
    df_new.show()


main()
