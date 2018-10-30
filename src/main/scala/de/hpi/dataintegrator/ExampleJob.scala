package de.hpi.dataintegrator

import com.datastax.spark.connector._
import de.hpi.ingestion.framework.SparkJob
import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD


case class Test(a: String, b: Int, c: List[Int])

class ExampleJob extends SparkJob {
//    var inputData: RDD[Test] = _
//    var outputData: RDD[String] = _

    override def load(sc: SparkContext): Unit = {
//        inputData = sc.cassandraTable[Test]("keyspace", "table")
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
//        val test = inputData.flatMap { testEntity =>
//            testEntity.c
//
//        }
//        test
        println("Hallo")
    }
}
