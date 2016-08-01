# esl
esl

所有脚本直接使用python ***.py即可运行
使用数据库为MongoClient("127.0.0.1", 27017).test.syntax2，身份验证user: test, password: test
执行顺序为
newdb.py建立数据库
getstemmer.py获取数据库中所有stemmer
updatestemmer.py更新数据库上的stemmer
