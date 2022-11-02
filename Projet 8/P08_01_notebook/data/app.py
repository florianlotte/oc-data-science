import io
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.functions import element_at, split, col, udf
from PIL import Image
from tensorflow.keras.applications.imagenet_utils import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications import ResNet50
from pyspark.ml.linalg import DenseVector, VectorUDT
from pyspark.ml.clustering import KMeans


def main():
    spark = SparkSession.builder.appName('OC-p8').getOrCreate()
    sc = spark.sparkContext
    numPartitions = 24

    s3_uri = "s3://oc-p8/images/**"
    images_df = spark.read.format("binaryFile").option("pathGlobFilter", "*.jpg").load(s3_uri).cache()
    images_df = images_df.withColumn('label', element_at(split(col('path'), '/'),-2))

    model = ResNet50(include_top=False, input_shape=(None, None, 3), weights="imagenet", pooling="avg")
    bc_model_weights = sc.broadcast(model.get_weights())

    @udf(returnType=VectorUDT())
    def features_vectorizer(content):
        img = Image.open(io.BytesIO(content))
        arr = img_to_array(img)
        arr = preprocess_input(arr)
        model = ResNet50(include_top=False, input_shape=arr.shape, weights=None, pooling="avg")
        model.set_weights(bc_model_weights.value)
        features = model.predict(np.array([arr]))
        return DenseVector(features.flatten())

    features_df = images_df.repartition(numPartitions).select('path', 'label', features_vectorizer('content').alias('features'))

    features_df.select('path', 'label', 'features').toPandas().to_csv("s3://oc-p8/training_features_result.csv")

    # k = features_df.select("label").distinct().count()
    #
    # kmeans = KMeans(k=k, seed=1)
    # kmeans.setFeaturesCol('features')
    # kmeans.setPredictionCol('prediction')
    #
    # kmeans_model = kmeans.fit(features_df.select('features'))
    # cluster_df = kmeans_model.transform(features_df)

    # cluster_df.select('path', 'label', 'features', 'prediction').toPandas().to_csv("s3://oc-p8/training_predictions_result.csv")


if __name__ == "__main__":
    main()
