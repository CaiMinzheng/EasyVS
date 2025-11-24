#!/bin/bash
# 主脚本：提交作业到LSF作业调度系统

TAR_GZ_DIR="/public/home/xingyli/auto_dock_vina/meeko_chunk1"
OUTPUT_DIR="/public/home/xingyli/auto_dock_vina/meeko_chunk1_out"
GRID_SIZE="22.5 30 22.5"
RECEPTOR="/public/home/xingyli/auto_dock_vina/fold_monilinia_fructicola_1_model_0.pdbqt"

mkdir -p "$OUTPUT_DIR"

for TAR_FILE in "$TAR_GZ_DIR"/*.tar.gz; do
    bsub -n 1 -o "${OUTPUT_DIR}/job_$(basename "$TAR_FILE").out" \
         -e "${OUTPUT_DIR}/job_$(basename "$TAR_FILE").err" \
         "bash run_vina.sh '$TAR_FILE' '$RECEPTOR' '$OUTPUT_DIR' '$GRID_SIZE'"
done