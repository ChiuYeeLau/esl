ADDR="localhost"
if [ $# -eq 1 ]
then
    ADDR=$1
else
    ADDR="localhost"
fi
TEST="curl http://$ADDR:8983/solr/syntax/update/?stream.body=%3Cdelete%3E%3Cquery%3E*:*%3C/query%3E%3C/delete%3E&stream.contentType=text/xml;charset=utf-8&commit=true"
$TEST

