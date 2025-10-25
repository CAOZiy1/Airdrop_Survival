# Airdrop Survival

这是一个末日背景的“空投生存”小游戏。高空飞机会不断投掷炸弹、金币和回血包；你需要左右移动去躲避炸弹、收集金币/回血包，在关卡倒计时结束前达成目标。

## 如何运行

最直接：点击运行 `src/main.py`（在 VS Code 打开它，然后点右上角“运行”按钮；或在文件资源管理器里用 Python 运行）。

或使用命令行（Windows PowerShell）：

```powershell
# 在 airdrop_survival/ 目录下
python -m pip install -r requirements.txt
python .\src\main.py
```

可选（增强特效）：
- 安装 numpy（用于更丰富的紧张 BGM 合成和死亡灰度特效）：
  ```powershell
  python -m pip install numpy
  ```

## 玩法简介

- UI：左上角为生命（3 颗心）；右上角是奖励图标与所需金币数；顶部中间是关卡倒计时（默认 60 秒）。
- 规则：被炸弹命中 -1 心；回血包 +1 心（最多 3）；倒计时结束时若金币数达到要求（默认 20）则成功，否则失败。
- 音频：成功/失败会播放对应结局音乐。播放前会自动停止背景 BGM，避免盖过结局音。
- 操作：方向键 ←/→ 或 A / D。

## 设计思路与架构

目录结构（关键文件/用途）：

```
airdrop_survival/
  assets/
    sounds/
      success.wav       # 玩家提供的成功结局音乐
      failure.wav       # 玩家提供的失败结局音乐
      urgent_bgm*.wav   # 紧张背景音乐（缺失时可由程序合成占位）
  src/
    main.py     # 入口：启动 Intro（仅首次），然后进入 Game
    game.py     # 游戏主循环、碰撞判定、关卡计时、结局音乐播放与返回菜单
    intro.py    # 开场动画与“ENTER GAME”菜单
    audio.py    # 背景 BGM（urgent_bgm）的简易合成与变体工具
    settings.py # 游戏参数：分辨率、掉落频率、音量、是否回菜单后重播 Intro 等
    state.py    # 运行期标记：本进程是否已播放过 Intro（intro_shown）
    player.py   # 玩家移动/渲染
    drop.py     # 掉落物（炸弹/金币/回血包）与拾取/爆炸音效初始化
    ui.py       # 背景与状态栏、提示文案、结算面板等绘制
```

说明：
- 结局音乐必须命名为 `assets/sounds/success.wav` 与 `assets/sounds/failure.wav`。
  - 为最佳兼容，推荐标准 WAV（RIFF）PCM 16-bit/44100Hz；若是“非 PCM 的 WAV”，`mixer.music` 可能不识别，程序会自动回退到 `mixer.Sound` 播放，仍可正常响起。
- 背景 BGM 使用 `urgent_bgm.wav`；缺失时会自动合成一个占位音轨，你可以用同名文件替换它。
- Intro 默认“仅首次”播放；回到菜单后点击 ENTER GAME 会直接开始。可在 `settings.py` 修改：
  - `REPLAY_INTRO_ON_RETURN = False`（默认）：回菜单不重播 Intro；
  - 改为 `True` 则每次回菜单都会重播 Intro。

## 享受游戏体验！

如果你想进一步调整难度（掉落频率/速度、关卡时长、音量等），可编辑 `src/settings.py`；若结局音乐不响，可在终端查看 `[ending-music]` 开头的日志，或使用仓库根目录下的 `tools/check_wav.py` 检查文件格式。




