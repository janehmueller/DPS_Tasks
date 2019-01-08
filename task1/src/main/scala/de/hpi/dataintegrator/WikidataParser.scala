package de.hpi.dataintegrator

import com.datastax.spark.connector._
import de.hpi.ingestion.framework.SparkJob
import org.apache.spark.SparkContext
import org.apache.spark.rdd.RDD
import spray.json._
import DefaultJsonProtocol._
import de.hpi.dataintegrator.models.{Property, RawWikidataData, Sitelink}

class WikidataParser extends SparkJob {
    appName = "Wikidata Parser"
    var wikidataRaw: RDD[String] = _
    var parsedWikidata: RDD[RawWikidataData] = _

    override def load(sc: SparkContext): Unit = {
        wikidataRaw = sc.textFile("dps/wikidata.json")
    }

    override def save(sc: SparkContext): Unit = {
         parsedWikidata.saveToCassandra("dps", "wikidata")
    }

    override def run(sc: SparkContext): Unit = {
        parsedWikidata = wikidataRaw
            .map(_.replaceAll("^\\[|,$|, $|\\]$", ""))
            .collect {
                case line: String if line.nonEmpty => parseRawLine(line)
            }
    }

    implicit class JsonASTTraversal(json: JsValue) {
        def \(field: String): JsValue = {
            json.asJsObject.fields(field)
        }

        def get(field: String*): Option[JsValue] = {
            def next(field: String, json: Option[JsValue]) = json.flatMap(_.asJsObject.fields.get(field))

            try {
                field.foldRight(Option(json))(next)
            } catch {
                case e: spray.json.DeserializationException =>
                    println(s"Traversing path $field in ${json.toString()}")
                    None
            }
        }

        def getAsString(field: String*): Option[String] = {
            json.get(field:_*).map(_.convertTo[String])
        }

        def getAsDouble(field: String*): Option[Double] = {
            json.get(field:_*).map(_.convertTo[Double])
        }

        def getAsStringList(field: String*): List[String] = {
            json.get(field:_*).map(_.convertTo[List[String]]).toList.flatten
        }
    }

    def parseToStringMap(jsonField: JsValue, valueField: String): Map[String, String] = {
        jsonField
            .asJsObject
            .fields
            .flatMap { case (keyField, jsonSubfield) =>
                val value = jsonSubfield.getAsString(valueField)
                value.map((keyField, _))
            }
    }

    def parseToSitelinkMap(jsonField: JsValue): Map[String, Sitelink] = {
        jsonField
            .asJsObject
            .fields
            .map { case (wikiPage, jsonSubfield) =>
                val title = jsonSubfield.getAsString("title").get
                val badges = jsonSubfield.getAsStringList("badges")
                val sitelink = Sitelink(wikiPage, title, badges)
                (wikiPage, sitelink)
            }
    }

    def claimPropertyPathMap: Map[String, List[String]] = Map(
        "string" -> List("value"),
        "wikibase-entityid" -> List("value", "id"),
        "time" -> List("value", "time"),
        "monolingualtext" -> List("value", "text"))

    def parseClaim(jsonField: JsValue): Property = {
        val snakOpt = jsonField.get("mainsnak", "datavalue", "value")
        val valueType = snakOpt.flatMap(_.getAsString("mainsnak", "datavalue", "type"))
        val snakValue = valueType
            .flatMap(claimPropertyPathMap.get)
            .flatMap { path =>
                snakOpt.map { snak => path.foldRight(snak)((subPath, subJsonField) => subJsonField \ subPath) }
            }.map(_.convertTo[String])
        val specialSnakValue = valueType.collect {
            case "globecoordinate" =>
                val latitude = snakOpt.flatMap(_.getAsDouble("latitude"))
                val longitude = snakOpt.flatMap(_.getAsDouble("longitude"))
                s"${latitude.getOrElse("")};${longitude.getOrElse("")}"
            case "quantity" =>
                val amount = snakOpt.flatMap(_.getAsString("amount"))
                val unit = snakOpt.flatMap(_.getAsString("unit")).map(_.split("/").last)
                s"${amount.getOrElse("")};${unit.getOrElse("")}"
            }
        Property(
            propertytype = valueType,
            claimtype = jsonField.getAsString("type"),
            snaktype = jsonField.getAsString("mainsnak", "datatype"),
            value = snakValue.orElse(specialSnakValue)
        )
    }

    def parseToClaimMap(jsonField: JsValue): Map[String, List[Property]] = {
        jsonField
            .asJsObject
            .fields
            .map { case (propertyId, jsonSubfield) =>
                val properties = jsonSubfield
                    .convertTo[List[JsValue]]
                    .map(parseClaim)
                (propertyId, properties)
            }
    }


    def parseRawLine(line: String): RawWikidataData = {
        val json = line.parseJson

        val aliases = (json \ "aliases")
            .asJsObject
            .fields
            .map { case (language, jsonSubfield) =>
                val values = jsonSubfield
                    .convertTo[List[JsValue]]
                    .flatMap(_.getAsString("value"))
                (language, values)
            }

        RawWikidataData(
            id = (json \ "id").convertTo[String],
            entitytype = json.getAsString("type"),
            labels = json.get("labels").map(parseToStringMap(_, "value")).getOrElse(Map()),
            descriptions = json.get("descriptions").map(parseToStringMap(_, "value")).getOrElse(Map()),
            aliases = aliases,
            sitelinks = json.get("sitelinks").map(parseToSitelinkMap).getOrElse(Map()),
            claims = json.get("claims").map(parseToClaimMap).getOrElse(Map())
        )
    }
}
