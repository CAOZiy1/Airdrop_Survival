# Airdrop Survival Intro Module

这是一个末日背景的“空投生存”小游戏demo。高空的飞机会不断投掷炸弹、金币和回血包；你需要左右移动去躲避炸弹、收集金币/回血包，并在关卡倒计时结束前达到目标。该仓库包含完整可运行的 Pygame 项目、音效与示例资产（音效与 BGM 可选，缺失时游戏会静默运行）。


## How to Run

前置要求
- Python 3.9 或更高（推荐 3.10+）
- 依赖：`pygame>=2.6.0`、`numpy`（用于死亡灰度特效，已在 requirements.txt 中列出）

快速运行（Windows / PowerShell）
```powershell
# 克隆仓库并进入目录
git clone https://github.com/CAOZiy1/Airdrop_Survival.git
cd Airdrop_Survival

# 建议在虚拟环境中安装依赖
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安装依赖
python -m pip install -U pip
pip install -r requirements.txt

# 运行主程序（先播 Intro，再进入 Game）
python .\airdrop_survival\src\main.py
```

可选安装与素材
- 若缺少基本 PNG 素材，可生成占位图以快速体验：
```powershell
python .\airdrop_survival\tools\generate_assets.py
```

---

## Input and Feedback

Input
- 键盘: 左右方向键 或 A / D 控制玩家移动（支持长按）。
- 鼠标: 在 Intro 场景点击 “ENTER GAME” 按钮以开始；结算界面可点击 Back to Menu 或 Quit。

Feedback
- 视觉反馈: HUD 显示生命（心数）、金币与右上角目标奖励提示；拾取金币/医疗包显示 +1 浮动文字；受伤/死亡显示覆盖图；可选背景图；顶部显示“XX seconds until starvation” 倒计时条目。
- 听觉反馈: 背景 BGM 优先加载 `assets/sounds/bgm.mp3`，无则尝试 `bgm.wav`；拾取/爆炸/治疗/结局尝试播放对应音效（缺失时静默）。
- 规则反馈: 60 秒后按金币数评判胜负；胜利播放 success.wav，失败播放 failure.wav 并显示结算界面。

---

## Project Structure

```
airdrop_survival/
├── README.md
├── requirements.txt
├── assets/
│   ├── sounds/                # BGM 与音效（可选，缺失则静默）
│   └── screenshots/           # 截图占位（可自行创建）
├── src/
│   ├── main.py                # 入口：播放 Intro（若需要）然后启动 Game
│   ├── game.py                # 主循环、碰撞、计时、结局与结局音乐控制
│   ├── intro.py               # 开场动画、飞机投放、ENTER GAME 按钮
│   ├── player.py              # 玩家控制与渲染（受伤、死亡覆盖图/动画）
│   ├── drop.py                # 掉落物逻辑、图像/音效加载与播放
│   ├── ui.py                  # HUD 与界面绘制、倒计时提示
│   ├── audio.py               # 预留：音频辅助（当前无合成 BGM）
│   ├── settings.py            # 全局设置：分辨率、速度、音量、Intro 重播等
│   └── state.py               # 运行时状态标记（例如 intro_shown）
└── tools/
    ├── check_wav.py           # 检查 success.wav/failure.wav 等是否可被 Pygame 播放
    ├── generate_assets.py     # 生成炸弹/硬币/医疗包占位图（PNG）
    └── make_transparent.py    # 将近白背景变透明的小工具
```

重要文件说明
- 结局音乐文件：`assets/sounds/success.wav` 与 `assets/sounds/failure.wav`（推荐 PCM 16-bit / 44100Hz WAV 以确保兼容性）。
- 背景 BGM：优先 `assets/sounds/bgm.mp3`，无则尝试 `bgm.wav`。
- Intro 仅在本进程第一次进入时播放；`src/settings.py` 的 `REPLAY_INTRO_ON_RETURN` 控制返回菜单时是否重播。

---

## Implementation Mapping

- 玩家输入与主循环: `src/game.py`（事件循环、键盘输入、关卡计时、结算与音乐切换）。
- 玩家渲染与状态: `src/player.py`（移动、受伤/死亡覆盖图与绘制尺寸控制）。
- 掉落物逻辑与音效: `src/drop.py`（加载图片/音效、更新/绘制、播放拾取/爆炸/治疗音效）。
- HUD 与 UI: `src/ui.py`（生命、金币、右上角目标提示、中心倒计时与结算界面）。
- Intro 动画: `src/intro.py`（飞机飞行、三段投放、渐暗与 Enter 按钮）。
- 结局音乐和切换逻辑: `src/game.py::_play_ending_music`（停止 BGM、播放成功/失败音乐）。
- 可选音频辅助: `src/audio.py`（当前为占位，不再合成 BGM）。

---

## How This Meets Assignment Objectives

- Python 为主实现: 项目以 Python（Pygame）编写，所有交互逻辑位于 `src/` 下。
- 至少一种用户输入: 实现键盘（左右/A D）和鼠标点击交互，触发即时反馈。
- 实时反馈机制: 拾取、受伤、死亡、结算切换均有视觉与音频反馈；缺素材时安全降级。
- 状态管理与交互逻辑: hearts（生命）、coins（金币）、timer（倒计时）驱动成功/失败分支。
- 创意与审美整合: 通过倒计时、加速掉落与声效设计，营造紧张的生存体验。

---

## Demo Assets and Screenshots (占位与指示)

请在仓库中添加以下截图与可选视频链接以便评分者快速预览。把截图放到 `assets/screenshots/` 目录，并确保文件名与下方占位一致。

- assets/screenshots/intro.png  — Intro 飞机进入画面  
- assets/screenshots/drop.png   — 投放物资瞬间（炸弹/金币/回血包）  
- assets/screenshots/success.png — 成功结局画面  
- assets/screenshots/failure.png — 失败结局画面

将下面 Markdown 区块直接保留到 README（或已经存在则替换占位），在你添加实际截图后图片会显示：

```markdown
## Demo

![Intro - 飞机进入](assets/screenshots/intro.png)   <!-- ADD: intro screenshot -->
![Drop Moment - 投放瞬间](assets/screenshots/drop.png)   <!-- ADD: drop moment screenshot -->
![Success Screen - 成功结局](assets/screenshots/success.png)   <!-- ADD: success screenshot -->
![Failure Screen - 失败结局](assets/screenshots/failure.png)   <!-- ADD: failure screenshot -->

🎥 Demo video: https://youtu.be/your-demo-link  <!-- OPTIONAL: replace with your demo video -->
```

占位说明（便于后续替换）：
- 把每张截图命名并放入 `assets/screenshots/`，同 README 中的路径一致。  
- 如果没有视频，可暂时移除视频行或用 `TBD` 占位。  
- 推荐每张截图尺寸不超过 1600px 宽并压缩为 PNG 或 JPG。

---

## Submission Notes and Checklist

请确保仓库为 Public 并及时在课程平台提交 GitHub 链接。

提交前检查项：
- [ ] README 明确列出输入、反馈与实现映射  
- [ ] requirements.txt 包含主要依赖并标注可选项（numpy）  
- [ ] assets/sounds 包含 `success.wav` 与 `failure.wav` 或在 README 中说明占位  
- [ ] 在 README 中放置至少 3 张关键截图（Intro / 投放 / 结局）或提供视频链接  
- [ ] 仓库为 Public，并将链接提交到课程平台（可在截止前继续更新）

---

## Credits and Notes

- 代码基于 Pygame；音效与素材请使用免版权或自行创作的资源，并在 README 中注明第三方素材来源与授权信息（如 Pixabay、Freesound 等）。  
- 若结局音乐无法播放，请查看终端日志或使用 `tools/check_wav.py` 校验 `assets/sounds/success.wav` 与 `failure.wav` 的格式与可播放性。  
- `src/settings.py` 提供了大量可调参数（掉落速度、权重、音量、Intro 重播等），可根据演示需要快速调优。

---

祝你玩得开心，也欢迎继续扩展更多关卡与玩法！




