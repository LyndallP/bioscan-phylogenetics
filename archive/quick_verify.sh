#!/bin/bash
# Quick verification of metadata restoration

echo "============================================"
echo "METADATA RESTORATION VERIFICATION"
echo "============================================"

cd /mnt/project

echo ""
echo "1. Checking BIOSCAN specimens with missing BIN..."
awk -F'\t' 'NR==1 {for(i=1;i<=NF;i++) {if($i=="dataset") d=i; if($i=="bin") b=i}} 
NR>1 && $d=="BIOSCAN" && ($b=="" || $b=="0") {missing++} 
END {print "   BIOSCAN specimens missing BIN:", missing+0}' sciaridae_metadata_UPLOAD.tsv

echo ""
echo "2. Checking BIOSCAN specimens with complete BIN..."
awk -F'\t' 'NR==1 {for(i=1;i<=NF;i++) {if($i=="dataset") d=i; if($i=="bin") b=i}} 
NR>1 && $d=="BIOSCAN" && $b!="" && $b!="0" {complete++} 
END {print "   BIOSCAN specimens with BIN:", complete+0}' sciaridae_metadata_UPLOAD.tsv

echo ""
echo "3. Example restored specimen (FACE25516-24):"
grep "FACE25516-24" sciaridae_metadata_UPLOAD.tsv | awk -F'\t' '{print "   BIN:", $2; print "   Species:", $3; print "   Category:", $4; print "   Placement:", $5, "-", $6}'

echo ""
echo "4. File location and size:"
ls -lh sciaridae_metadata_UPLOAD.tsv

echo ""
echo "============================================"
echo "VERIFICATION COMPLETE"
echo "============================================"
