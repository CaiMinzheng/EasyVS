from rdkit import Chem
import os
import sys

def split_sdf(input_file, output_prefix, chunk_size=300000):
    """将SDF文件拆分为多个较小的SDF文件，优化内存使用"""
    # 创建SDMolSupplier读取输入SDF文件
    supplier = Chem.SDMolSupplier(input_file)
    if not supplier:
        raise ValueError(f"无法读取文件: {input_file}")

    chunk_num = 1
    mols = []
    count = 0

    # 创建一个写入器用于写入每个拆分的小文件
    def write_chunk(mols, chunk_num):
        output_file = f"{output_prefix}_chunk_{chunk_num}.sdf"
        with Chem.SDWriter(output_file) as writer:
            for mol in mols:
                writer.write(mol)
        print(f"写入文件: {output_file} 完成.")

    # 遍历分子并按指定大小分批处理
    for i, mol in enumerate(supplier):
        if mol is None:
            continue

        mols.append(mol) # 将当前分子添加到列表

        # 每达到chunk_size时，写入当前批次并清空列表
        if len(mols) >= chunk_size:
            write_chunk(mols, chunk_num)
            mols.clear() # 清空当前批次的分子列表
            chunk_num += 1 # 递增文件编号

        count += 1

    # 如果最后一批剩余的分子没有达到chunk_size，仍然需要写入
    if mols:
        write_chunk(mols, chunk_num)

    print(f"总共处理了{count}个分子。")

def main():
    """命令行参数处理主函数"""
    if len(sys.argv) < 3:
        print("使用方法: python script.py 输入文件.sdf 输出文件名 [分块大小]")
        print("示例: python split_sdf.py large_file.sdf output 50000")
        print("参数说明:")
        print("  输入文件.sdf - 要拆分的SDF文件路径")
        print("  输出文件名 - 输出文件的前缀名")
        print("  分块大小 - 可选，每个文件包含的分子数（默认: 300000）")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_prefix = sys.argv[2]
    
    # 设置分块大小（如果提供了第三个参数）
    chunk_size = 300000  # 默认值
    if len(sys.argv) >= 4:
        try:
            chunk_size = int(sys.argv[3])
        except ValueError:
            print("错误: 分块大小必须是整数")
            sys.exit(1)
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 输入文件 '{input_file}' 不存在")
        sys.exit(1)
    
    print(f"开始处理文件: {input_file}")
    print(f"输出前缀: {output_prefix}")
    print(f"分块大小: {chunk_size} 个分子/文件")
    
    try:
        split_sdf(input_file, output_prefix, chunk_size)
        print("文件拆分完成！")
    except Exception as e:
        print(f"处理过程中出现错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()