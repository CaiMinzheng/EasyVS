#!/bin/bash
# 从脚本：实际执行对接任务

TAR_FILE=$1
RECEPTOR=$2
OUTPUT_DIR=$3
GRID_SIZE=$4

# 解析网格尺寸
SIZE_X=$(echo $GRID_SIZE | cut -d' ' -f1)
SIZE_Y=$(echo $GRID_SIZE | cut -d' ' -f2)
SIZE_Z=$(echo $GRID_SIZE | cut -d' ' -f3)

TEMP_DIR=$(mktemp -d)

# 解压文件
tar -xvzf "$TAR_FILE" -C "$TEMP_DIR"

# 批量对接
for PDBQT_FILE in "$TEMP_DIR"/*.pdbqt; do
    OUTPUT_FILE="${OUTPUT_DIR}/$(basename "$PDBQT_FILE")"
    vina --receptor "$RECEPTOR" --ligand "$PDBQT_FILE" --out "$OUTPUT_FILE" \
         --center_x -0.327 --center_y 0.926 --center_z 0.491 \
         --size_x $SIZE_X --size_y $SIZE_Y --size_z $SIZE_Z
done

rm -rf "$TEMP_DIR"