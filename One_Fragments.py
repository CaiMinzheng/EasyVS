from rdkit import Chem
from rdkit.Chem import SDWriter
import sys
import os

def filter_single_fragment_molecules(input_sdf, output_sdf):
    """
    过滤SDF文件，只保留单片段分子
    """
    # 检查输入文件是否存在
    if not os.path.exists(input_sdf):
        print(f"错误: 输入文件不存在: {input_sdf}")
        return
    
    supplier = Chem.SDMolSupplier(input_sdf, removeHs=False)  # 关键：保留显性氢
    writer = SDWriter(output_sdf)
    
    total_count = 0
    kept_count = 0
    skipped_count = 0
    
    for mol in supplier:
        total_count += 1
        
        if mol is None:
            skipped_count += 1
            continue
        
        # 检查是否为单片段分子
        if len(Chem.GetMolFrags(mol)) == 1:
            writer.write(mol)
            kept_count += 1
        else:
            skipped_count += 1
    
    writer.close()
    
    print(f"过滤完成!")
    print(f"总分子数: {total_count}")
    print(f"保留的单片段分子: {kept_count}")
    print(f"跳过的多片段分子: {skipped_count}")
    print(f"保留比例: {kept_count/total_count*100:.1f}%")
    print(f"结果保存至: {output_sdf}")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        # 使用命令行参数
        input_sdf = sys.argv[1]
        output_sdf = sys.argv[2]
    else:
        # 使用默认路径
        input_sdf = "LC_Stock_HTS_Compounds_process.sdf"
        output_sdf = "LC_Stock_HTS_Compounds_process_one.sdf"
        print("使用默认文件路径，如需指定请使用: python script.py <输入文件> <输出文件>")
    
    filter_single_fragment_molecules(input_sdf, output_sdf)