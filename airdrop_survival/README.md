# Airdrop Survival (starter)

Simple starter project skeleton for a small pygame game.

Prerequisites
- Python 3.8+
- pip

Install dependencies (PowerShell):

```powershell
python -m pip install -r requirements.txt
```

Run the game (PowerShell):

```powershell
python -m src.main
```

Notes
游戏设计说明（中文）

这是我想做这个游戏的想法：上空有一架飞机会不断投掷三种物品：炸弹、金币或回血包。下边是玩家角色，可以左右移动。右上或侧边的面板会显示两项数值：生命值（以三颗心表示）和金币数量。

玩法规则：
- 玩家初始有 3 颗心。每次被炸弹击中会失去一颗心。
- 如果生命值降到 0，触发 Game Over（失败结局），此时显示最终的金币数与剩余血量。
- 一个回血包会恢复一颗心，但生命值最多回到 3 颗。
- 每获得一枚金币，金币计数加 1。达到 50 个金币时触发胜利结局（Victory），并显示结算信息。

目标：尽量躲避炸弹，同时收集尽可能多的金币与补血的回血包。

控制：
- 左右方向键或 A/D 键控制玩家移动。

实现建议：
- UI 中最好不要依赖系统 emoji（不同系统/字体下可能无法显示），建议使用图片或用 pygame 绘制图标——已在本仓库中用程序绘制心形和金币图标以保证跨平台可见性。
- 将图像资源放到 `assets/`，并通过 `pygame.image.load(...).convert_alpha()` 加载以获得更好的外观。
