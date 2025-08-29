#!/usr/bin/env python3
"""
生成 ListenTube 应用图标的简单脚本
需要安装 Pillow 库: pip install Pillow
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
except ImportError:
    print("请先安装 Pillow 库: pip install Pillow")
    exit(1)

def create_icon(size, output_path):
    """创建指定尺寸的图标"""
    # 创建画布
    img = Image.new('RGBA', (size, size), (76, 175, 80, 255))  # 绿色背景
    draw = ImageDraw.Draw(img)
    
    # 计算音符图标的位置和大小
    icon_size = int(size * 0.6)
    x = (size - icon_size) // 2
    y = (size - icon_size) // 2
    
    # 绘制音符图标（简化版）
    # 音符头部
    head_radius = int(icon_size * 0.15)
    head_x = x + int(icon_size * 0.3)
    head_y = y + int(icon_size * 0.2)
    draw.ellipse([head_x - head_radius, head_y - head_radius, 
                   head_x + head_radius, head_y + head_radius], 
                  fill='white')
    
    # 音符杆
    stem_width = int(icon_size * 0.08)
    stem_x = head_x + head_radius
    stem_y = head_y
    stem_height = int(icon_size * 0.5)
    draw.rectangle([stem_x, stem_y, stem_x + stem_width, stem_y + stem_height], 
                   fill='white')
    
    # 音符尾部
    tail_start_x = stem_x + stem_width
    tail_start_y = stem_y + stem_height
    tail_width = int(icon_size * 0.3)
    tail_height = int(icon_size * 0.15)
    draw.ellipse([tail_start_x, tail_start_y - tail_height//2,
                   tail_start_x + tail_width, tail_start_y + tail_height//2], 
                  fill='white')
    
    # 保存图标
    img.save(output_path, 'PNG')
    print(f"已创建图标: {output_path}")

def main():
    """主函数"""
    # 确保 static 目录存在
    static_dir = "static"
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    # 创建不同尺寸的图标
    icons = [
        (192, "icon-192.png"),
        (512, "icon-512.png")
    ]
    
    for size, filename in icons:
        output_path = os.path.join(static_dir, filename)
        create_icon(size, output_path)
    
    print("\n图标创建完成！")
    print("现在你可以重新启动应用，PWA 功能就可以正常使用了。")

if __name__ == "__main__":
    main() 