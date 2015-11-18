rm word.db
cat <<EOF | sqlite3 word.db   
    CREATE TABLE word (hashword int, hashascii int, word text, word_ascii text, type int , meta text );
.separator "\t"
.import dump.tsv word

CREATE INDEX hash_ascii_index on word(hashascii);
CREATE INDEX hash_word_index on word(hashword);

EOF
