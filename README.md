# esl
esl

所有脚本直接使用python .py即可运行
使用数据库为MongoClient("127.0.0.1", 27017).test.syntax2，身份验证user: test, password: test
执行顺序为
newdb.py建立数据库（要求同一目录包含list.txt，其中包含parse过的txt列表）
getstemmer.py获取数据库中所有stemmer（要求.jar文件在同一目录下）
updatestemmer.py更新数据库上的stemmer
