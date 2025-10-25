# Airdrop Survival

Post-apocalyptic “airdrop survival” mini game. A plane drops bombs, coins, and health packs; you move left and right to dodge bombs and collect items before the level timer runs out.

## How to run

Easiest: open and run `src/main.py` (in VS Code: open the file and click “Run” at the top-right; or run it with Python from your file explorer).

Or use Windows PowerShell:

```powershell
# from the airdrop_survival/ folder
python -m pip install -r requirements.txt
python .\src\main.py
```

Optional (enhanced effects):
- Install numpy (for richer urgent BGM synthesis and a grayscale death effect):
  ```powershell
  python -m pip install numpy
  ```

## Gameplay

- UI: top-left shows hearts (3 lives); top-right shows the reward icon and required coins; top-center is the level timer (default 60s).
- Rules: getting hit by a bomb costs 1 heart; a health pack restores 1 heart (max 3); when the timer ends, reach the coin goal (default 20) to succeed, otherwise you fail.
- Audio: success/failure music plays at the end; background BGM fades out/stops first so it won’t mask the ending track.
- Controls: use Left/Right arrows or A/D.

## Design and architecture

Folder layout and purpose:

```
airdrop_survival/
  assets/
    sounds/
      success.wav       # your success ending music
      failure.wav       # your failure ending music
      urgent_bgm*.wav   # urgent background music (auto-generated placeholder if missing)
  src/
    main.py     # entry: plays Intro once, then starts the Game
    game.py     # main loop, collisions, level timing, ending music, back-to-menu flow
    intro.py    # intro animation and menu with ENTER GAME
    audio.py    # simple synthesis/variants for urgent_bgm
    settings.py # game constants: resolution, spawn rates, audio volume, intro replay flag, etc.
    state.py    # runtime flag: whether Intro has been shown (intro_shown)
    player.py   # player movement/rendering
    drop.py     # drops (bomb/coin/health) and pickup/explosion sound init
    ui.py       # background, HUD/status, hints, result panels
```

Notes:
- Ending music files must be named `assets/sounds/success.wav` and `assets/sounds/failure.wav`.
  - For best compatibility, use standard WAV (RIFF) PCM 16‑bit at 44100 Hz. If a file is a non‑PCM WAV (or another codec renamed as .wav), `mixer.music` may reject it; the game will automatically fall back to `mixer.Sound` so it still plays.
- Background BGM: if `assets/sounds/bgm.mp3` exists, it will be used. Otherwise the game uses `urgent_bgm.wav`; if that’s missing, a simple placeholder is synthesized automatically.
- The Intro plays only on first run; after returning to menu, ENTER GAME starts immediately. You can change this in `settings.py`:
  - `REPLAY_INTRO_ON_RETURN = False` (default): don’t replay Intro on return;
  - set to `True` to replay the Intro every time you go back to the menu.

## Enjoy!

Tweak difficulty (spawn rates/speed), timer, and audio volume in `src/settings.py`. If an ending track doesn’t play, check the console for `[ending-music]` logs, or use `airdrop_survival/tools/check_wav.py` to validate the file format.

---

## 中文说明（Chinese Version）

这是一个末日背景的“空投生存”小游戏。高空的飞机会不断投掷炸弹、金币和回血包；你需要左右移动去躲避炸弹、收集金币/回血包，并在关卡倒计时结束前达到目标。

### 如何运行

最直接：点击运行 `src/main.py`（在 VS Code 打开该文件并点击右上角“运行”；或在资源管理器中用 Python 运行）。

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

### 玩法简介

- UI：左上角为生命（3 颗心）；右上角是奖励图标与所需金币数；顶部中间是关卡倒计时（默认 60 秒）。
- 规则：被炸弹命中 -1 心；回血包 +1 心（最多 3）；倒计时结束时若金币数达到要求（默认 20）则成功，否则失败。
- 音频：成功/失败时会播放对应的结局音乐；播放前会自动停止背景 BGM，避免盖过结局音。
- 操作：方向键 ←/→ 或 A / D。

### 设计与架构

目录结构与用途（基于当前仓库）：

```
README.md                    # 项目说明（本文件）
requirements.txt             # Python 依赖（pygame 2.6+，可选 numpy）

airdrop_survival/
  assets/
    sounds/
      success.wav            # 成功结局音乐
      failure.wav            # 失败结局音乐
      urgent_bgm*.wav        # 紧张背景音乐（缺失时程序会合成占位，可自行替换）

  src/
    main.py                  # 入口：首次播放 Intro（仅一次），随后进入 Game
    game.py                  # 主循环、碰撞与计时、结局音乐（含 BGM 停止与回退播放）、返回菜单逻辑
    intro.py                 # 开场动画与“ENTER GAME”按钮；飞机投放物品、渐暗与提示
    audio.py                 # 紧张 BGM（urgent_bgm）的简易合成与变体生成
    settings.py              # 全局参数：分辨率、掉落频率/速度、音量、是否回菜单重播 Intro 等
    state.py                 # 运行期标记：本进程是否已播放过 Intro（intro_shown）
    player.py                # 玩家移动与渲染（含可选描边、受伤/死亡贴图）
    drop.py                  # 掉落物（炸弹/金币/回血包）逻辑与拾取/爆炸音效初始化
    ui.py                    # 背景绘制、HUD 状态（生命/金币/定时器/奖励提示）、结算/倒计时面板
    __pycache__/             # Python 字节码缓存目录（可忽略）

  tools/
    generate_assets.py       # 资产生成辅助脚本（如占位或批量处理，具体见脚本注释）
    make_transparent.py      # 将图片背景处理为透明的帮助脚本（具体见脚本注释）
    check_wav.py             # WAV 检查脚本（校验音频格式/是否可被 pygame 识别）
```

注意：
- 结局音乐文件须命名为 `assets/sounds/success.wav` 与 `assets/sounds/failure.wav`。
  - 为最佳兼容，推荐使用标准 WAV（RIFF）PCM 16-bit / 44100Hz；若是“非 PCM 的 WAV”，`mixer.music` 可能不识别，程序会自动回退到 `mixer.Sound` 播放，仍可正常响起。
- 背景 BGM：若存在 `assets/sounds/bgm.mp3` 则优先使用；否则使用 `urgent_bgm.wav`。若 `urgent_bgm.wav` 不存在，程序会自动合成一个占位音轨。
- Intro 默认“仅首次”播放；回到菜单后点击 ENTER GAME 会直接开始。可在 `settings.py` 修改：
  - `REPLAY_INTRO_ON_RETURN = False`（默认）：回菜单不重播 Intro；
  - 改为 `True` 则每次回菜单都会重播 Intro。

### 祝你游戏愉快！

想要调整难度（掉落频率/速度）、关卡时长或音量，请编辑 `src/settings.py`。若结局音乐不响，可在终端查看以 `[ending-music]` 开头的日志，或使用 `airdrop_survival/tools/check_wav.py` 检查文件格式。




