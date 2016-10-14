ADDR="localhost"
if [ $# -eq 1 ]
then
    ADDR="$1"
else
    ADDR="localhost"
fi
curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field-type":{
    "name":"sentence",
    "class":"solr.TextField",
    "positionIncrementGap":"100",
    "analyzer":{
      "tokenizer":{
        "class":"solr.StandardTokenizerFactory" },
      "filters":[{
        "class":"solr.StopFilterFactory",
        "words":"lang/stopwords_en.txt",
        "ignoreCase":true}, {
        "class":"solr.LowerCaseFilterFactory"}, {
        "class":"solr.EnglishPossessiveFilterFactory"}, {
        "class":"solr.KeywordMarkerFilterFactory",
        "protected":"protwords.txt"}, {
        "class":"solr.KStemFilterFactory"}]}},
  "add-field" : {
    "name":"sent",
    "type":"sentence",
    "stored":true,
    "indexed":true },
  "add-field" : {
    "name":"res1",
    "type":"sentence",
    "stored":true,
    "multiValued":true,
    "indexed":true },
  "add-field" : {
    "name":"res2",
    "type":"sentence",
    "stored":true,
    "multiValued":true,
    "indexed":true },
  "add-field" : {
    "name":"res3",
    "type":"string",
    "stored":true,
    "multiValued":true,
    "indexed":false }
}' http://"$1":8983/solr/syntax/schema
