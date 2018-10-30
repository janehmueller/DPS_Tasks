package de.hpi.dataintegrator

import com.holdenkarau.spark.testing.SharedSparkContext
import org.scalatest.FlatSpecLike

class ExampleJobTest extends FlatSpecLike with SharedSparkContext {
    "An example job" should "do something" in {
        val job = new ExampleJob
        job.load(sc)
        job.run(sc)
    }
}
