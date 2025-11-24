from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import SaltRemover
from rdkit.Chem import Descriptors
import sys
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 函数：RO5过滤
def filter_ro5(mol):
    """根据RO5原则过滤分子：分子量<500，LogP<5，氢键供体≤5，氢键受体≤10"""
    try:
        if mol is None:
            return False
        
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)

        if mw < 500 and logp < 5 and hbd <= 5 and hba <= 10:
            return True
        return False
    except Exception as e:
        logger.warning(f"RO5过滤过程中发生错误: {e}")
        return False

# 函数：去除盐离子
def remove_salts(mol):
    """去除分子中的盐离子"""
    try:
        salt_remover = SaltRemover.SaltRemover()
        return salt_remover.StripMol(mol)
    except Exception as e:
        logger.warning(f"去除盐离子过程中发生错误: {e}")
        return None

# 函数：加氢
def add_hydrogens(mol):
    """为分子加氢"""
    try:
        return Chem.AddHs(mol)
    except Exception as e:
        logger.warning(f"加氢过程中发生错误: {e}")
        return None

# 函数：2D 转 3D
def convert_2d_to_3d(mol):
    """将 2D 分子结构转换为 3D 构象"""
    try:
        # 尝试嵌入 3D 构象
        result = AllChem.EmbedMolecule(mol, randomSeed=42)
        if result == -1:
            logger.warning("3D构象生成失败")
            return None
        return mol
    except Exception as e:
        logger.warning(f"2D转3D过程中发生错误: {e}")
        return None

# 函数：3D结构优化（使用MMFF94力场）
def optimize_3d(mol):
    """使用 MMFF94 力场对 3D 分子进行优化"""
    try:
        # 使用MMFF94力场优化
        result = AllChem.MMFFOptimizeMolecule(mol, maxIters=500)
        if result == -1:
            logger.warning("MMFF94优化失败")
            return None
        return mol
    except Exception as e:
        logger.warning(f"3D优化过程中发生错误: {e}")
        return None

def process_sdf(input_file, output_file):
    """读取SDF文件并进行处理，完成RO5筛选、去盐、加氢、2D转3D、3D优化"""
    
    processed_count = 0
    error_count = 0
    total_count = 0
    
    try:
        # 读取输入的SDF文件
        supplier = Chem.SDMolSupplier(input_file)
        writer = Chem.SDWriter(output_file)
        
        logger.info(f"开始处理文件: {input_file}")

        # 处理每个分子
        for i, mol in enumerate(supplier):
            total_count += 1
            
            try:
                if mol is None:
                    logger.warning(f"分子 {i+1}: 无法读取分子，跳过")
                    error_count += 1
                    continue
                
                # 检查分子是否有原子
                if mol.GetNumAtoms() == 0:
                    logger.warning(f"分子 {i+1}: 分子没有原子，跳过")
                    error_count += 1
                    continue

                logger.info(f"处理分子 {i+1}: {Chem.MolToSmiles(mol) if mol else 'Unknown'}")

                # 1. RO5过滤
                if not filter_ro5(mol):
                    logger.info(f"分子 {i+1}: 未通过RO5过滤，跳过")
                    continue

                # 2. 去除盐离子
                mol = remove_salts(mol)
                if mol is None or mol.GetNumAtoms() == 0:
                    logger.warning(f"分子 {i+1}: 去盐后分子无效，跳过")
                    error_count += 1
                    continue

                # 3. 加氢
                mol = add_hydrogens(mol)
                if mol is None or mol.GetNumAtoms() == 0:
                    logger.warning(f"分子 {i+1}: 加氢后分子无效，跳过")
                    error_count += 1
                    continue

                # 4. 2D转3D
                mol = convert_2d_to_3d(mol)
                if mol is None or mol.GetNumAtoms() == 0:
                    logger.warning(f"分子 {i+1}: 3D转换失败，跳过")
                    error_count += 1
                    continue

                # 5. 3D结构优化（使用MMFF94力场）
                mol = optimize_3d(mol)
                if mol is None or mol.GetNumAtoms() == 0:
                    logger.warning(f"分子 {i+1}: 3D优化失败，跳过")
                    error_count += 1
                    continue

                # 写入处理后的分子
                writer.write(mol)
                processed_count += 1
                logger.info(f"分子 {i+1}: 处理完成")

            except Exception as e:
                error_count += 1
                logger.error(f"处理分子 {i+1} 时发生错误: {e}")
                continue
        
        writer.close()
        
    except Exception as e:
        logger.error(f"处理文件时发生严重错误: {e}")
    
    finally:
        # 输出统计信息
        logger.info(f"处理完成! 总共处理: {total_count} 个分子, 成功: {processed_count} 个, 错误/跳过: {error_count} 个")

# 从命令行获取文件路径
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python process_sdf.py <输入文件> <输出文件>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    process_sdf(input_file, output_file)