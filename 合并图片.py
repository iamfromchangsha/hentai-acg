import os
from PIL import Image

def concatenate_images_vertically(subfolder_path, output_path):
    """
    将指定子文件夹内所有的图片文件垂直拼接成一张长图。

    :param subfolder_path: 包含图片文件的子文件夹路径
    :param output_path: 输出图片的路径
    """
    # 支持的图片扩展名
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')

    # 列出子文件夹内所有的文件，并筛选出图片文件
    image_paths = [os.path.join(subfolder_path, f) for f in os.listdir(subfolder_path) if f.lower().endswith(image_extensions)]

    # 如果没有找到图片文件，则退出
    if not image_paths:
        print(f"在 {subfolder_path} 中没有找到任何图片文件。")
        return

    # 打开所有的图片
    images = [Image.open(path) for path in image_paths]

    # 获取每张图片的宽度和高度
    widths, heights = zip(*(i.size for i in images))

    # 计算输出图片的高度
    total_height = sum(heights)
    max_width = max(widths)

    # 创建一个新的空白图像，尺寸为最大宽度和总高度
    new_image = Image.new('RGB', (max_width, total_height))

    # 将图片粘贴到新图像中
    y_offset = 0
    for im in images:
        new_image.paste(im, (0, y_offset))
        y_offset += im.size[1]  # 更新偏移量

    # 保存结果
    try:
        new_image.save(output_path, quality=95)  # 保存为JPEG格式，quality参数控制压缩质量
        print(f"拼接完成，已保存至 {output_path}")
    except Exception as e:
        print(f"保存图片时发生错误: {e}")

def process_folder(main_folder_path, output_folder_path):
    """
    处理主文件夹下的每一个子文件夹，将子文件夹中的图片垂直拼接并保存。

    :param main_folder_path: 主文件夹路径
    :param output_folder_path: 输出图片存放的文件夹路径
    """
    # 确保输出文件夹存在
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    # 遍历主文件夹中的每一个子文件夹
    for subfolder_name in os.listdir(main_folder_path):
        subfolder_path = os.path.join(main_folder_path, subfolder_name)
        
        # 检查是否为文件夹
        if os.path.isdir(subfolder_path):
            # 为每个子文件夹创建输出文件路径
            output_path = os.path.join(output_folder_path, f"{subfolder_name}.jpg")
            # 调用函数拼接图片
            concatenate_images_vertically(subfolder_path, output_path)

# 使用示例
main_folder_path = 'H:\jm\[牛肝菌汉化] [flanvia] 钓れたて♥ウオむすめ (コミックゼロス #91) [中国翻译] [DL版]'  # 替换为您的主文件夹路径
output_folder_path = 'E:\桌面\BilibiliDown.v6.32.release'  # 替换为您想要保存拼接后图片的文件夹路径
process_folder(main_folder_path, output_folder_path)