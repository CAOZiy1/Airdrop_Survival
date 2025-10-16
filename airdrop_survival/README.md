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

Hunger 与 经济（新特性）
- 玩家现在有一个饥饿值（以 3 个胃图标显示）。饥饿值会随时间衰减。
- 玩家可以通过金币购买食物：按下 "F" 键以花费一定金币换取 1 份食物来恢复 1 点饥饿值。
- 默认配置为 5 个金币换 1 份食物（可在 `src/settings.py` 中修改 COINS_PER_FOOD）。

Assets 说明
- 若想使用自定义胃图标，请把 `stomach.png` 放到 `assets/` 中（若缺失，游戏会使用内置绘制的简易胃图标作为回退）。
- 如果你有罐头图片并希望用于食物显示，可将其命名为 `can.png` 或替换 `health_pack.png`。
