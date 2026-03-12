#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final script to rename all note files in the notes directory to English filenames
This will fix the 404 issues on GitHub Pages
"""

import os
import shutil
from pathlib import Path

def create_english_filename(chinese_title):
    """Convert Chinese book titles to English filenames"""
    # Mapping of Chinese titles to English filenames
    title_mapping = {
        "文明的故事": "civilization.html",
        "伊利亚特": "iliad.html",
        "通往奴役之路": "road-to-serfdom.html",

        # Self-improvement classics
        "思考，快与慢": "think-fast-slow.html",
        "思考 快与慢": "think-fast-slow.html",
        "思考的艺术": "thinking-art.html",
        "原则": "principles.html",
        "原子习惯": "atomic-habits.html",
        "深度工作": "deep-work.html",
        "刻意练习": "deliberate-practice.html",
        "高效能人士的七个习惯": "seven-habits.html",
        "被讨厌的勇气": "unliked-courage.html",
        "非暴力沟通": "nonviolent-communication.html",
        "心流": "flow.html",
        "影响力": "influence.html",
        "系统思考": "systems-thinking.html",
        "系统之美": "systems-beauty.html",
        "认知天性": "cognitive-nature.html",
        "认知觉醒": "cognitive-awareness.html",
        "终身成长": "lifelong-growth.html",
        "跃迁": "transition.html",
        "远见": "vision.html",
        "精进": "mastery.html",
        "执行": "execution.html",
        "学习之道": "learning-path.html",
        "如何阅读一本书": "how-read-book.html",
        "如何高效学习": "efficient-learning.html",
        "学会提问": "ask-questions.html",
        "反脆弱": "anti-fragile.html",
        "反直觉思考": "intuition-thinking.html",
        "习惯的力量": "power-of-habits.html",
        "掌控习惯": "master-habits.html",
        "掌控时间": "time-management.html",
        "精力管理": "energy-management.html",
        "时间管理": "time-management.html",
        "番茄工作法": "pomodoro-method.html",
        "拖延心理学": "procrastination-psychology.html",
        "奇特的一生": "strange-life.html",

        # Business & Innovation
        "从0到1": "from-zero-one.html",
        "精益创业": "lean-startup.html",
        "创新者的窘境": "innovators-dilemma.html",
        "定位": "positioning.html",
        "增长黑客": "growth-hackers.html",
        "商业模式": "business-model.html",
        "商业模式新生代": "business-model-new-generation.html",
        "创业维艰": "startup-hardship.html",
        "重新定义公司": "reimagine-company.html",
        "创新者": "innovators.html",
        "颠覆创新": "disruptive-innovation.html",
        "创业": "entrepreneurship.html",
        "商业": "business-strategy.html",

        # Psychology & Philosophy
        "心理学": "psychology.html",
        "心理学与生活": "psychology-life.html",
        "津巴多": "zimbardo.html",
        "社会心理学": "social-psychology.html",
        "社会性动物": "social-animals.html",
        "亲密关系": "close-relationships.html",
        "梦的解析": "dream-analysis.html",
        "路西法效应": "lucifer-effect.html",
        "操纵心理学": "psychological-manipulation.html",
        "幸福的婚姻": "happy-marriage.html",
        "正面管教": "positive-discipline.html",
        "如何说孩子才会听": "talk-kids.html",
        "爱的五种语言": "five-languages-love.html",
        "养育": "parenting.html",
        "父母": "parents.html",
        "稀缺": "scarcity.html",
        "自卑与超越": "self-esteem-superiority.html",
        "自卑": "self-esteem.html",
        "自我": "self.html",
        "人格": "personality.html",
        "情绪": "emotions.html",
        "意志力": "willpower.html",
        "自控力": "self-control.html",
        "少有人走的路": "few-roads.html",
        "学会提问": "critical-thinking.html",
        "清醒思考": "conscious-thinking.html",
        "清醒思考的艺术": "art-of-conscious-thinking.html",
        "掌控习惯": "master-habits.html",

        # Investment & Finance
        "投资": "investment.html",
        "聪明的投资者": "smart-investor.html",
        "穷查理宝典": "buffett-principles.html",
        "巴菲特": "buffett.html",
        "原则": "principles.html",
        "证券分析": "security-analysis.html",
        "漫步华尔街": "wall-street.html",
        "投资最重要的事": "important-investments.html",
        "随机漫步的傻瓜": "random-walk.html",
        "非理性繁荣": "irrational-exuberance.html",
        "估值": "valuation.html",
        "指数基金": "index-funds.html",
        "资产配置": "asset-allocation.html",
        "财务自由": "financial-freedom.html",
        "穷爸爸富爸爸": "rich-dad-poor-dad.html",
        "小狗钱钱": "little-money-dog.html",
        "纳瓦尔宝典": "navarro-principles.html",
        "金钱心理学": "money-psychology.html",
        "思考致富": "think-rich.html",
        "芒格": "munger.html",
        "慢慢变富": "slow-wealth.html",
        "有钱人": "rich-thinking.html",
        "富有的习惯": "rich-habits.html",
        "贫穷的本质": "poverty-depth.html",
        "钱从哪里来": "wealth-source.html",
        "你的第一本理财书": "first-finance-book.html",

        # Biography & Leadership
        "传记": "biography.html",
        "美国恺撒": "american-caesar.html",
        "十二位对抗诸神的人": "twelve-defying-gods.html",
        "成吉思汗": "genghis-khan.html",
        "富兰克林自传": "benjamin-franklin.html",
        "苏东坡": "su-dongpo.html",
        "曾国藩": "confucius.html",
        "乔布斯": "jobs.html",
        "马斯克传": "elon-musk.html",
        "毛选": "mao-selections.html",
        "稻盛和夫": "kazuo-ishikawa.html",
        "贝索斯": "jeff-bezos.html",
        "甘地自传": "gandhi.html",
        "曼德拉传": "nelson-mandela.html",
        "曹操": "caocao.html",
        "褚时健": "du-shijian.html",
        "张居正": "zhang-juzheng.html",
        "左宗棠": "zuozongtang.html",
        "袁隆平": "yuan-longping.html",
        "居里夫人传": "marie-curie.html",
        "海伦凯勒": "helen-keller.html",
        "苏格拉底": "socrates.html",

        # Art & Aesthetics
        "艺术": "art.html",
        "吴哥之美": "anguo-beauty.html",
        "艺术的故事": "art-story.html",
        "美的历程": "beauty-history.html",
        "谈美": "discussing-beauty.html",
        "观看之道": "viewing-ways.html",
        "艺术精神": "art-spirit.html",

        # Philosophy & Religion
        "哲学": "philosophy.html",
        "宗教": "religion.html",
        "纯粹理性批判": "critique-rational.html",
        "存在与时间": "being-time.html",
        "查拉图斯特拉如是说": "thus-spoke-zarathustra.html",
        "禅与摩托车维修艺术": "zen-motorcycle.html",
        "悉达多": "siddhartha.html",
        "心经": "heart-sutra.html",
        "蒙田随笔": "montaigne-essays.html",
        "黄庭经": "yellow-court.html",
        "太上感应篇": "taishang-inductions.html",
        "庄子": "zhuangzi.html",
        "周易参同契": "talisman-hexagram.html",
        "抱朴子内篇": "baopu-zi-inner.html",
        "养生延命录": "prolonging-life.html",
        "太乙金华宗旨": "golden-prescription.html",
        "云笈七签": "seven-signs.html",
        "性命圭旨": "guizhi.html",
        "乐育堂语录": "joyful-classroom.html",
        "炁体源流": "qi-body-source.html",
        "礼记·月令": "monthly-commandments.html",
        "黄帝内经": "yellow-emperor.html",
        "千金方": "thousand-gold.html",
        "本草纲目": "bencaogen.html",
        "遵生八笺": "eight-fold-note.html",
        "丹道法诀": "dan-dao-methods.html",
        "道的呼吸": "dao-breathing.html",
        "道家养生学": "daojia-health.html",
        "道教与养生": "dao-medicine.html",
        "道医学": "dao-medicine.html",
        "金花的秘密": "secret-golden.html",
        "马王堆房中术": "warring-states-sexual.html",
        "容成阴道": "rongcheng-vagina.html",
        "养性延命录·御女损益篇": "nurture-extension.html",
        "素女经": "plain-woman.html",
        "洞玄子": "dunhuang.html",
        "房中补益": "benefits-sex.html",
        "三元延寿参赞书": "three-yuan-extend.html",
        "遵生八笺·延年却病笺": "eight-fold-note-prevent.html",
        "摄生总要": "collective-health.html",
        "道教与性": "daoism-sex.html",
        "中国古代房内考": "ancient-chinese-sexual.html",
        "道家性养生研究": "daojia-sex-health.html",
        "性理学": "sexual-philosophy.html",
        "悟真篇": "wisdom-tan.html",
        "无根树词": "tree-without-root.html",
        "钟吕传道集": "zhonglü-transmit.html",
        "方壶外史": "fanghu-wai-shi.html",
        "道窍谈": "dao-qiao-talk.html",
        "三车秘旨": "three-car-secret.html",
        "金丹真传": "true-golden.html",
        "大成捷要": "great-completion.html",
        "青娥功": "blue-eyed-girl.html",
        "道教南宗与双修": "daoist-south-school.html",
        "与塞涅卡共进早餐": "stoicism.html",

        # Literature & Fiction
        "百年孤独": "one-hundred-years-solitude.html",
        "1984": "nineteen-eighty-four.html",
        "红楼梦": "dream-of-red-chamber.html",
        "悲惨世界": "les-miserables.html",
        "罪与罚": "crime-punishment.html",
        "简·爱": "jane-eyre.html",
        "傲慢与偏见": "pride-prejudice.html",
        "呼啸山庄": "wuthering-heights.html",
        "双城记": "tale-two-cities.html",
        "老人与海": "old-man-sea.html",
        "了不起的盖茨比": "great-gatsby.html",
        "麦田里的守望者": "catcher-rye.html",
        "堂吉诃德": "don-quixote.html",
        "变形记": "metamorphosis.html",
        "安娜·卡列尼娜": "anna-karenina.html"
    }

    # Try exact match first
    if chinese_title in title_mapping:
        return title_mapping[chinese_title]

    # Try partial match
    for chinese, english in title_mapping.items():
        if chinese in chinese_title or chinese_title in chinese:
            return english

    # Fallback: convert Chinese characters to pinyin-like format
    fallback_name = chinese_title.replace(" ", "-").replace(",", "").replace(".", "")
    fallback_name = fallback_name.replace("·", "-").replace("、", "-")
    fallback_name = ''.join(c for c in fallback_name if ord(c) < 256)  # Keep only ASCII chars
    return f"{fallback_name}.html" if not fallback_name.endswith('.html') else fallback_name

def main():
    notes_dir = Path("notes")
    if not notes_dir.exists():
        print("ERROR: notes directory not found!")
        return

    print(f"Finding {len(list(notes_dir.glob('*.html')))} HTML files in notes directory")

    renamed_count = 0
    errors = []

    # Get all HTML files
    html_files = list(notes_dir.glob("*.html"))
    html_files.sort()  # Sort for consistent processing

    for old_file in html_files:
        # Extract title from filename (remove .html and any numbers/suffixes)
        base_name = old_file.stem
        if not base_name:
            continue

        # Remove trailing numbers and spaces
        clean_title = base_name.rstrip(" 0123456789")
        if clean_title == base_name:
            clean_title = base_name.rstrip()

        if not clean_title:
            continue

        # Create new English filename
        new_filename = create_english_filename(clean_title)

        # Ensure we don't overwrite existing files
        final_new_filename = new_filename
        counter = 1
        while (notes_dir / final_new_filename).exists():
            name, ext = os.path.splitext(new_filename)
            final_new_filename = f"{name}_{counter}{ext}"
            counter += 1

        try:
            new_path = notes_dir / final_new_filename
            old_path = notes_dir / old_file.name

            # Rename the file
            shutil.move(str(old_path), str(new_path))
            print(f"Renamed: {old_file.name} -> {final_new_filename}")
            renamed_count += 1

        except Exception as e:
            error_msg = f"Failed to rename {old_file.name}: {str(e)}"
            print(error_msg)
            errors.append(error_msg)

    print(f"\nRenaming complete!")
    print(f"Summary:")
    print(f"  Total files processed: {len(html_files)}")
    print(f"  Successfully renamed: {renamed_count}")
    print(f"  Errors: {len(errors)}")

    if errors:
        print(f"\nErrors encountered:")
        for error in errors:
            print(f"  {error}")

if __name__ == "__main__":
    main()