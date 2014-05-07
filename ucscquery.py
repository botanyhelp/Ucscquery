"""Basic standalone program to query UCSC Genome Browser Mysql database

Requires module MySQLdb
Requires internet access
Hardcoded username and database.  Only the database will need to be changed by you...you would change 'mm9' to 'hg19' if you want to change from Mouse to Human organism. 

This program performs steps that can be run manually like this:

mysql --user=genome --host=genome-mysql.cse.ucsc.edu -A
mysql> use mm9;
Database changed
mysql> select * from knownCanonical;

The UCSC Genome Browser provides a public mysql server.  Python program ucscquery.py shows how to query that server.  The public server, username and password are embedded in the program.  There are hundreds of databases, one for each assembly.  The program hardcodes the mm9 assembly of the Mouse organism.  The query execution returns a long, which we promptly convert to an int.  We then use that to fetch every record one at a time in a loop.  Understanding the databases and their tables is not easy.  The schema is designed primarily to support the genome browser at genome.ucsc.edu.  Even so, clever querying is possible.  Good luck.

This program was started in order to query the Publications tables in hg19 and/or mm9.  The idea is to find the genomic locations of interest in published papers in order to find other papers that are also concerned with that same genomic location.  A use case, for example, might be to find the genomic locations of interest in papers by a certain author.  And then look at that location in the genome browser (http://genome.ucsc.edu), with Publications track not hidden!, and see the other papers listed there.  Or, better yet, search by paper author name (in the program, no web browser) to get list of other authors who have written a paper concerned with the similar location in the genome.  As you can see, very little program code progress.  

Finding papers in the genome browser for an author name can be attempted like this, from the mysql command line, for one G Kelleher:

mysql> select pubsBlat.chrom,pubsBlat.chromStart,pubsBlat.chromEnd FROM hg19.pubsBlat WHERE pubsBlat.name IN (SELECT pubsArticle.articleId FROM hgFixed.pubsArticle WHERE hgFixed.pubsArticle.firstAuthor='Kelleher' AND hgFixed.pubsArticle.authors LIKE '%G%' AND hgFixed.pubsArticle.dbs='hg19');
+-------+------------+-----------+
| chrom | chromStart | chromEnd  |
+-------+------------+-----------+
| chr11 |  125482931 | 125489911 |
| chr22 |   23465585 |  23465610 |
| chr3  |   31666487 |  31677553 |
| chr3  |  128348904 | 128356783 |
| chr8  |   15621938 |  15621962 |
| chrX  |   77150844 |  77150885 |
+-------+------------+-----------+
6 rows in set (2.88 sec)

...and then you can search hg19 for those locations at genome.ucsc.edu with the Publications track set to be viewable.  If its your paper, you will probably know some of the names of nearby authors in the browser image.  Other papers you may not know and may be worth investigating.  For the first result sequence in the query output above, we would go to here:

http://genome.ucsc.edu/cgi-bin/hgTracks?db=hg19&position=chr11%3A125482931-125489911 

..and we would notice Kelleher2003 on the publications track. If we click on that Kelleher2003 line we go to here:

http://genome.ucsc.edu/cgi-bin/hgc?c=chr11&o=125482931&t=125489911&g=pubsBlat&i=2003306527

...to see some notes on the paper.  Sequences in Articles: PubmedCentral and Elsevier (2003306527) page.  

If we instead go to the second location in our query output (above) chr22:23,465,585-23,465,610 then we see three papers: Kelleher2001, Zhou2000 and Pauwels2001 with the Kelleher paper at:

http://genome.ucsc.edu/cgi-bin/hgc?c=chr22&o=23465585&t=23465610&g=pubsBlat&i=2001451864

If we got to the chromosome 8 location in our query: chr8:15621938-15621962 then we see two papers:

http://genome.ucsc.edu/cgi-bin/hgc?c=chr8&o=15615314&t=15621995&g=pubsBlat&i=2000679657

http://genome.ucsc.edu/cgi-bin/hgc?c=chr8&o=15621938&t=15621962&g=pubsBlat&i=2003306527

To correlate sequence location and published papers is tricky business.  Here we see the schema for two important tables and the indexes in both:

mysql> describe hg19.pubsBlat;
+-------------+----------------------+------+-----+---------+-------+
| Field       | Type                 | Null | Key | Default | Extra |
+-------------+----------------------+------+-----+---------+-------+
| bin         | smallint(5) unsigned | NO   |     | NULL    |       |
| chrom       | varchar(255)         | NO   | MUL | NULL    |       |
| chromStart  | int(10) unsigned     | NO   |     | NULL    |       |
| chromEnd    | int(10) unsigned     | NO   |     | NULL    |       |
| name        | varchar(255)         | NO   | MUL | NULL    |       |
| score       | int(10) unsigned     | NO   |     | NULL    |       |
| strand      | char(1)              | NO   |     | NULL    |       |
| thickStart  | int(10) unsigned     | NO   |     | NULL    |       |
| thickEnd    | int(10) unsigned     | NO   |     | NULL    |       |
| reserved    | int(10) unsigned     | NO   |     | NULL    |       |
| blockCount  | int(10) unsigned     | NO   |     | NULL    |       |
| blockSizes  | longblob             | NO   |     | NULL    |       |
| chromStarts | longblob             | NO   |     | NULL    |       |
| tSeqTypes   | varchar(255)         | NO   |     | NULL    |       |
| seqIds      | blob                 | NO   |     | NULL    |       |
| seqRanges   | blob                 | NO   |     | NULL    |       |
+-------------+----------------------+------+-----+---------+-------+
16 rows in set (0.09 sec)

mysql> describe hgFixed.pubsArticle;
+-------------+----------------+------+-----+---------+-------+
| Field       | Type           | Null | Key | Default | Extra |
+-------------+----------------+------+-----+---------+-------+
| articleId   | bigint(20)     | NO   | PRI | NULL    |       |
| extId       | varchar(255)   | NO   | MUL | NULL    |       |
| pmid        | bigint(20)     | NO   |     | NULL    |       |
| doi         | varchar(255)   | NO   |     | NULL    |       |
| source      | varchar(255)   | NO   |     | NULL    |       |
| citation    | varchar(2000)  | YES  | MUL | NULL    |       |
| year        | int(11)        | NO   |     | NULL    |       |
| title       | varchar(6000)  | YES  |     | NULL    |       |
| authors     | varchar(12000) | YES  |     | NULL    |       |
| firstAuthor | varchar(255)   | YES  |     | NULL    |       |
| abstract    | varchar(32000) | NO   |     | NULL    |       |
| url         | varchar(1000)  | YES  |     | NULL    |       |
| dbs         | varchar(500)   | YES  |     | NULL    |       |
+-------------+----------------+------+-----+---------+-------+
13 rows in set (0.08 sec)

mysql> show index from hgFixed.pubsArticle
    -> ;
+-------------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
| Table       | Non_unique | Key_name | Seq_in_index | Column_name | Collation | Cardinality | Sub_part | Packed | Null | Index_type | Comment | Index_comment |
+-------------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
| pubsArticle |          0 | PRIMARY  |            1 | articleId   | A         |     2257588 |     NULL | NULL   |      | BTREE      |         |               |
| pubsArticle |          1 | extIdx   |            1 | extId       | A         |     2257588 |     NULL | NULL   |      | BTREE      |         |               |
| pubsArticle |          1 | citation |            1 | citation    | NULL      |           9 |     NULL | NULL   | YES  | FULLTEXT   |         |               |
| pubsArticle |          1 | citation |            2 | title       | NULL      |           9 |     NULL | NULL   | YES  | FULLTEXT   |         |               |
| pubsArticle |          1 | citation |            3 | authors     | NULL      |           9 |     NULL | NULL   | YES  | FULLTEXT   |         |               |
| pubsArticle |          1 | citation |            4 | abstract    | NULL      |           9 |     NULL | NULL   |      | FULLTEXT   |         |               |
+-------------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
6 rows in set (0.09 sec)

mysql> show index from hg19.pubsBlat;
+----------+------------+-------------------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
| Table    | Non_unique | Key_name          | Seq_in_index | Column_name | Collation | Cardinality | Sub_part | Packed | Null | Index_type | Comment | Index_comment |
+----------+------------+-------------------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
| pubsBlat |          1 | name              |            1 | name        | A         |       86852 |       16 | NULL   |      | BTREE      |         |               |
| pubsBlat |          1 | chrom             |            1 | chrom       | A         |         110 |        6 | NULL   |      | BTREE      |         |               |
| pubsBlat |          1 | chromStartAndName |            1 | chrom       | A         |         110 |        6 | NULL   |      | BTREE      |         |               |
| pubsBlat |          1 | chromStartAndName |            2 | chromStart  | A         |      260558 |     NULL | NULL   |      | BTREE      |         |               |
| pubsBlat |          1 | chromStartAndName |            3 | name        | A         |      260558 |     NULL | NULL   |      | BTREE      |         |               |
| pubsBlat |          1 | binChrom          |            1 | chrom       | A         |         189 |     NULL | NULL   |      | BTREE      |         |               |
| pubsBlat |          1 | binChrom          |            2 | bin         | A         |       52111 |     NULL | NULL   |      | BTREE      |         |               |
+----------+------------+-------------------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+
7 rows in set (0.09 sec)

mysql>

This program sets up the connection, queries a table in the mm9 database, and loops through the results:
"""

import MySQLdb
conn = MySQLdb.connect(host='genome-mysql.cse.ucsc.edu', user='genome', db='mm9')
curs = conn.cursor()
sql = 'SELECT * FROM knownCanonical'
count = int(curs.execute(sql))
for i in range(count):
    curs.fetchone()
