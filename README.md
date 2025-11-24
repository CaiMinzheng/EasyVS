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









S3，历遍-初级虚拟筛选（Virtual  screening）
