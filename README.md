# EasyVS
## 基于Autodock vina的批量分子筛选pipeline

## S1，受体（macromolecule）准备
S1-1 使用 Alphafold3 同源建模 或者在 PDB database 网站下载蛋白结构文件  
S1-2 alphafold3 预测的蛋白结构使用Pymol转换成PDB格式，PDB database网站下载的则使用Pymol打开删除水分子和配体  
S1-3 使用MGLTools处理macromolecule，加氢计算电荷然后转换成PDBQT格式  

## S2，配体（Ligand）准备
S2-1 在PubChem，Enamine Real，ZINC，Life Chemicals等网站下载目标小分子的3D SDF格式文件  

S2-2 使用Split_SDF.py 脚本分割SDF文件，预防后续计算RAM不足  
使用方法：`python Split_SDF.py 输入文件.sdf 输出前缀 分块大小`  

S2-3 使用Process_SDF.py厉遍分割后的小分子，进行RO5过滤，去除盐离子，加氢，2D转3D，3D结构优化(MMFF94)  
使用方法:  `python Process_SDF.py 输入文件.sdf 输出文件.sdf`    

S2-4 如果服务器RAM比较小，分割后的小分子文件较多，可以使用submit_jobs.sh脚本批量提交任务  
使用方法： `./submit_jobs.sh`
注意：脚本需要根据Computer Cluster的种类（LSF，PBS或者其他）进行修改。

S2-5 使用meeko给3D.sdf文件计算电荷，生成每 500 pdbqt/tar.gt  
`mk_prepare_ligand.py -i processed_chunk_1.sdf --multimol_outdir meeko_chunk1 --multimol_prefix meeko_chunk1 -z --multimol_targz_size 500`  

s2-6 如果网站中下载的小分子中有小分子复合体，使用single_fragment_filter.py保留分子量最大的小分子后再进行步骤S2-5
使用方法： `python single_fragment_filter.py 输入文件.sdf 输出文件.sdf`  

##S3，历遍-初级虚拟筛选（Virtual  screening）  
`vi Run_Vina.sh` 创建一个名为Run_Vina.sh的脚本进行高通量虚拟筛选
`#!/bin/bash`
`# 主脚本：提交作业到LSF作业调度系统`

`TAR_GZ_DIR="/public/home/xingyli/auto_dock_vina/meeko_chunk1"`
`OUTPUT_DIR="/public/home/xingyli/auto_dock_vina/meeko_chunk1_out"`
`GRID_SIZE="22.5 30 22.5"`
`RECEPTOR="/public/home/xingyli/auto_dock_vina/fold_monilinia_fructicola_1_model_0.pdbqt"`

`mkdir -p "$OUTPUT_DIR"`

`for TAR_FILE in "$TAR_GZ_DIR"/*.tar.gz; do
    bsub -n 1 -o "${OUTPUT_DIR}/job_$(basename "$TAR_FILE").out" \
         -e "${OUTPUT_DIR}/job_$(basename "$TAR_FILE").err" \
         "bash run_vina.sh '$TAR_FILE' '$RECEPTOR' '$OUTPUT_DIR' '$GRID_SIZE'"
done`

