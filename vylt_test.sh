#!/usr/bin/env bash
set -euo pipefail

export VYLT_PASSWORD="pass123"

pip install -e . >/dev/null

rm -rf testdata testdata.*.vylt orig.sha dec.sha

mkdir -p testdata/level1/level2

dd if=/dev/urandom of=testdata/big1.bin bs=1M count=30 status=none
dd if=/dev/urandom of=testdata/level1/big2.bin bs=1M count=20 status=none
echo "hello vylt" > testdata/readme.txt
echo "nested file" > testdata/level1/level2/info.txt

du -sh testdata

find testdata -type f -exec sha256sum {} \; | sort > orig.sha

vylt encrypt testdata
vylt info testdata.*.vylt
vylt list testdata.*.vylt

rm -rf testdata
vylt decrypt testdata.*.vylt

find testdata -type f -exec sha256sum {} \; | sort > dec.sha
diff orig.sha dec.sha

rm -rf testdata testdata.*.vylt orig.sha dec.sha

mkdir -p testdata/level1/level2

dd if=/dev/urandom of=testdata/big1.bin bs=1M count=30 status=none
dd if=/dev/urandom of=testdata/level1/big2.bin bs=1M count=20 status=none
echo "hello vylt" > testdata/readme.txt
echo "nested file" > testdata/level1/level2/info.txt

find testdata -type f -exec sha256sum {} \; | sort > orig.sha

vylt encrypt testdata --seal-meta
vylt info testdata.*.vylt
vylt list testdata.*.vylt

rm -rf testdata
vylt decrypt testdata.*.vylt

find testdata -type f -exec sha256sum {} \; | sort > dec.sha
diff orig.sha dec.sha

rm -rf testdata testdata.*.vylt orig.sha dec.sha

vylt setup
