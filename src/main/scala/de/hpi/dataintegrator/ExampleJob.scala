package de.hpi.dataintegrator

import com.datastax.spark.connector._
import de.hpi.ingestion.framework.SparkJob
import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD
import play.api.libs.json.Json

class ExampleJob extends SparkJob {
    var wikidataRaw: RDD[String] = _
//    var outputData: RDD[String] = _

    override def load(sc: SparkContext): Unit = {
        wikidataRaw = sc.textFile("dps/wikidata_dump_small.json")
    }

    override def save(sc: SparkContext): Unit = {
        // save processed data to the cassandra
        // save outputData
    }

    override def run(sc: SparkContext): Unit = {
        wikidataRaw
            .map(_.replaceAll("^\\[|,$|, $|\\]$", ""))
            .collect {
                case line: String if line.nonEmpty => parseRawLine(line)
            }.collect
            .foreach(println)
    }


    def parseRawLine(line: String): String = {
        val json = Json.parse(line)
        (json \ "id").as[String]
    }
}
