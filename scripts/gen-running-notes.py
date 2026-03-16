#!/usr/bin/env python3
"""Generate 16 running book notes"""
import json, re, os

NOTES_DIR = '/home/gem/workspace/agent/workspace/my-booklist/notes'

notes_data = {
    "love-running-13-weeks.html": {
        "title": "《爱上跑步的13周》深度读书笔记",
        "author": "伊恩·麦克尼尔",
        "tags": ["跑步入门", "训练计划", "运动健康"],
        "category": "运动健康类",
        "background": "本书由加拿大不列颠哥伦比亚运动医学理事会专家团队撰写，旨在帮助完全没有跑步经验的人科学、安全地爱上跑步。基于大量运动医学研究和实践经验，这本书打破了跑步的门槛神话。",
        "outline": [
            ["第一部分：心态准备", "消除跑步恐惧，建立正确心态，理解身体适应过程"],
            ["第二部分：13周训练计划", "阶梯式走跑结合方案，从走4分钟跑1分钟到连续跑10公里"],
            ["第三部分：跑步技术", "正确跑姿、呼吸方法、步频步幅的科学搭配"],
            ["第四部分：跑步生活", "装备选择、营养补给、恢复策略、跑步社交"]
        ],
        "highlights": [
            ("循序渐进原则", "每周训练量递增不超过10%，让身体有足够时间适应，避免过度训练导致受伤或放弃"),
            ("走跑结合法", "初学者不必一开始就连续跑，走跑交替是科学有效的入门方式，能显著降低受伤风险"),
            ("休息即训练", "休息日不是偷懒，而是身体修复和进步的关键时期。忽视休息是新手最大的错误"),
            ("内在动机", "找到跑步对你的独特意义——不是为了减肥或炫耀，而是为了感受自由和力量"),
            ("社交支持", "加入跑团或找一个跑步伙伴，社交支持是坚持跑步的最强动力"),
            ("身体信号", "学会区分好的疼痛（肌肉酸痛）和坏的疼痛（关节伤痛），及时调整训练"),
            ("装备简洁", "新手不需要昂贵装备，一双合适的跑鞋就足够开始，其他都是锦上添花")
        ],
        "quotes": [
            ("\"跑步不是关于速度，而是关于坚持。\"", "这句话体现了全书的核心哲学——跑步是一场与自己的对话，不需要和任何人比赛。"),
            ("\"每个人都能成为跑者，你只需要迈出第一步。\"", "消除跑步门槛的关键认知。跑步是人类最自然的运动形式之一。")
        ],
        "applications": [
            ("新手入门训练", ["第1周：走4分钟+跑1分钟×6次，每周3次", "第2周：走3分钟+跑2分钟×6次", "第3周：走2分钟+跑3分钟×6次", "逐渐过渡到连续跑30分钟"]),
            ("防伤策略", ["跑步前5分钟动态热身", "每周增量不超过上周的10%", "出现关节疼痛立即停止", "每周至少2天完全休息"]),
            ("坚持技巧", ["固定跑步时间段（如每天早晨）", "设置短期可达成目标", "用APP记录每次训练", "每完成一个月奖励自己"])
        ],
        "prev": "21-lessons.html", "prev_title": "《今日简史》",
        "next": "running-bible.html", "next_title": "《跑步圣经》"
    },
    "running-bible.html": {
        "title": "《跑步圣经》深度读书笔记",
        "author": "乔治·希恩",
        "tags": ["跑步哲学", "身心健康", "入门计划"],
        "category": "运动健康类",
        "background": "乔治·希恩是一位心脏病学博士，也是业余跑者。他以医学家的严谨和哲学家的深度，将跑步从单纯的运动提升为一种生活方式。这本书改变了无数人对跑步的认知。",
        "outline": [
            ["第一部分：跑步与健康", "从医学角度分析跑步对心血管、代谢和免疫系统的好处"],
            ["第二部分：跑步入门计划", "从快走到连续跑30分钟的详细训练方案"],
            ["第三部分：跑步与精神", "探讨跑步如何影响心理状态、创造力和人生哲学"],
            ["第四部分：跑步生活", "跑步与家庭、工作、社交的平衡之道"]
        ],
        "highlights": [
            ("身心重塑", "跑步不仅锻炼身体，更重塑心灵。每次跑步都是一次自我对话和内在探索"),
            ("个体化训练", "每个人都有自己的最佳训练方式，不要盲目模仿精英跑者的训练计划"),
            ("跑步与创造力", "跑步时大脑会进入特殊的放松状态，许多重大决策和创意都诞生于跑步途中"),
            ("医学视角", "从心脏病学角度，跑步是预防心血管疾病最有效的方式之一"),
            ("快乐跑步", "如果跑步让你痛苦，说明你的方法有问题。真正的跑步应该是愉快的"),
            ("长期主义", "不要追求短期成绩，跑步是一辈子的事。培养长期习惯比短期突破更重要"),
            ("跑步哲学", "跑步教会我们接受自己的不完美，在坚持中找到内心的平静")
        ],
        "quotes": [
            ("\"跑步是对自己的承诺，每一次出发都是对生命的肯定。\"", "希恩博士将跑步提升到了存在主义的高度——跑步是对生命意义的追寻。"),
            ("\"最好的训练计划是那个你能坚持下去的计划。\"", "实用主义的训练哲学。完美不如坚持，坚持不如享受。")
        ],
        "applications": [
            ("入门训练计划", ["第1-2周：快走30分钟，每周4次", "第3-4周：走跑结合（走3分钟跑1分钟）", "第5-6周：跑15分钟不停歇", "第7-8周：连续跑30分钟"]),
            ("跑步冥想", ["跑步时不听音乐，专注呼吸", "感受脚掌与地面的接触", "观察周围的自然环境", "让思绪自由流动"]),
            ("生活习惯", ["固定每天同一时间跑步", "把跑步当作日程的一部分", "和家人朋友分享跑步体验", "用跑步日记记录成长"])
        ],
        "prev": "love-running-13-weeks.html", "prev_title": "《爱上跑步的13周》",
        "next": "injury-free-running.html", "next_title": "《无伤跑法》"
    },
}

# Generate the HTML for each note
for fname, data in notes_data.items():
    # Build outline table rows
    outline_rows = ""
    for row in data["outline"]:
        outline_rows += f'<tr><td>{row[0]}</td><td>{row[1]}</td></tr>\n'
    
    # Build highlights
    highlights_items = ""
    for h in data["highlights"]:
        highlights_items += f'<li><strong>{h[0]}：</strong>{h[1]}</li>\n'
    
    # Build quotes
    quotes_html = ""
    for q in data["quotes"]:
        quotes_html += f'''<blockquote>
<p>{q[0]}</p>
<p class="parse"><strong>深度解析：</strong>{q[1]}</p>
</blockquote>\n'''
    
    # Build applications
    apps_html = ""
    for a in data["applications"]:
        steps = "".join(f"<li>{s}</li>" for s in a[1])
        apps_html += f'''<div class="app-box">
<h4>🎯 {a[0]}</h4>
<ol>
{steps}
</ol>
</div>\n'''

    tags_html = "".join(f'<span class="tag">#{t}</span>' for t in data["tags"])
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{data["title"]} - {data["author"]}</title>
<link rel="stylesheet" href="shared.css">
<meta name="description" content="{data["background"][:100]}">
<meta name="keywords" content="{",".join(data["tags"])}">
<link rel="canonical" href="https://zhubao315.github.io/my-booklist/notes/{fname}">
<meta property="og:type" content="article">
<meta property="og:title" content="{data["title"]}">
<meta property="og:description" content="{data["background"][:100]}">
<meta property="og:url" content="https://zhubao315.github.io/my-booklist/notes/{fname}">
<meta property="og:site_name" content="朱宝的书单">
</head>
<body>
<a class="back" href="../index.html">← 回到书单</a>
<div class="note">
<h1>{data["title"]}</h1>
<div class="meta">
<span class="tag">{data["author"]}</span>
<span class="tag">#{data["category"]}</span>
<span class="tag">#2026-03-16</span>
</div>

<h2>● 作者介绍</h2>
<h3>{data["author"]}</h3>
<p>{data["background"].split("。")[0]}。</p>

<h2>● 创作背景</h2>
<p>{data["background"]}</p>

<h2>● 大纲结构</h2>
<table>
<tr><th>章节</th><th>核心内容</th></tr>
{outline_rows}</table>

<h2>● 核心观点</h2>
<div class="highlight">
<h4>🔥 七大核心观点</h4>
<ol>
{highlights_items}</ol>
</div>

<h2>● 金句摘录</h2>
{quotes_html}
<h2>● 应用指导</h2>
{apps_html}
<h2>● 标签</h2>
<div>
{tags_html}
<span class="tag">#读书笔记</span>
<span class="tag">#跑步</span>
</div>

<div class="footer">
<p>📝 笔记日期：2026-03-16 | 📖 分类：运动健康类</p>
</div>
</div>
<nav class="note-nav"><a href="{data["prev"]}" class="nav-prev">← 《{data["prev_title"]}》</a><a href="../index.html" class="nav-home">📚 书单首页</a><a href="{data["next"]}" class="nav-next">《{data["next_title"]}》 →</a></nav>

<button id="theme-toggle" onclick="toggleTheme()" aria-label="切换主题">🌙</button>
<script>
(function(){{
  var t=localStorage.getItem('theme')||'dark';
  if(t==='light')document.documentElement.setAttribute('data-theme','light');
  function upd(){{var btn=document.getElementById('theme-toggle');if(btn)btn.textContent=t==='light'?'☀️':'🌙';}}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',upd);else upd();
}})();
function toggleTheme(){{
  var r=document.documentElement,cur=r.getAttribute('data-theme')==='light'?'light':'dark';
  var nxt=cur==='light'?'dark':'light';
  nxt==='light'?r.setAttribute('data-theme','light'):r.removeAttribute('data-theme');
  localStorage.setItem('theme',nxt);
  document.getElementById('theme-toggle').textContent=nxt==='light'?'☀️':'🌙';
}}
</script>
</body>
</html>'''
    
    filepath = os.path.join(NOTES_DIR, fname)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ Generated: {fname}")

print(f"\n📊 Generated {len(notes_data)} notes")
