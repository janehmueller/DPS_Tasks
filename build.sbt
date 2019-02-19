// project definition
lazy val commonSettings = Seq(
	organization := "de.hpi",
	version := "1.0",
	scalaVersion := "2.11.8"
)

// main project
lazy val dps_tasks = (project in file("."))
	.settings(
		commonSettings,
		name := "dps_tasks",
		mainClass in Compile := Some("dps_tasks")
	)

// repositories to use for dependency lookup. the public maven repository is the default lookup repository.
resolvers ++= Seq(
//	"Spark Packages Repo" at "https://dl.bintray.com/spark-packages/maven"
)

// additional dependencies used in the project
// provided flag is used for jars included in the spark environment
// dependencies used for testing are also excluded from assembly jar
// exclude flag is used to exclude conflicting transitive dependencies
libraryDependencies ++= Seq(
	"org.apache.spark" %% "spark-core" % "2.1.0" % "provided" exclude("org.scalatest", "scalatest_2.11"),
	"org.apache.spark" %% "spark-sql" % "2.1.0" % "provided",
	"org.apache.spark" %% "spark-mllib" % "2.1.0" % "provided",
	"org.scalactic" %% "scalactic" % "3.0.4" % "provided",
	"org.scalatest" %% "scalatest" % "3.0.4" % "provided",
	"com.holdenkarau" %% "spark-testing-base" % "2.1.0_0.7.4" % "provided",
    "com.datastax.spark" %% "spark-cassandra-connector" % "2.0.5",
    "io.spray" %%  "spray-json" % "1.3.4"
)

// exclude scala libraries from assembly jar as they are provided by the spark environment
assemblyOption in assembly := (assemblyOption in assembly).value.copy(includeScala = false)

// scala compiler flags for warnings
// also sets source path for correct scala doc source links
scalacOptions in ThisBuild ++= baseDirectory.map { bd =>
	Seq("-deprecation", "-feature", "-sourcepath", bd.getAbsolutePath, "-unchecked")
}.value

// testing settings
logBuffered in Test := false
parallelExecution in Test := false
fork in Test := true
testOptions in Test := Seq(
	Tests.Argument(TestFrameworks.ScalaTest, "-oD"),
	Tests.Argument(TestFrameworks.ScalaTest, "-u", "target/test-reports"))
javaOptions ++= Seq("-Xms512M", "-Xmx4096M", "-XX:+CMSClassUnloadingEnabled")

// fat jar assembly settings
assemblyMergeStrategy in assembly := {
	case PathList("META-INF", xs @ _*) => MergeStrategy.discard
	case PathList(ps @ _*) if ps.last endsWith "pom.properties" => MergeStrategy.discard
	case _ => MergeStrategy.first
}

// disables testing for assembly
test in assembly := {}

// suppresses include info and merge warnings
logLevel in assembly := Level.Error

// scalastyle config
// adds test files to scalastyle check
scalastyleSources in Compile ++= (unmanagedSourceDirectories in Test).value
