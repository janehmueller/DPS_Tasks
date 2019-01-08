package de.hpi.dataintegrator.models

case class RawWikidataData(
    id: String,
    entitytype: Option[String] = None,
    labels: Map[String, String] = Map(),
    descriptions: Map[String, String] = Map(),
    aliases: Map[String, List[String]] = Map(),
    sitelinks: Map[String, Sitelink] = Map(),
    claims: Map[String, List[Property]] = Map()
)

case class Sitelink(
    site: String,
    title: String,
    badges: List[String] = Nil
)

case class Property(
    propertytype: Option[String],
    claimtype: Option[String],
    snaktype: Option[String],
    value: Option[String]
)
