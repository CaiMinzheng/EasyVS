# EasyVS
## 高自由度，高通量，基础成本，基于Autodock vina的批量分子筛选pipeline

## S1，受体（macromolecule）准备
S1-1 使用 Alphafold3 同源建模 或者在 PDB database 网站下载蛋白结构文件  
S1-2 alphafold3 预测的蛋白结构使用Pymol转换成PDB格式，PDB database网站下载的则使用Pymol打开删除水分子和配体  
S1-3 使用MGLTools处理macromolecule，加氢计算电荷然后转换成PDBQT格式  

## S2，配体（Ligand）准备
S2-1 在`PubChem，Enamine Real，ZINC，Life Chemicals`等网站下载目标小分子的3D SDF格式文件  

S2-2 使用`Split_SDF.py` 脚本分割SDF文件，预防后续计算RAM不足  
使用方法：`python Split_SDF.py 输入文件.sdf 输出前缀 分块大小`  

S2-3 使用`Process_SDF.py`厉遍分割后的小分子，进行RO5过滤，去除盐离子，加氢，2D转3D，3D结构优化(MMFF94)  
使用方法:  `python Process_SDF.py 输入文件.sdf 输出文件.sdf`    

S2-4 如果服务器RAM比较小，分割后的小分子文件较多，可以使用`submit_jobs.sh`脚本批量提交任务  
使用方法： `./submit_jobs.sh`
注意：脚本需要根据Computer Cluster的种类（LSF，PBS或者其他）进行修改。

S2-5 使用`meeko`给3D.sdf文件计算电荷，生成每 500 pdbqt/tar.gt  
`mk_prepare_ligand.py -i processed_chunk_1.sdf --multimol_outdir meeko_chunk1 --multimol_prefix meeko_chunk1 -z --multimol_targz_size 500`  

s2-6 如果网站中下载的小分子中有小分子复合体，使用`single_fragment_filter.py`保留分子量最大的小分子后再进行步骤S2-5
使用方法： `python single_fragment_filter.py 输入文件.sdf 输出文件.sdf`  

## S3，历遍-初级虚拟筛选（Virtual  screening）  

S3-1 使用Autodock vina 批量对接转换成pdbqt格式的小分子,这个脚本不直接运行，使用下个脚本调用

`#!/bin/bash`  
`# 从脚本：实际执行对接任务`  

`TAR_FILE=$1`  
`RECEPTOR=$2`  
`OUTPUT_DIR=$3`  
`GRID_SIZE=$4`  

`# 解析网格尺寸`  
`SIZE_X=$(echo $GRID_SIZE | cut -d' ' -f1)`  
`SIZE_Y=$(echo $GRID_SIZE | cut -d' ' -f2)`  
`SIZE_Z=$(echo $GRID_SIZE | cut -d' ' -f3)`  

`TEMP_DIR=$(mktemp -d)`  

`# 解压文件`  
`tar -xvzf "$TAR_FILE" -C "$TEMP_DIR"`  

`# 批量对接`  
`for PDBQT_FILE in "$TEMP_DIR"/*.pdbqt; do
    OUTPUT_FILE="${OUTPUT_DIR}/$(basename "$PDBQT_FILE")"
    vina --receptor "$RECEPTOR" --ligand "$PDBQT_FILE" --out "$OUTPUT_FILE" \
         --center_x -0.327 --center_y 0.926 --center_z 0.491 \
         --size_x $SIZE_X --size_y $SIZE_Y --size_z $SIZE_Z
done`  PS：这里的X,Y,Z坐标数据由MGLTools收集。  

`rm -rf "$TEMP_DIR"`   

S3-2 使用脚本批量提交任务

`vi Run_Vina.sh` 创建一个名为Run_Vina.sh的脚本进行高通量虚拟筛选
`#!/bin/bash`  
`# 主脚本：提交作业到LSF作业调度系统`  

`TAR_GZ_DIR="/public/home/xingyli/auto_dock_vina/meeko_chunk1"`定义输入文件夹，里面装的是S2-5的输出文件  
`OUTPUT_DIR="/public/home/xingyli/auto_dock_vina/meeko_chunk1_out"`定义输出文件夹  
`GRID_SIZE="22.5 30 22.5"`定义受体蛋白结合口袋的大小，需要用MGLTools设定  
`RECEPTOR="/public/home/xingyli/auto_dock_vina/fold_monilinia_fructicola_1_model_0.pdbqt"`配体位置  

`mkdir -p "$OUTPUT_DIR"`启动循环  

`for TAR_FILE in "$TAR_GZ_DIR"/*.tar.gz; do  
    bsub -n 1 -o "${OUTPUT_DIR}/job_$(basename "$TAR_FILE").out" \  
         -e "${OUTPUT_DIR}/job_$(basename "$TAR_FILE").err" \  
         "bash run_vina.sh '$TAR_FILE' '$RECEPTOR' '$OUTPUT_DIR' '$GRID_SIZE'"  
done`  

S3-3 调用服务器资源  
`#!/bin/bash`  
`#BSUB -J sdf_processing[1-10]    # 作业数组，处理10个任务`  
`#BSUB -n 1                       # 每个任务使用1个核心，这个服务器上每个核会分配5GB RAM，每个任务申请一个核应该够了`  
`#BSUB -R "span[ptile=20]"         # 每个节点最多使用20个核心`  
`#BSUB -o job_output.%J.%I.log    # 输出日志文件，%J是作业ID，%I是任务ID`  
`#BSUB -e job_error.%J.%I.log     # 错误日志文件`  
`#BSUB -q normal                  # 使用的队列`  
`./submit_Vina_jobs.sh`  
计算资源申请与计算时间：如果有50W小分子被分成1000个文件，每个文件500个小分子，一个核处理一个文件每个小分子平均耗费15秒，500个小分子大概耗费两小时。也就是说单核处理500小分子耗费2小时，50W小分子耗费83天。100核耗费0.83天约20小时。  

S3-4 使用`extract_best_compounds.py`提取结合能最低的结果  

使用方法：`python extract_best_compounds.py_name.py 输入文件夹 输出文件夹`
