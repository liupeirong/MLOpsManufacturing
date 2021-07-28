def some_func(df):
    return df.withColumn("bonus", df.salary * 10)
