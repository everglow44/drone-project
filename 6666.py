import streamlit as st
import subprocess
import sys
import os
from io import StringIO
import re
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from itertools import permutations
import io

# 设置页面配置
st.set_page_config(
    page_title="救灾无人机智能装箱系统",
    page_icon="📦",
    layout="wide"
)

# CSS样式
st.markdown("""
<style>
    .main-header {
        text-align: center;           
        color: #1e3a8a;              
        font-size: 2.5rem;           
        font-weight: bold;           
        margin-bottom: 1rem;        
    }

    .sub-header {
        text-align: center;
        color: #374151;              
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }

    .info-box {
        background-color: #e0f2fe;   
        padding: 1rem;               
        border-radius: 0.5rem;       
        margin-bottom: 1rem;
        border-left: 4px solid #0ea5e9; 
    }

    .result-box {
        background-color: #f0fdf4;   
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
        border-left: 4px solid #10b981; 
    }

    .error-box {
        background-color: #fef2f2;   
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
        border-left: 4px solid #ef4444; 
    }

    .typhoon-level {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: white;
        font-weight: bold;
        text-align: center;
    }
    .light-typhoon {
        background-color: #10b981; /* 绿色 - 轻度 */
    }
    .moderate-typhoon {
        background-color: #f59e0b; /* 橙色 - 中度 */
    }
    .severe-typhoon {
        background-color: #ef4444; /* 红色 - 重度 */
    }
</style>
""", unsafe_allow_html=True)

# 页面标题 - 使用自定义CSS样式
st.markdown("<h1 class='main-header'>📦 救灾无人机智能装箱系统</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>智能算法驱动下救灾无人机的最优摆放方案</p>", unsafe_allow_html=True)

# 说明信息 - 使用HTML格式创建带样式的盒子
st.markdown("""
<div class="info-box">
    <h4>💡 系统说明</h4>
    <p>本系统基于智能装箱算法，救灾无人机在标准集装箱中的最优摆放方案。</p>
    <ul>
        <li>支持两种无人机型号：DJI FlyCart 和 DJI Mavic 3E</li>
        <li>自动计算空间利用率和摆放数量</li>
        <li>提供3D可视化展示装箱结果</li>
        <li>支持旋转摆放以最大化空间利用</li>
        <li>本系统根据台风受灾等级（轻度、中度、重度）自动调整无人机装箱策略，优化救援资源配置</li>
        <li>无人机特殊货物标准（含锂电），空间利用率首先考虑安全</li>
    </ul>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📦 集装箱信息")
    st.write(f"**尺寸**: 6058 × 2591 × 2438 mm")
    st.write("**类型**: 标准集装箱")

with col2:
    st.subheader("🚁 无人机信息")
    st.write(f"**DJI FlyCart**: 1105 × 1265 × 975 mm")
    st.write(f"**DJI Mavic 3E**: 221 × 96.3 × 90.3 mm")

st.markdown("---")
st.subheader("📝 输入救灾无人机数量")

col1, col2 = st.columns(2)

with col1:
    large_drones = st.number_input(
        "DJI FlyCart 数量",
        min_value=0,
        max_value=1000,
        value=10,
        step=1,
        help="输入需要装箱的 DJI FlyCart 无人机数量"
    )

with col2:
    small_drones = st.number_input(
        "DJI Mavic 3E 数量",
        min_value=0,
        max_value=10000,
        value=100,
        step=1,
        help="输入需要装箱的 DJI Mavic 3E 无人机数量"
    )

with st.expander("⚙️ 高级选项"):
    st.write("预留高级功能选项（演示版本使用默认参数）")
    algorithm_choice = st.selectbox(
        "选择算法策略",
        ["底层优先填充策略", "体积优先策略", "混合策略", "遗传算法策略", "紧急情况过载策略（极端用）"],
        disabled=False,
        help="演示版本固定使用底层优先填充策略"
    )

    st.markdown("### 🌪️ 选择台风受灾等级")
    typhoon_level = st.selectbox(
        "选择台风受灾等级",
        ["轻度受灾", "中度受灾", "重度受灾"],
        help="根据受灾等级自动调整无人机配置策略"
    )

    if typhoon_level == "轻度受灾":
        st.markdown(
            "<div class='typhoon-level light-typhoon'>🟢 轻度受灾 - 无人机配置：8台DJIFlyCart + 68台Mavic3E</div>",
            unsafe_allow_html=True)
        default_large = 8
        default_small = 68
    elif typhoon_level == "中度受灾":
        st.markdown(
            "<div class='typhoon-level moderate-typhoon'>🟡 中度受灾 - 无人机配置：16台DJIFlyCart + 970台Mavic3E</div>",
            unsafe_allow_html=True)
        default_large = 16
        default_small = 970
    else:
        st.markdown(
            "<div class='typhoon-level severe-typhoon'>🔴 重度受灾 - 无人机配置：16台DJIFlyCart + 2138台Mavic3E</div>",
            unsafe_allow_html=True)
        default_large = 16
        default_small = 2138

    st.markdown("### 🌪️ 灾情评估选项")
    Disaster_severity_standard = st.selectbox(
        "初步选择灾情评估标准",
        ["受灾人口优先", "受灾面积优先", "预估经济损失优先", "综合优先"],
        disabled=False,
        help="演示版本固定使用综合优先考虑(中度灾害)"
    )

# 计算按钮
st.markdown("---")
if st.button("🚀 开始计算装箱方案", type="primary", use_container_width=True):
    with st.spinner("正在计算最优装箱方案..."):
        try:
            # 捕获输出
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()

            # 设置matplotlib后端
            plt.switch_backend('Agg')
            plt.rcParams['font.sans-serif'] = ['SimHei']
            plt.rcParams['axes.unicode_minus'] = False

            CONTAINER_DIMENSIONS = (6058, 2591, 2438)
            LARGE_BOX_DIMENSIONS = (1105, 1265, 975)
            SMALL_BOX_DIMENSIONS = (221, 96.3, 90.3)


            def get_all_rotations(dims):
                rotations = set()
                for p in permutations(dims):
                    sorted_p = tuple(sorted(p, reverse=True))
                    rotations.add(sorted_p)
                return list(rotations)


            LARGE_BOX_ROTATIONS = get_all_rotations(LARGE_BOX_DIMENSIONS)
            SMALL_BOX_ROTATIONS = get_all_rotations(SMALL_BOX_DIMENSIONS)


            def split_space(original_space_pos, original_space_dim, placed_box_pos, placed_box_dim):
                ox, oy, oz = original_space_pos
                ol, ow, oh = original_space_dim
                bx, by, bz = placed_box_pos
                bl, bw, bh = placed_box_dim

                new_spaces = []

                new_length = ol - (bx - ox + bl)
                if new_length > 1e-9:
                    new_pos = (bx + bl, oy, oz)
                    new_dim = (new_length, ow, oh)
                    new_spaces.append((new_pos, new_dim))

                new_width = ow - (by - oy + bw)
                if new_width > 1e-9:
                    new_pos = (ox, by + bw, oz)
                    new_dim = (bl, new_width, oh)
                    new_spaces.append((new_pos, new_dim))

                new_height = oh - (bz - oz + bh)
                if new_height > 1e-9:
                    new_pos = (ox, oy, bz + bh)
                    new_dim = (bl, bw, new_height)
                    new_spaces.append((new_pos, new_dim))

                return new_spaces


            def pack_boxes_optimized(num_large, num_small):
                placed_boxes = []
                available_spaces = [((0, 0, 0), CONTAINER_DIMENSIONS)]

                large_placed = 0
                small_placed = 0

                while available_spaces and (large_placed < num_large or small_placed < num_small):
                    available_spaces.sort(key=lambda s: (s[0][2], s[1][0] * s[1][1] * s[1][2]))
                    space_pos, space_dim = available_spaces.pop(0)

                    placed_a_large_box = False
                    if large_placed < num_large:
                        for rot_dim in LARGE_BOX_ROTATIONS:
                            if (rot_dim[0] <= space_dim[0] + 1e-9 and
                                    rot_dim[1] <= space_dim[1] + 1e-9 and
                                    rot_dim[2] <= space_dim[2] + 1e-9):
                                box_pos = space_pos
                                placed_boxes.append((box_pos, rot_dim, 'large'))
                                large_placed += 1
                                new_spaces = split_space(space_pos, space_dim, box_pos, rot_dim)
                                available_spaces.extend(new_spaces)
                                placed_a_large_box = True
                                break

                    if not placed_a_large_box and small_placed < num_small:
                        while small_placed < num_small:
                            placed_a_small_box = False
                            for rot_dim in SMALL_BOX_ROTATIONS:
                                if (rot_dim[0] <= space_dim[0] + 1e-9 and
                                        rot_dim[1] <= space_dim[1] + 1e-9 and
                                        rot_dim[2] <= space_dim[2] + 1e-9):
                                    box_pos = space_pos
                                    placed_boxes.append((box_pos, rot_dim, 'small'))
                                    small_placed += 1
                                    new_spaces = split_space(space_pos, space_dim, box_pos, rot_dim)
                                    if new_spaces:
                                        space_pos, space_dim = new_spaces[0]
                                        available_spaces.extend(new_spaces[1:])
                                    else:
                                        space_dim = (0, 0, 0)
                                    placed_a_small_box = True
                                    break
                            if not placed_a_small_box:
                                break

                return placed_boxes, large_placed, small_placed


            def plot_box(ax, position, dimensions, color, alpha=0.7):
                x, y, z = position
                l, w, h = dimensions

                vertices = np.array([
                    [x, y, z], [x + l, y, z], [x + l, y + w, z], [x, y + w, z],
                    [x, y, z + h], [x + l, y, z + h], [x + l, y + w, z + h], [x, y + w, z + h]
                ])

                edges = [
                    [0, 1], [1, 2], [2, 3], [3, 0],
                    [4, 5], [5, 6], [6, 7], [7, 4],
                    [0, 4], [1, 5], [2, 6], [3, 7]
                ]

                for edge in edges:
                    ax.plot3D(
                        [vertices[edge[0], 0], vertices[edge[1], 0]],
                        [vertices[edge[0], 1], vertices[edge[1], 1]],
                        [vertices[edge[0], 2], vertices[edge[1], 2]],
                        color=color, linewidth=2, alpha=alpha
                    )


            def visualize_packing(placed_boxes):
                print("正在创建可视化图像...")
                try:
                    plt.switch_backend('Agg')
                except:
                    pass

                fig = plt.figure(figsize=(15, 10))
                ax = fig.add_subplot(111, projection='3d')

                plot_box(ax, (0, 0, 0), CONTAINER_DIMENSIONS, 'green', 0.2)

                large_count = 0
                small_count = 0
                for (pos, dim, box_type) in placed_boxes:
                    color = 'blue' if box_type == 'large' else 'red'
                    plot_box(ax, pos, dim, color, 0.8)
                    if box_type == 'large':
                        large_count += 1
                    else:
                        small_count += 1

                ax.set_xlabel('长度 (mm)')
                ax.set_ylabel('宽度 (mm)')
                ax.set_zlabel('高度 (mm)')
                ax.set_title(
                    f'救灾无人机三维装箱布局\nDJI FlyCart: {large_count} 个, Mavic 3E: {small_count} 个\n台风受灾等级: {typhoon_level}')

                from matplotlib.lines import Line2D
                legend_elements = [
                    Line2D([0], [0], color='blue', lw=4, label='DJI FlyCart'),
                    Line2D([0], [0], color='red', lw=4, label='Mavic 3E'),
                    Line2D([0], [0], color='green', lw=4, label='集装箱')
                ]
                ax.legend(handles=legend_elements)

                ax.view_init(elev=20, azim=45)
                plt.tight_layout()

                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0)
                return buf


            # 执行计算
            print("=" * 60)
            print(f"救灾无人机装箱模拟程序 ({typhoon_level})")
            print("=" * 60)
            print(f"集装箱尺寸: {CONTAINER_DIMENSIONS[0]}×{CONTAINER_DIMENSIONS[1]}×{CONTAINER_DIMENSIONS[2]} mm")
            print(f"DJI FlyCart 尺寸: {LARGE_BOX_DIMENSIONS} mm (支持旋转)")
            print(f"Mavic 3E 尺寸: {SMALL_BOX_DIMENSIONS} mm (支持旋转)")
            print(f"台风受灾等级: {typhoon_level}")
            print("=" * 60)

            print(f"计划放置 DJI FlyCart: {large_drones} 个")
            print(f"计划放置 Mavic 3E: {small_drones} 个")

            print(f"算法策略: {algorithm_choice}")
            print(f"灾情评估标准: {Disaster_severity_standard}")

            print("\n正在计算装箱方案...")
            placed_boxes, large_placed, small_placed = pack_boxes_optimized(large_drones, small_drones)

            print("\n" + "=" * 60)
            print("装箱结果")
            print("=" * 60)
            print(f"计划放置 DJI FlyCart: {large_drones} 个")
            print(f"实际放置 DJI FlyCart: {large_placed} 个")
            print(f"计划放置 Mavic 3E: {small_drones} 个")
            print(f"实际放置 Mavic 3E: {small_placed} 个")
            print(f"DJI FlyCart 放置率: {large_placed / large_drones * 100:.1f}%" if large_drones > 0 else "N/A")
            print(f"Mavic 3E 放置率: {small_placed / small_drones * 100:.1f}%" if small_drones > 0 else "N/A")

            total_volume = CONTAINER_DIMENSIONS[0] * CONTAINER_DIMENSIONS[1] * CONTAINER_DIMENSIONS[2]
            used_volume = (large_placed * np.prod(LARGE_BOX_DIMENSIONS) +
                           small_placed * np.prod(SMALL_BOX_DIMENSIONS))
            utilization = used_volume / total_volume * 100
            print(f"空间利用率: {utilization:.1f}%")
            print("=" * 60)

            sys.stdout = old_stdout
            output = captured_output.getvalue()

            # 解析结果
            lines = output.split('\n')
            results = {}
            for line in lines:
                if '实际放置 DJI FlyCart' in line:
                    results['large_placed'] = int(re.search(r'(\d+)', line.split(':')[-1].strip()).group(1))
                elif '实际放置 Mavic 3E' in line:
                    results['small_placed'] = int(re.search(r'(\d+)', line.split(':')[-1].strip()).group(1))
                elif '空间利用率' in line:
                    results['utilization'] = float(re.search(r'([\d.]+)', line.split(':')[-1].strip()).group(1))

            # 显示结果
            st.success(f"✅ {typhoon_level}装箱计算完成！")

            # 使用指标卡片显示结果
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    label="DJI FlyCart 放置数量",
                    value=f"{results.get('large_placed', 0)} / {large_drones}",
                    delta=f"{results.get('large_placed', 0) / large_drones * 100:.1f}%" if large_drones > 0 else "N/A"
                )

            with col2:
                st.metric(
                    label="Mavic 3E 放置数量",
                    value=f"{results.get('small_placed', 0)} / {small_drones}",
                    delta=f"{results.get('small_placed', 0) / small_drones * 100:.1f}%" if small_drones > 0 else "N/A"
                )

            with col3:
                st.metric(
                    label="空间利用率",
                    value=f"{results.get('utilization', 0):.1f}%",
                    delta="理想装箱"
                )

            # 生成可视化
            if placed_boxes:
                st.subheader("📊 装箱结果可视化")
                image_buf = visualize_packing(placed_boxes)
                st.image(image_buf, caption=f"救灾无人机三维装箱布局图 - {typhoon_level}", use_column_width=True)

                st.download_button(
                    label="💾 下载装箱布局图",
                    data=image_buf.getvalue(),
                    file_name=f"rescue_drone_packing_{typhoon_level}.png",
                    mime="image/png"
                )

            with st.expander("🔍 查看详细计算过程"):
                st.text(output)

        except Exception as e:
            st.error(f"❌ 计算过程中发生错误: {str(e)}")
            import traceback

            st.code(traceback.format_exc())

# 页脚
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 1rem;'>
    <p><strong>救灾无人机智能装箱系统</strong></p>
    <p>基于三维装箱算法的智能摆放方案计算工具</p>
    <p>支持多种无人机型号的混合装箱优化</p>
</div>
""", unsafe_allow_html=True)
