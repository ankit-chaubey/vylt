#!/usr/bin/env bash
set -uo pipefail

echo "🚀 VYLT FULL XYZ INTEGRATION TEST (TRULY FINAL)"

export VYLT_PASSWORD="pass123"
FAILED_STEPS=0

run_step() {
  local label="$1"
  shift
  echo -n "$label... "
  if "$@"; then
    echo "✅"
  else
    echo "❌ FAILED"
    FAILED_STEPS=$((FAILED_STEPS + 1))
  fi
}

cleanup() {
  rm -rf testdata restored *.vylt orig.sha dec.sha sel.sha
}

cleanup

# -------------------------------------------------
echo "[1/10] Creating test dataset"
mkdir -p testdata/level1/level2
dd if=/dev/urandom of=testdata/big1.bin bs=1M count=30 status=none
dd if=/dev/urandom of=testdata/level1/big2.bin bs=1M count=20 status=none
echo "hello vylt" > testdata/readme.txt
echo "nested file" > testdata/level1/level2/info.txt
(cd testdata && find . -type f -exec sha256sum {} \;) | sort > orig.sha
echo "✔ Test data created"

# -------------------------------------------------
run_step "[2/10] Encrypt directory" vylt encrypt testdata

run_step "[3/10] Info + list" bash -c "
  vylt info testdata.*.vylt >/dev/null &&
  vylt list testdata.*.vylt >/dev/null
"

# -------------------------------------------------
echo "[4/10] Rename + decrypt"
mv testdata.*.vylt renamed.vylt
rm -rf testdata

run_step "      Decrypt renamed" vylt decrypt renamed.vylt --out restored

TARGET_DIR=$(find restored -name readme.txt -exec dirname {} \;)
(cd "$TARGET_DIR" && find . -type f -exec sha256sum {} \;) | sort > dec.sha
run_step "      Integrity check" diff orig.sha dec.sha

# -------------------------------------------------
echo "[5/10] Selective extraction (CORRECT ROOT)"
rm -rf restored

run_step "      Extract testdata/level1/*" \
  vylt decrypt renamed.vylt --only "testdata/level1/*" --out restored

find restored -type f > sel.sha

run_step "      Contains big2.bin" \
  grep -E '(^|/)big2\.bin$' sel.sha

run_step "      Contains info.txt" \
  grep -E '(^|/)info\.txt$' sel.sha

run_step "      Excludes big1.bin" \
  bash -c "! grep -E '(^|/)big1\.bin$' sel.sha"

# -------------------------------------------------
echo "[6/10] Encrypt with sealed metadata"
cleanup
mkdir -p testdata/level1
echo "data" > testdata/a.bin
echo "secret" > testdata/level1/secret.txt
(cd testdata && find . -type f -exec sha256sum {} \;) | sort > orig.sha

export VYLT_PASSWORD="sealed_pass"
vylt encrypt testdata --seal-meta

# -------------------------------------------------
run_step "[7/10] Sealed list does not leak names" bash -c '
  OUT=$(VYLT_PASSWORD=wrong vylt list testdata.*.vylt 2>/dev/null || true)
  echo "$OUT" | grep -q "secret.txt" && exit 1 || exit 0
'

# -------------------------------------------------
echo "[8/10] Decrypt sealed archive"
export VYLT_PASSWORD="sealed_pass"

run_step "      Decrypt sealed" \
  vylt decrypt testdata.*.vylt --out restored

TARGET_DIR=$(find restored -name a.bin -exec dirname {} \;)
(cd "$TARGET_DIR" && find . -type f -exec sha256sum {} \;) | sort > dec.sha
run_step "      Sealed integrity" diff orig.sha dec.sha

# -------------------------------------------------
run_step "[9/10] Diagnostics" vylt setup

# -------------------------------------------------
echo "[10/10] Cleanup"
cleanup
unset VYLT_PASSWORD

echo "---------------------------------------"
if [ "$FAILED_STEPS" -eq 0 ]; then
  echo "🎉 ALL VYLT TESTS PASSED — VERIFIED & CORRECT"
else
  echo "⚠️ TEST COMPLETED WITH $FAILED_STEPS FAILURE(S)"
fi
