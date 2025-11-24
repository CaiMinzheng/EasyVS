#!/bin/bash
#BSUB -J sdf_processing[1-10]    # 作业数组，处理10个任务
#BSUB -n 5                       # 每个任务使用5个核心
#BSUB -R "span[ptile=5]"         # 每个节点最多使用5个核心
#BSUB -o job_output.%J.%I.log    # 输出日志文件，%J是作业ID，%I是任务ID
#BSUB -e job_error.%J.%I.log     # 错误日志文件
#BSUB -q normal                  # 使用的队列

# 设置输入和输出目录
input_dir="/public/home/xingyli/ligand/Life_chemicals"
output_dir="/public/home/xingyli/ligand/Life_chemicals"

# 根据作业数组编号获取对应的文件
input_file="${input_dir}/output_chunk_chunk_${LSB_JOBINDEX}.sdf"
output_file="${output_dir}/processed_chunk_${LSB_JOBINDEX}.sdf"

# 运行 Python 脚本处理 SDF 文件
python process_sdf.py "$input_file" "$output_file"