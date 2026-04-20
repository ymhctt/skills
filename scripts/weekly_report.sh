#!/bin/bash
exec 2>&1
FROM_DATE=$(date -d "8 days ago" +%Y-%m-%d)
TO_DATE=$(date -d "1 day ago" +%Y-%m-%d)
mes -o json statistics list --from "$FROM_DATE" --to "$TO_DATE" --team-id 23 --page-size 200 > /tmp/mes_report_$(date +%Y%m%d).json
