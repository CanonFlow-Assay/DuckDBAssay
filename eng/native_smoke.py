"""Real DuckDB 2.0 behavior and settings; requires its pinned Python binding."""
import json
from pathlib import Path
import tempfile
import sys
import duckdb

ROOT=Path(__file__).resolve().parents[1]


def run():
    assert duckdb.__version__=='2.0.0'
    cases=['exact engine version']
    with tempfile.TemporaryDirectory(prefix='duckdb-assay-native-') as tmp:
        base=Path(tmp);db=base/'test.duckdb';spill=base/'spill';spill.mkdir()
        conn=duckdb.connect(str(db),config={'memory_limit':'256 MiB','threads':2,'allow_unsigned_extensions':False})
        try:
            conn.execute('SET temp_directory=?',[str(spill)]);conn.execute("SET max_temp_directory_size='1 GiB'")
            conn.execute('CREATE TABLE orders(id INTEGER PRIMARY KEY,quantity INTEGER NOT NULL CHECK(quantity>0),amount DECIMAL(10,2),note VARCHAR)')
            conn.execute('INSERT INTO orders VALUES(?,?,?,?)',[1,2,'0.30',None]);cases.append('parameterized valid insert')
            try:conn.execute('INSERT INTO orders VALUES(2,0,0.10,NULL)')
            except duckdb.ConstraintException:pass
            else:raise AssertionError('invalid quantity accepted')
            cases.append('invalid quantity rejected')
            conn.execute('BEGIN');conn.execute('UPDATE orders SET quantity=9 WHERE id=1');conn.execute('ROLLBACK')
            assert conn.execute('SELECT quantity FROM orders').fetchone()[0]==2;cases.append('rollback retains prior state')
            injection="x'); DROP TABLE orders; --"
            conn.execute('UPDATE orders SET note=? WHERE id=1',[injection]);assert conn.execute('SELECT note FROM orders').fetchone()[0]==injection
            cases.append('parameter input remains data')
            assert str(conn.execute('SELECT 0.1::DECIMAL(10,2)+0.2::DECIMAL(10,2)').fetchone()[0])=='0.30';cases.append('exact decimal arithmetic')
            parquet=base/'orders.parquet';conn.execute('COPY orders TO ? (FORMAT PARQUET)',[str(parquet)])
            assert conn.execute('SELECT count(*) FROM read_parquet(?)',[str(parquet)]).fetchone()[0]==1;cases.append('Parquet round trip')
            assert conn.execute('SELECT typeof(42::VARIANT)').fetchone()[0]=='VARIANT';cases.append('2.0 VARIANT type available')
            values=dict(conn.execute('SELECT name,value FROM duckdb_settings()').fetchall())
            keys=['memory_limit','threads','temp_directory','max_temp_directory_size','allow_unsigned_extensions']
            settings={k: int(values[k]) if k=='threads' else values[k]=='true' if k=='allow_unsigned_extensions' else values[k] for k in keys}
            snapshot={'schemaVersion':1,'product':'duckdb','version':'2.0.0','settings':settings}
        finally:conn.close()
        check=duckdb.connect(str(db),read_only=True)
        try:assert check.execute('SELECT count(*) FROM orders').fetchone()[0]==1;cases.append('persistent reopen')
        finally:check.close()
        restricted=duckdb.connect(config={'memory_limit':'128 MiB','threads':1,'allow_unsigned_extensions':False,'allow_community_extensions':False,'autoinstall_known_extensions':False,'autoload_known_extensions':False,'enable_external_access':False})
        try:
            restricted.execute('SET lock_configuration=true')
            try:restricted.execute('SET threads=4')
            except duckdb.Error:pass
            else:raise AssertionError('locked configuration changed')
            cases.append('locked configuration rejects change')
            try:restricted.execute('SELECT * FROM read_parquet(?)',[str(parquet)])
            except duckdb.Error:pass
            else:raise AssertionError('external file access escaped restriction')
            cases.append('external file access denied by configured boundary')
            raw=dict(restricted.execute('SELECT name,value FROM duckdb_settings()').fetchall())
            untrusted={'schemaVersion':1,'product':'duckdb','version':'2.0.0','settings':{k:int(v) if k=='threads' else v=='true' if v in ('true','false') else v for k,v in raw.items() if k in ['memory_limit','threads','allow_unsigned_extensions','allow_community_extensions','autoinstall_known_extensions','autoload_known_extensions','enable_external_access','lock_configuration']}}
        finally:restricted.close()
        out=ROOT/'artifacts';out.mkdir(exist_ok=True)
        (out/'native-snapshot.json').write_text(json.dumps(snapshot,indent=2)+'\n')
        (out/'native-untrusted-snapshot.json').write_text(json.dumps(untrusted,indent=2)+'\n')
    return {'status':'Pass','engineVersion':duckdb.__version__,'cases':cases,'expectedSnapshotVerdict':'Inconclusive without configured tests; Pass with retained native-result acceptance',
            'limits':'Local small-data semantics and defense-in-depth settings only; not whole-process isolation, measured spill performance, Quack, S3 or concurrency qualification.'}


if __name__ == "__main__":
    if sys.argv[1:3] == ["--profile", "parquet-compatibility"]:
        from parquet_native import main
        main(sys.argv[3:])
    elif len(sys.argv) == 1:
        result = run()
        (ROOT / "artifacts/native-results.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
    else:
        raise SystemExit("unsupported native profile")
