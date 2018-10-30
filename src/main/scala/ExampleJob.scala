import de.hpi.ingestion.framework.SparkJob
import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD

class ExampleJob extends SparkJob {
    var inputData: RDD[String] = _
    var outputData: RDD[String] = _

    override def load(sc: SparkContext): Unit = {
        // load input data from cassandra or hdfs
        // inputData = something
    }

    override def save(sc: SparkContext): Unit = {
        // save processed data to the cassandra
        // save outputData
    }

    override def run(sc: SparkContext): Unit = {
        // proccess input data
        // outputData = something
    }
}
