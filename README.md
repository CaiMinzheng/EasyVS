# EasyVS
## A highly flexible, high-throughput, and cost-effective batch molecular screening pipeline based on Autodock Vina.

## Receptor (Macromolecule) Preparation​
S1-1​ Perform homology modeling using AlphaFold 3 or download the protein structure file from the PDB database.

S1-2​ For structures predicted by AlphaFold 3, convert the model to PDB format using PyMOL. For structures downloaded from the PDB database, open them in PyMOL and remove water molecules and ligands.

S1-3​ Process the macromolecule with MGLTools: add hydrogen atoms, calculate charges, and convert it to PDBQT format.

## Ligand Preparation​
S2-1​ Download the 3D SDF files of the target small molecules from databases/websites such as `PubChem, Enamine REAL, ZINC, and Life Chemicals`.

S2-2​ Use the `Split_SDF.pyscript` to split the SDF file, preventing insufficient RAM in subsequent calculations.
Usage: `python Split_SDF.py input_file.sdf output_prefix chunk_size`

S2-3​ Use `Process_SDF.py` to process the split small molecules sequentially, performing RO5 filtering, removing salt ions, adding hydrogens, converting 2D to 3D, and optimizing the 3D structure (MMFF94).
Usage: `python Process_SDF.py input_file.sdf output_file.sdf`

S2-4​ If the server has limited RAM and there are many split small molecule files, use the `submit_jobs.sh` script to submit jobs in batch.
Usage: `./submit_jobs.sh`
Note: The script needs to be modified according to the type of Computer Cluster (LSF, PBS, or others).

S2-5​ Use `meeko` to compute charges for the 3D .sdf file and generate PDBQT files in tar.gz archives of 500 molecules each.
`mk_prepare_ligand.py -i processed_chunk_1.sdf --multimol_outdir meeko_chunk1 --multimol_prefix meeko_chunk1 -z --multimol_targz_size 500`

S2-6​ If the small molecules downloaded from the websites contain molecular complexes, use `single_fragment_filter.py` to retain the small molecule with the largest molecular weight before proceeding to step S2-5.
Usage: `python single_fragment_filter.py input_file.sdf output_file.sdf`


## S3. Batch Primary Virtual Screening

S3-1 Use Autodock Vina to perform batch docking of small molecules converted into PDBQT format. This script is not run directly; it is called by the next script.
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

S3-2 Use the script to submit jobs in batch.

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

S3-3 Call on server resources.
`#!/bin/bash`  
`#BSUB -J sdf_processing[1-10]    # 作业数组，处理10个任务`  
`#BSUB -n 1                       # 每个任务使用1个核心，这个服务器上每个核会分配5GB RAM，每个任务申请一个核应该够了`  
`#BSUB -R "span[ptile=20]"         # 每个节点最多使用20个核心`  
`#BSUB -o job_output.%J.%I.log    # 输出日志文件，%J是作业ID，%I是任务ID`  
`#BSUB -e job_error.%J.%I.log     # 错误日志文件`  
`#BSUB -q normal                  # 使用的队列`  
`./submit_Vina_jobs.sh`  
Computational Resource Request and Time Estimation:
If 500,000 small molecules are split into 1,000 files, each containing 500 molecules, and a single core processes one file with an average time of 15 seconds per small molecule, processing 500 molecules would take approximately 2 hours. This means a single core would require 2 hours for 500 molecules, and 83 days for the entire set of 500,000 molecules. Using 100 cores would reduce the total time to 0.83 days, or about 20 hours.

S3-4 Use `extract_best_compounds.py` to extract the results with the lowest binding energy.

Usage：`python extract_best_compounds.py_name.py 输入文件夹 输出文件夹`
