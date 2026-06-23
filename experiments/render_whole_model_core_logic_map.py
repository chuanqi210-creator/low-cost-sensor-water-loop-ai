from __future__ import annotations

from math import atan2, cos, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = PROJECT_ROOT / "deliverables" / "model_core_optimization"
OUT_PRIMARY = OUT_DIR / "whole_model_logic_map_v2.png"
OUT_LEGACY = OUT_DIR / "whole_model_logic_map.png"
OUT_CORE = OUT_DIR / "whole_model_core_logic_map.png"


FONT_CANDIDATES = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
]


def font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


TITLE = font(56)
SUBTITLE = font(27)
SECTION = font(30)
CARD_TITLE = font(25)
BODY = font(19)
SMALL = font(16)
TINY = font(14)
TAG = font(18)
NUMBER = font(22)


COLORS = {
    "bg": "#f4f7fb",
    "ink": "#162433",
    "muted": "#52667a",
    "line": "#4f6477",
    "navy": "#122033",
    "blue": "#2f83ad",
    "blue_fill": "#e9f6fc",
    "green": "#25845e",
    "green_fill": "#eaf7ef",
    "purple": "#7257b7",
    "purple_fill": "#f2edfc",
    "orange": "#b5742c",
    "orange_fill": "#fff3e4",
    "red": "#b64e4e",
    "red_fill": "#fff0f0",
    "yellow": "#b79a22",
    "yellow_fill": "#fff9df",
    "grey": "#6f8396",
    "grey_fill": "#eef3f7",
    "white": "#ffffff",
}


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    buf = ""
    for ch in text:
        if ch == "\n":
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(ch)
            continue
        if ch.isascii() and (ch.isalnum() or ch in "-_:/().×"):
            buf += ch
        else:
            if buf:
                tokens.append(buf)
                buf = ""
            tokens.append(ch)
    if buf:
        tokens.append(buf)
    return tokens


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for token in tokenize(text):
        if token == "\n":
            lines.append(current)
            current = ""
            continue
        trial = current + token
        if not current or text_size(draw, trial, fnt)[0] <= max_width:
            current = trial
        else:
            lines.append(current)
            current = token
    if current:
        lines.append(current)
    return lines


def rounded(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    *,
    fill: str,
    outline: str,
    width: int = 2,
    radius: int = 24,
) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def panel(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], title: str, color: str) -> None:
    x1, y1, x2, y2 = xy
    rounded(draw, xy, fill=COLORS["white"], outline=color, width=3, radius=26)
    draw.rounded_rectangle((x1, y1, x2, y1 + 68), radius=26, fill=color)
    draw.rectangle((x1, y1 + 34, x2, y1 + 68), fill=color)
    draw.text((x1 + 30, y1 + 19), title, font=SECTION, fill="#ffffff")


def card(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    title: str,
    lines: list[str],
    *,
    fill: str,
    outline: str,
    tag: str | None = None,
    title_color: str = COLORS["ink"],
) -> None:
    x1, y1, x2, y2 = xy
    rounded(draw, xy, fill=fill, outline=outline, width=2, radius=18)
    if tag:
        tw, _ = text_size(draw, tag, TAG)
        draw.rounded_rectangle((x2 - tw - 30, y1 + 15, x2 - 13, y1 + 44), radius=14, fill=outline)
        draw.text((x2 - tw - 22, y1 + 20), tag, font=TAG, fill="#ffffff")
    draw.text((x1 + 22, y1 + 19), title, font=CARD_TITLE, fill=title_color)
    y = y1 + 61
    for line in lines:
        fnt = SMALL if line.startswith("·") else BODY
        color = COLORS["muted"] if line.startswith("·") else COLORS["ink"]
        for part in wrap(draw, line, fnt, x2 - x1 - 44):
            draw.text((x1 + 22, y), part, font=fnt, fill=color)
            y += 27 if fnt is BODY else 23
        y += 3


def pill(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], text: str, fill: str, outline: str) -> None:
    rounded(draw, xy, fill=fill, outline=outline, width=2, radius=17)
    x1, y1, x2, y2 = xy
    tw, th = text_size(draw, text, SMALL)
    draw.text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2 - 1), text, font=SMALL, fill=COLORS["ink"])


def arrowhead(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str, size: int = 16) -> None:
    angle = atan2(end[1] - start[1], end[0] - start[0])
    p1 = (end[0] - size * cos(angle) + size * 0.55 * sin(angle), end[1] - size * sin(angle) - size * 0.55 * cos(angle))
    p2 = (end[0] - size * cos(angle) - size * 0.55 * sin(angle), end[1] - size * sin(angle) + size * 0.55 * cos(angle))
    draw.polygon([end, p1, p2], fill=color)


def dashed_line(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    *,
    fill: str,
    width: int,
    dash_len: int = 16,
    gap_len: int = 12,
) -> None:
    x1, y1 = start
    x2, y2 = end
    dx, dy = x2 - x1, y2 - y1
    length = max(1, int((dx * dx + dy * dy) ** 0.5))
    step = dash_len + gap_len
    for i in range(0, length, step):
        t1 = i / length
        t2 = min(i + dash_len, length) / length
        draw.line((x1 + dx * t1, y1 + dy * t1, x1 + dx * t2, y1 + dy * t2), fill=fill, width=width)


def arrow(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[int, int]],
    *,
    color: str = COLORS["line"],
    width: int = 4,
    dash: bool = False,
) -> None:
    if dash:
        for a, b in zip(points, points[1:]):
            dashed_line(draw, a, b, fill=color, width=width)
    else:
        draw.line(points, fill=color, width=width, joint="curve")
    arrowhead(draw, points[-2], points[-1], color)


def badge(draw: ImageDraw.ImageDraw, center: tuple[int, int], label: str, color: str) -> None:
    x, y = center
    draw.ellipse((x - 25, y - 25, x + 25, y + 25), fill=color, outline="#ffffff", width=3)
    tw, th = text_size(draw, label, NUMBER)
    draw.text((x - tw / 2, y - th / 2 - 2), label, font=NUMBER, fill="#ffffff")


def draw_matrix(draw: ImageDraw.ImageDraw, origin: tuple[int, int]) -> None:
    x, y = origin
    node_labels = ["N1", "N2", "N3", "N4", "N5", "N6"]
    modality_labels = ["pH", "ORP", "EC", "UV", "Q"]
    cell = 22
    for i, node in enumerate(node_labels):
        draw.text((x - 34, y + i * cell + 2), node, font=TINY, fill=COLORS["muted"])
        for j, _ in enumerate(modality_labels):
            fill = "#2f83ad" if (i + j) % 3 != 0 else "#ffffff"
            outline = "#98bfd4"
            draw.rectangle((x + j * cell, y + i * cell, x + (j + 1) * cell - 3, y + (i + 1) * cell - 3), fill=fill, outline=outline, width=1)
    for j, label in enumerate(modality_labels):
        draw.text((x + j * cell - 1, y - 22), label, font=TINY, fill=COLORS["muted"])


def draw_process_loop(draw: ImageDraw.ImageDraw) -> None:
    x, y = 2040, 610
    names = ["均质/暂存", "反应核心", "催化剂床", "末端精处理"]
    for idx, name in enumerate(names):
        cx = x + idx * 205
        rounded(draw, (cx, y, cx + 152, y + 78), fill="#ffffff", outline=COLORS["green"], width=2, radius=17)
        tw, th = text_size(draw, name, SMALL)
        draw.text((cx + 76 - tw / 2, y + 27), name, font=SMALL, fill=COLORS["ink"])
        if idx < len(names) - 1:
            arrow(draw, [(cx + 152, y + 39), (cx + 205, y + 39)], color=COLORS["green"], width=4)
    arrow(draw, [(x + 675, y + 84), (x + 675, y + 165), (x + 76, y + 165), (x + 76, y + 84)], color=COLORS["green"], width=4, dash=True)
    draw.text((x + 205, y + 184), "回流 / 延长停留 / 暂存验证：把慢传感变成可用窗口", font=SMALL, fill=COLORS["green"])


def draw_logic_key(draw: ImageDraw.ImageDraw) -> None:
    x, y = 2145, 62
    items = [
        ("主数据/决策流", COLORS["line"], False),
        ("循环反馈流", COLORS["green"], True),
        ("校准/写回流", COLORS["orange"], True),
        ("硬阻断边界", COLORS["red"], True),
    ]
    for idx, (label, color, dash) in enumerate(items):
        yy = y + idx * 32
        arrow(draw, [(x, yy), (x + 75, yy)], color=color, width=3, dash=dash)
        draw.text((x + 88, yy - 10), label, font=TINY, fill=COLORS["muted"])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (3100, 1900), COLORS["bg"])
    draw = ImageDraw.Draw(image)

    draw.text((80, 48), "低成本传感循环式水处理智能闭环：全模型逻辑图", font=TITLE, fill=COLORS["ink"])
    draw.text(
        (84, 118),
        "核心不是展示材料，而是让“少量低成本传感 + 循环结构 + 软传感灰箱 + 多智能体诊断控制 + 现场校准”形成可验证、可落地的工程模型。",
        font=SUBTITLE,
        fill=COLORS["muted"],
    )
    draw_logic_key(draw)

    rounded(draw, (80, 170, 3020, 255), fill=COLORS["navy"], outline=COLORS["navy"], width=1, radius=24)
    draw.text((118, 195), "第一性原理", font=TAG, fill="#b7d8ff")
    draw.text(
        (245, 195),
        "循环结构为软传感、慢证据和多智能体诊断争取时间，所以传感器不用又快又贵；但每一次动作都必须经过不确定性、安全门、现场 replay 或人工复核约束。",
        font=BODY,
        fill="#edf5ff",
    )

    # Main model lanes.
    panel(draw, (80, 310, 540, 1290), "1 真实对象与稀疏感知", COLORS["blue"])
    card(
        draw,
        (115, 415, 505, 575),
        "污染场景与过程对象",
        ["某类污染物 / 某类废水 / 某类材料体系", "均质池、反应核心、催化剂床、回流环、末端单元", "·先定义场景，模型才有现实边界"],
        fill=COLORS["blue_fill"],
        outline="#9ecde5",
        tag="场景",
    )
    card(
        draw,
        (115, 625, 505, 835),
        "Agent48 管网布点与稀疏感知",
        ["节点 × 区域 × 传感模态 × 时间 的观测矩阵", "缺失掩码、布点编号、噪声、漂移、传感器经济性", "·目标：少量传感器支撑状态重构、异常分类和低延迟保护"],
        fill=COLORS["blue_fill"],
        outline="#9ecde5",
        tag="P1",
    )
    draw_matrix(draw, (235, 744))
    card(
        draw,
        (115, 900, 505, 1110),
        "慢证据与现场标签",
        ["离线 lab：目标污染物、氧化剂余量、副产物", "催化剂年龄、再生记录、人工复核、operation log", "·慢证据用于校准和 replay，不伪装成实时真值"],
        fill=COLORS["orange_fill"],
        outline="#ddb279",
        tag="field",
    )

    panel(draw, (620, 310, 1810, 1290), "2 黑箱到灰箱的状态推理中枢", COLORS["purple"])
    card(
        draw,
        (660, 415, 1015, 610),
        "数据质控 + 软传感器",
        ["从 pH / ORP / EC / UV254 / 浊度 / 流量等低成本信号估计隐藏状态", "输出预测区间、外推风险、校准状态", "·P5 将 node/modality/missingness 接入软传感合同"],
        fill=COLORS["purple_fill"],
        outline="#b8a5de",
        tag="P5",
    )
    card(
        draw,
        (1060, 415, 1415, 610),
        "最小灰箱物理 prior",
        ["停留时间分布、短流/旁路、拟一级反应", "质量守恒、基质抑制、催化剂衰减、副产物风险", "·目前是 synthetic prior，等待 field 参数校准"],
        fill=COLORS["green_fill"],
        outline="#8bc7a7",
        tag="P4",
    )
    card(
        draw,
        (1460, 415, 1770, 610),
        "可推理知识图谱",
        ["污染物-基质-材料-工艺-信号-状态-动作", "证据等级：文献 / 仿真 / field / 假设", "·提供机理解释和动作约束"],
        fill=COLORS["yellow_fill"],
        outline="#d7bf4d",
        tag="KG",
    )

    rounded(draw, (705, 705, 1745, 875), fill="#ffffff", outline=COLORS["purple"], width=3, radius=30)
    draw.text((740, 735), "灰箱状态向量 z(t)：把过程黑箱变成可审查状态", font=CARD_TITLE, fill=COLORS["ink"])
    state_labels = [
        "残留污染物风险",
        "反应完成度",
        "催化剂有效活性",
        "基质抑制强度",
        "水力短流风险",
        "副产物风险",
        "传感可信度",
        "不确定性/OOD",
    ]
    for i, label in enumerate(state_labels):
        px = 740 + (i % 4) * 240
        py = 790 + (i // 4) * 42
        pill(draw, (px, py, px + 210, py + 34), label, COLORS["grey_fill"], "#ccd6df")

    card(
        draw,
        (660, 960, 1000, 1160),
        "机理解释 Agent",
        ["解释为何需要回流、加药、再生、延时或预处理", "把文献/KG 证据附到结论上"],
        fill=COLORS["white"],
        outline="#c9d4df",
    )
    card(
        draw,
        (1035, 960, 1375, 1160),
        "故障诊断 Agent",
        ["区分传感漂移、水力异常、氧化剂不足、催化剂失活、基质冲击", "判断过程失败还是测量失败"],
        fill=COLORS["white"],
        outline="#c9d4df",
    )
    card(
        draw,
        (1410, 960, 1770, 1160),
        "不确定性与门控 Agent",
        ["保形校准、field holdout、外推风险", "给出可执行、需验证或必须阻断的边界"],
        fill=COLORS["white"],
        outline="#c9d4df",
    )

    panel(draw, (1890, 310, 3020, 1290), "3 循环控制与多设施协同", COLORS["green"])
    card(
        draw,
        (1930, 415, 2300, 565),
        "候选动作生成",
        ["回流、暂存、延长停留、调药剂", "再生/更换催化剂、切换单元、旁路验证、禁止放行"],
        fill=COLORS["green_fill"],
        outline="#8bc7a7",
        tag="动作",
    )
    card(
        draw,
        (2340, 415, 2980, 565),
        "Agent49/52 多设施协同控制",
        ["把设施状态、动作、奖励、回放评估接成 policy candidate", "联合奖励包含安全、成本、能耗、误动作、延迟和验证需求", "·synthetic 阶段只生成候选，不写执行器"],
        fill=COLORS["green_fill"],
        outline="#8bc7a7",
        tag="P3",
    )
    draw_process_loop(draw)
    card(
        draw,
        (1930, 855, 2360, 1110),
        "工程执行约束进入 reward/仲裁",
        ["泵阀动作次数、执行器延迟、池容、药剂库存、维护窗口", "人工复核时间、离线检测排队、误动作成本", "·这些不是说明文字，而是进入策略评价"],
        fill=COLORS["orange_fill"],
        outline="#ddb279",
        tag="P7",
    )
    card(
        draw,
        (2400, 855, 2980, 1110),
        "安全仲裁与放行门",
        ["不确定性高、field gate 未过、replay 证据不足时，只允许保护性候选策略", "没有现场留出集/现场回放：不能写 release gate，不能写真实执行器策略"],
        fill=COLORS["red_fill"],
        outline="#d58f8f",
        tag="硬边界",
    )

    panel(draw, (80, 1360, 3020, 1815), "4 验证、学习、工程治理：决定什么能写回模型", COLORS["grey"])
    card(
        draw,
        (120, 1460, 600, 1695),
        "现场数据接口与 replay 链",
        ["Agent30/42/43/44/45：sensor、lab、operation、fast proxy 对齐到同一时间轴", "计算 precision/recall、lead time、误触发成本、导入 provenance", "·只通过真实 replay 后才允许保护性控制写回"],
        fill=COLORS["blue_fill"],
        outline="#9ecde5",
    )
    card(
        draw,
        (650, 1460, 1130, 1695),
        "软传感 field holdout 与弱目标校准",
        ["Agent36/39/46/47：coverage、区间宽度、OOD、abstention、弱目标覆盖", "重点盯住 catalyst_activity、matrix_interference 等弱状态", "·synthetic 只验证接口，不能当实证结论"],
        fill=COLORS["purple_fill"],
        outline="#b8a5de",
    )
    card(
        draw,
        (1180, 1460, 1660, 1695),
        "知识与模型真实性审计",
        ["Agent35/37/38：知识库从论文条目变成可推理 KG", "每条 claim 都写来源、适用条件、失败边界和数据需求", "·区分文献支持、仿真成立、现场待验证"],
        fill=COLORS["yellow_fill"],
        outline="#d7bf4d",
    )
    card(
        draw,
        (1710, 1460, 2190, 1695),
        "跨批次工程运行层",
        ["Agent12-28：多批次调度、队列、资源扩容、长期经济性、压力测试、恢复放量", "把单批次动作转成 campaign 级可执行方案"],
        fill=COLORS["orange_fill"],
        outline="#ddb279",
    )
    card(
        draw,
        (2240, 1460, 2980, 1695),
        "Agent50 自我打断治理与当前核心优先级",
        ["按模型关联度、链条影响、科研价值、工程可行性和验证就绪度排序", "展示/收束若不改变模型指标，自动降为低优先级", "当前主轴：P5 软传感矩阵耦合；通过后转向 P7 工程执行约束进入 reward 与仲裁"],
        fill=COLORS["white"],
        outline="#c9d4df",
    )

    # Main arrows.
    arrow(draw, [(540, 505), (620, 505)], color=COLORS["line"], width=5)
    badge(draw, (580, 468), "1", COLORS["blue"])
    draw.text((548, 430), "观测进入模型", font=SMALL, fill=COLORS["blue"])

    arrow(draw, [(1015, 512), (1060, 512)], color=COLORS["line"], width=4)
    arrow(draw, [(1415, 512), (1460, 512)], color=COLORS["line"], width=4)
    arrow(draw, [(835, 610), (925, 705)], color=COLORS["purple"], width=4)
    arrow(draw, [(1237, 610), (1230, 705)], color=COLORS["green"], width=4)
    arrow(draw, [(1615, 610), (1510, 705)], color=COLORS["yellow"], width=4)
    badge(draw, (1195, 660), "2", COLORS["purple"])
    draw.text((1228, 650), "估计灰箱状态", font=SMALL, fill=COLORS["purple"])

    arrow(draw, [(1225, 875), (1225, 960)], color=COLORS["line"], width=5)
    badge(draw, (1270, 922), "3", COLORS["purple"])
    draw.text((1302, 912), "诊断解释", font=SMALL, fill=COLORS["purple"])

    arrow(draw, [(1770, 1060), (1890, 1060)], color=COLORS["line"], width=5)
    badge(draw, (1835, 1015), "4", COLORS["green"])
    draw.text((1812, 977), "生成候选动作", font=SMALL, fill=COLORS["green"])

    arrow(draw, [(2300, 495), (2340, 495)], color=COLORS["line"], width=4)
    arrow(draw, [(2615, 565), (2615, 610)], color=COLORS["green"], width=4)
    badge(draw, (2532, 725), "5", COLORS["green"])
    draw.text((2562, 715), "循环执行并反馈", font=SMALL, fill=COLORS["green"])

    # Physical process feedback to sensing.
    arrow(draw, [(2868, 775), (2868, 1265), (312, 1265), (312, 1110)], color=COLORS["green"], width=4, dash=True)

    # Validation/writeback loops.
    arrow(draw, [(312, 1110), (312, 1360)], color=COLORS["orange"], width=4, dash=True)
    arrow(draw, [(900, 1460), (900, 1200), (850, 1160)], color=COLORS["orange"], width=4, dash=True)
    arrow(draw, [(1420, 1460), (1420, 1225), (1585, 1160)], color=COLORS["orange"], width=4, dash=True)
    arrow(draw, [(2605, 1460), (2605, 1215), (2690, 1110)], color=COLORS["orange"], width=4, dash=True)
    badge(draw, (900, 1345), "6", COLORS["orange"])
    draw.text((932, 1335), "现场校准/写回", font=SMALL, fill=COLORS["orange"])

    # Hard boundary from arbitration to validation.
    arrow(draw, [(2690, 1110), (2690, 1360)], color=COLORS["red"], width=4, dash=True)

    # Governance back to model core.
    arrow(draw, [(2610, 1460), (2610, 1325), (1225, 1325), (1225, 1160)], color=COLORS["orange"], width=4, dash=True)
    badge(draw, (2215, 1325), "7", COLORS["orange"])
    draw.text((2248, 1314), "自我打断：回到最高边际价值模型问题", font=SMALL, fill=COLORS["orange"])

    rounded(draw, (80, 1835, 3020, 1882), fill="#ffffff", outline="#d0dae3", width=2, radius=16)
    draw.text(
        (112, 1850),
        "读图方式：左侧回答“能观测什么”，中间回答“如何把黑箱变灰箱”，右侧回答“能做什么动作并如何循环”，底部回答“哪些结论可以写回，哪些必须停在仿真/候选/待验证”。",
        font=SMALL,
        fill=COLORS["muted"],
    )

    image.save(OUT_PRIMARY)
    image.save(OUT_LEGACY)
    image.save(OUT_CORE)
    print(OUT_PRIMARY)


if __name__ == "__main__":
    main()
