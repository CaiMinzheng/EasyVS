import os
import shutil
import sys

def main():
    # 检查命令行参数
    if len(sys.argv) != 3:
        print("使用方法: python script_name.py 输入文件夹 输出文件夹")
        print("示例: python script_name.py /path/to/input /path/to/output")
        sys.exit(1)
    
    # 从命令行参数获取输入和输出文件夹
    OUTPUT_DIR = sys.argv[1]
    BEST_OUTPUT_DIR = sys.argv[2]
    
    # 检查输入文件夹是否存在
    if not os.path.exists(OUTPUT_DIR):
        print(f"错误: 输入文件夹 '{OUTPUT_DIR}' 不存在")
        sys.exit(1)
    
    # 确保目标文件夹存在
    if not os.path.exists(BEST_OUTPUT_DIR):
        os.makedirs(BEST_OUTPUT_DIR)
        print(f"已创建输出文件夹: {BEST_OUTPUT_DIR}")

    # 提取所有 .pdbqt 文件
    output_files = [os.path.join(OUTPUT_DIR, f) for f in os.listdir(OUTPUT_DIR) if f.endswith('.pdbqt')]
    
    if len(output_files) == 0:
        print(f"在文件夹 '{OUTPUT_DIR}' 中没有找到任何 .pdbqt 文件")
        sys.exit(1)
    
    print(f"找到 {len(output_files)} 个 .pdbqt 文件")

    # 提取每个文件的结合能
    binding_energies = []

    for file in output_files:
        with open(file, 'r') as f:
            for line in f:
                if "REMARK VINA RESULT" in line:  # 确保包含结合能信息的行
                    print(f"在文件 {os.path.basename(file)} 中找到结合能信息: {line.strip()}")  # 打印找到的结合能行
                    try:
                        # 提取结合能（该行中的第一个数字）
                        energy = float(line.split()[3])  # 假设结合能在该行的第4个元素
                        binding_energies.append((energy, file))
                    except (IndexError, ValueError) as e:
                        print(f"无法从文件 {file} 提取结合能，错误: {e}")
                    break

    # 检查是否提取到结合能
    if len(binding_energies) == 0:
        print("没有找到任何有效的结合能信息。")
        sys.exit(1)
    else:
        print(f"成功提取了 {len(binding_energies)} 个文件的结合能信息。")

    # 按结合能从小到大排序（结合能越小越好）
    binding_energies.sort(key=lambda x: x[0])

    # 提取最小结合能的前500个小分子
    best_500 = binding_energies[:500]

    # 检查是否成功提取前500个
    if len(best_500) == 0:
        print("没有找到最小结合能的500个小分子。")
        sys.exit(1)
    else:
        print(f"共找到最小结合能的 {len(best_500)} 个小分子，准备复制到 {BEST_OUTPUT_DIR}。")

    # 复制最好的500个小分子到目标文件夹
    copied_count = 0
    for energy, file in best_500:
        try:
            filename = os.path.basename(file)
            dest_path = os.path.join(BEST_OUTPUT_DIR, filename)
            shutil.copy2(file, dest_path)
            copied_count += 1
        except Exception as e:
            print(f"复制文件 {file} 时出错: {e}")

    # 删除剩余的所有小分子文件（不在前500名中的）
    deleted_count = 0
    for energy, file in binding_energies[500:]:
        try:
            os.remove(file)
            deleted_count += 1
        except Exception as e:
            print(f"删除文件 {file} 时出错: {e}")

    print(f"已将结合能最小的 {copied_count} 个小分子复制到 {BEST_OUTPUT_DIR}")
    print(f"已删除 {deleted_count} 个其他小分子文件")

if __name__ == "__main__":
    main()