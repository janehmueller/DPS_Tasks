package de.hpi.dataintegrator

import com.holdenkarau.spark.testing.SharedSparkContext
import org.scalatest.FlatSpecLike

class WikidataParserTest extends FlatSpecLike with SharedSparkContext {
    "An example job" should "do something" in {
        val job = new WikidataParser
        job.wikidataRaw = sc.textFile("dps/wikidata_dump_small.json")
        job.run(sc)
    }
}
