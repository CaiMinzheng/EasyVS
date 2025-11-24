1，python Split_SDF.py 输入文件.sdf 输出前缀 分块大小


2，python Process_SDF.py 输入文件.sdf 输出文件.sdf

3，./submit_jobs.sh

4，python single_fragment_filter.py 输入文件.sdf 输出文件.sdf

5，使用meeko给3D.sdf文件计算电荷，生成每 500 pdbqt/tar.gt
mk_prepare_ligand.py -i processed_chunk_1.sdf --multimol_outdir meeko_chunk1 --multimol_prefix meeko_chunk1 -z --multimol_targz_size 500

vi Run_Vina.sh

./submit_Vina_jobs.sh

python script_name.py 输入文件夹 输出文件夹



