import random
import copy
import re
import gradio as gr
import modules.scripts as scripts
from modules.processing import Processed, process_images


#==============================版本名称=========================================

#脚本名称，这个变量在创建ui界面的代码中会引用
title="江湾湾的漫画剪辑助手1.6"

#版本0：添加基础的按照行数生图功能。(完成)
#版本1：添加并完善全局prompt。
#版本2：添加角色识别替换功能。使用自然语言或prompt设定角色。
#版本3：添加镜头判断功能，并分别添加不同的场景prompt。包括局部特写，上半身近景，全身中景，大场面全景等功能。
#版本4：添加某种主题的各种元素内容。
#版本5：添加类似于文字游戏的功能。

#测试过程中问题积累
#1全景小像素下人物脸部崩坏，最低也应该是无脸


#=============================全局：下拉框参数输入======================================
"""
选择世界观类型
输入：赛博朋克时代
输出：Cyberpunk
"""
age_dict = {
"无": "",

"科幻：蒸汽朋克": "Steampunk",
"科幻：赛博朋克": "Cyberpunk",
"武侠": "Wuxia",
"仙侠": "Xianxia",
"奇幻": "Fantasy",
"欧洲：工业革命": "Industrial Revolution",

"古文明：古希腊": "Ancient Greece",
"古文明：古埃及": "Ancient Egypt",
"中国：港片": "Hong Kong cinema",
"中国：汉": "Han Dynasty",
"日本：戦国時代": "Sengoku Period",

        }
age_list = list(age_dict.keys())  #把字典的key取出来组成一个列表，用于给下拉框选择
def choice_age(key):  #根据选择的key，索取age_dict中的value
    return age_dict.get(key, "")  #根据key找value,如果没有返回空值

#-------------------------------------------------
"""
选择画风
输入："火垂るの墓"
输出：'Isao Takahata'
"""
style_dict = {
        "无": "",
        "古风画风1成熟": "Pan Tianshou",
        "古风画风2艳丽": "Zhu Qizhan",
        "古风画风3简约": "Qi Baishi",
        "古风画风4可爱": "Zhang Daqian",
        "都市画风1时尚": "Henri Matisse",
        "都市画风2欧美": "Georgia O'Keeffe",
        "都市画风3细腻": "Craig Thompson",
        "都市画风4流行": "Henri Matisse",
        "日式恐怖画风": "Junji Ito",
        "小鲜肉都市": "Park Tae-joon",
        "都市恋爱": "Park Ji-min",
        "韩风都市恋爱": "Kim Hyeong-seop",
        "细腻日漫": "Kyoji Asano",
        "都市少男风格": "Carlos Dattoli",
        "都市少女风格": "Kuvshinov Ilya",
        "美式漫画": "Gary Larson, Gerard Houckgeest",
        "国风插画": "Ruan Jia",
        "偏质感": "Paolo Roversi, Cecily Brown",
        "细节色彩": "Andreas Rocha",
        "小林家的龙女仆": "Ryohka",
        "西方魔幻": "Rebecca Guay",
        "末日科幻": "Craig Mullins",
        "Beck": "Osamu Kobayashi",
        "浪客剑心": "Ryoichi Ikegami",
        "死神": "Tite Kubo",
        "进击的巨人": "Hajime Isayama",
        "你的名字": "Makoto Shinkai",
        "美少女战士": "Naoko Takeuchi",
        "只有我能进入的隐藏迷宫": "Koyori",
        "时之歌、未来的未来": "Mamoru Hosoda",
        "龙珠": "Akira Toriyama",
        "犬夜叉、美少女战士": "Rumiko Takahashi",
        "新世纪福音战士": "Hideaki Anno",
        "龙猫、千与千寻": "Hayao Miyazaki",
        "借物少女艾莉緹": "Hiromasa Yonebayashi",
        "魔女宅急便": "Kazuo Oga",
        "声之形、春物": "Naoko Yamada",
        "Code Geass 反叛的鲁路修": "Takahiro Kimura",
        "火影忍者": "Masashi Kishimoto",
        "白雪公主与七个小矮人": "Walt Disney",
        "海底总动员": "John Lasseter",
        "魔发奇缘": "Tim Burton",
        "美女与野兽": "Glen Keane",
        "星球大战：克隆人战争": "Genndy Tartakovsky",
        "汤姆猫和杰瑞鼠": "Chuck Jones",
        "火垂るの墓": "Isao Takahata",
        }
style_list=list(style_dict.keys()) #把字典的key取出来组成一个列表，用于给下拉框选择
def choice_style(key):#根据选择的key，索取style_dict中的value
    return style_dict.get(key,"")#根据key找value,如果没有返回空值

#-----------------------------------------
"""
选择绘画方式
输入：彩色动画模式
输出：(( Animated Movies ))
"""
paint_dict = {
"无": "",

"黑白漫画": "((Black and white manga, story page, monochrome mode)),(Black hair)",
"彩色漫画":"((Color Japanese manga, story page, color mode)), (Color storyboard comic)",
"素描模式": "(monochrome  Drawing Sketch Wallpaper:1.5)",
"水彩模式": "(Watercolor wallpaper:1.2)",
"彩色动画模式": "(( Animated Movies ))",
"插画模式": "(masterpiece, best quality)",
"电影模式": "(Cinematic shot, cinematic texture)",
"游戏立绘模式": "(Game vertical drawing,(Solid black background:1.3)，Colorful clothes)",
"像素模式": "(Pixel Art，2D， Solid black background ，solo:1.4)",
"图标模式": "(icon:1.5)",
                }
paint_list=list(paint_dict.keys()) #把字典的key取出来组成一个列表，用于给下拉框选择
def choice_paint(key):#根据选择的key，索取paint_dict中的value，用于绘画prompt
    return paint_dict.get(key,"")#根据key找value,如果没有返回空值
#------------------------------------------------------------------------------
"""
选择光线
输入：正面视角
输出：pov
"""
light_dict = {
"无":"",

"正面光": "frontlighting",
"实体化阴影": "realistic shadows",
"漫射光": "diffuse light",
"边缘照明，效果很不错": "Rim Lighting",
"有氛围感的": "atmospheric",
"戏剧性的阴影": "dramatic shadows"
}
light_list = list(light_dict.keys())  #把字典的key取出来组成一个列表，用于给下拉框选择
def choice_light(key):  #根据选择的key，索取age_dict中的value
    return light_dict.get(key, "")  #根据key找value,如果没有返回空值

#=============================全局：滑条参数输入==============================================
"""
调整画面气氛
大于0是阳光，小于0是恐怖

in 0
out ""

in 2
out '((Sunshine, optimistic visuals,))'

in -2
out (((Horror, gloomy visuals),))'
"""
def choice_aura(Int):
    if Int == 0:
        return ""
    elif Int < 0:
        return '(' * abs(Int) + '(Horror, gloomy visuals,)' + ')' * abs(Int)
    else:
        return '(' * Int + 'Sunshine, optimistic visuals,' + ')' * Int

#-------------------------------------------------------------------------

"""
控制写实成度，大于0写实，小于0卡通

输入0
输出""

输入1
输出(Realistic style,)

输入-1
输出((Cute art style),)
"""
def choice_realistic(Int):
    if Int == 0:
        return ""
    elif Int < 0:
        return '(' * abs(Int) + '(Cute art style,)' + ')' * abs(Int)
    else:
        return '(' * Int + 'Realistic style,' + ')' * Int

#------------------------------------------------------------------------
"""
彩色与单色控制
输入0
输出""

输入2
输出((colorful))

输入-2
输出((Monochromatic mode))
"""
def choice_colour(Int):
    if Int == 0:
        return ""
    elif Int < 0:
        return '(' * abs(Int) + 'Monochromatic mode,' + ')' * abs(Int)
    else:
        return '(' * Int + 'colorful,' + ')' * Int

#==============================场景：下拉框=============================================
"""
选择构图
输入：正面视角
输出：pov
"""
compose_dict = {
"无":"",
"随机":"c",

"电影取景构图": "cinematic angle",
"仰视构图": "from below",
"斜视": "from above",
"全身拍摄": "full-body shot",
"脸部特写": "extreme close up",
"转头斜视图": "frontal view",
"背影像": "back",
"正面视角": "pov",
"人物从高处往下看": "from below",
"低角度拍摄": "low angle shot",
"第三人称视角": "Third-person view",
"逆光剪影": "silhouette"
}
compose_list = list(compose_dict.keys())  #把字典的key取出来组成一个列表，用于给下拉框选择
def choice_compose(key):  #根据选择的key，索取age_dict中的value
    if key=="随机":
        key=random.choice(compose_list) #如果随机，让key随机等于选择列表中的一个值
        return compose_dict.get(key, "") #根据key找value,如果没有返回空值

    return compose_dict.get(key, "")  #根据key找value,如果没有返回空值

#----------------------------------------------------------------
"""
选择特效
输入：运动相机
输出：go pro style
"""
effect_dict = {
"无":"",
"随机":"e",

"突出画面主体": "clear focus",
"运动相机": "go pro style",
"摄像机动态角度": "dynamic angle",
"锐利的焦点": "sharp focus",
"背景虑化": "deep focus",
"景深特写": "depth of field",
"鱼眼镜头": "fish eye shot",
"超透视": "hyperfocal",
"动做镜头": "action shot",
"模糊背景": "blurred background",
}
effect_list = list(effect_dict.keys())  #把字典的key取出来组成一个列表，用于给下拉框选择
def choice_effect(key):  #根据选择的key，索取age_dict中的value
    if key=="随机":
        key=random.choice(effect_list) #如果随机，让key随机等于选择列表中的一个值
        return effect_dict.get(key, "") #根据key找value,如果没有返回空值

    return effect_dict.get(key, "")  #根据key找value,如果没有返回空值

#----------------------------------------------------------------


#===============================场景：滑条============================================


#===============================剧本切分========================================


#===============================剧本数据处理========================================
"""
作用：去除多余的逗号，
输入：a, , ,b,c, , ,d
输出：a,b,c,d
"""
def Remove_comma(string):
    pattern = r',+(\s*,+)*'# 定义匹配模式，匹配连续的逗号及其后面的空格和逗号
    string = re.sub(pattern, ',', string)# 使用正则表达式将匹配到的连续逗号替换为一个逗号
    pattern = r'\s+,'# 定义匹配模式，匹配逗号前面的空格和逗号
    return re.sub(pattern, ',', string)# 使用正则表达式将匹配到的逗号前面的空格替换为逗号，即去除空格


#==========================分割线，以下会定义脚本内容====================================

# 定义脚本
class Script(scripts.Script):
    #=============================定义标题=======================================
    def title(self):
        return title

    #===============================定义界面=======================================
    # 备注：中文要加入【】，否则会有一些变量不会生效，经过大量试错，但不知道为什么
    def ui(self, is_img2img):

        # 以下是小说全局参数
        # 下拉框：时代背景
        # 下拉框：作品画风
        # 下拉框：绘画方式
        # 滑条：阴郁-画面气氛-阳光
        # 滑条：Q版-写实程度-真实
        # 滑条：单色-颜色-多色

        with gr.Row():  # 创建一个横幅，包括3个下拉框
            age = gr.Dropdown(label="【世界观类型】",choices=age_list,elem_id=self.elem_id("age"),)
            style = gr.Dropdown(label="【画风】",choices=style_list,elem_id=self.elem_id("style"),)
            paint = gr.Dropdown(label="【绘画方式】",choices=paint_list,elem_id=self.elem_id("paint"),)

        with gr.Row():  # 创建一个横幅，包括3个下拉框
            light = gr.Dropdown(label="【光影】",choices=light_list,elem_id=self.elem_id("light"),)


        with gr.Row():  # 创建一个横幅，包括3个滑条
            aura = gr.Slider(minimum=-5,maximum=5,step=1,label="【阴郁--画面气氛--阳光】",value=0,elem_id=self.elem_id("aura"),)
            realistic = gr.Slider(minimum=-5,maximum=5,step=1,label="【Q版--写实程度--真实】",value=0,elem_id=self.elem_id("realistic"),)
            colour = gr.Slider(minimum=-5,maximum=5,step=1,label="【单色--颜色--多色】",value=0,elem_id=self.elem_id("colour"),)

        #全局正负提示词
        positive_prompt = gr.Textbox(label="全局正面提示词", value=" ", lines=2,elem_id=self.elem_id("positive_prompt"))
        negative_prompt = gr.Textbox(label="全局负面提示词", value=" ", lines=2,elem_id=self.elem_id("negative_prompt"))



        # 以下是小说单场景参数
        # 下拉框：构图
        # 下拉框：特效
        # 下拉框：光线
        # 勾选：随机：表情
        # 勾选：随机：全身动作
        # 勾选：随机：小动作
        # 滑条：鱼眼透视强度
        # 滑条：动态感强度
        # 滑条：景深-模糊-运动
        # 滑条：近景-镜头距离-全景

        with gr.Row():  # 创建一个横幅，包括3个下拉框
            compose = gr.Dropdown(label="【每场构图】", choices=compose_list, elem_id=self.elem_id("compose"), )
            effect = gr.Dropdown(label="【每场镜头特效】", choices=effect_list, elem_id=self.elem_id("effect"), )


        with gr.Row():  # 创建一个横幅，包括3个勾选
            emote = gr.Checkbox(label="【随机：表情】", value=False, display="inline", elem_id=self.elem_id("emote"), )
            action = gr.Checkbox(label="【随机：全身动作】", value=False, display="inline", elem_id=self.elem_id("action"), )
            body = gr.Checkbox(label="【随机：小动作】", value=False, display="inline", elem_id=self.elem_id("body"), )

        with gr.Row():  # 创建一个横幅，包括2个滑条
            perspective = gr.Slider(minimum=0, maximum=5, step=1, label="【鱼眼透视强度】", elem_id=self.elem_id("perspective"), )
            dynamic = gr.Slider(minimum=0, maximum=5, step=1, label="【动态感强度】", elem_id=self.elem_id("dynamic"), )
        with gr.Row():  # 创建一个横幅，包括2个滑条
            depth = gr.Slider(minimum=-5, maximum=5, step=1, label="【景深--模糊--动态】", value=0, elem_id=self.elem_id("depth"))
            distance = gr.Slider(minimum=-5, maximum=5, step=1, label="【近景--镜头距离--全景】", value=0,elem_id=self.elem_id("distance"))

        # 剧本
        # 剧本输入
        text = gr.Textbox(label="输入剧本，分行输入，每行对应一张图，支持输入中文和英文",value=" ", lines=5, elem_id=self.elem_id("text"))
        # 如果输入一大坨没分行的内容，是否开启智能分割
        with gr.Row():# 创建一个横幅，包括1个勾选，1个分割长度
            split= gr.Checkbox(label="是否开启智能分行", value=False, display="inline", elem_id=self.elem_id("split"))
            split_length = gr.Slider(minimum=70, maximum=360, step=5, label='每张图对应的剧本长度', value=170,elem_id=self.elem_id("split_length"))
            split_random = gr.Slider(minimum=1, maximum=60, step=1, label='智能分割长度差异', value=30, elem_id=self.elem_id("split_random"))

        # 角色指定
        # 文本输入框
        with gr.Row():  # 创建一个横幅，包括2个文本输入框
            r1=gr.Textbox(label="角色1描述(自然语言输入)", value="AA = 18岁黑色哥特短裙萝莉", lines=2,elem_id=self.elem_id("r1"))
            r2=gr.Textbox(label="角色2描述(自然语言输入)", value=" ", lines=2,elem_id=self.elem_id("r2"))
        with gr.Row():  # 创建一个横幅，包括2个文本输入框
            r3=gr.Textbox(label="角色3描述(prompt输入)", value= "CC = (1 boy:1.1),<lora:CC：1>", lines=2,elem_id=self.elem_id("r3"))
            r4=gr.Textbox(label="角色4描述(prompt输入)", value=" ", lines=2,elem_id=self.elem_id("r4"))

        return [
            #全局参数：
            age,style,paint,#下拉框
            light,#下拉框
            aura,realistic,colour,#滑条
            positive_prompt,#文本
            negative_prompt,#文本
            #场景参数：
            compose,effect,#下拉框
            emote,action,body,#勾选
            perspective,dynamic,#滑条
            depth,distance,#滑条
            #剧本参数：
            text,#文本，剧本输入
            split,#勾选，是否开启智能分割
            split_length,#滑条，分行长度
            split_random,#滑条，分行长度差异
            #角色参数：
            r1,r2,#文本
            r3,r4,#文本
            ]

    #=========================定义运行函数====================================
    #接收参数
    def run(self, p,
            # 全局参数：
            age: str, style: str, paint: str,  # 下拉框str
            light:str, # 下拉框str
            aura: int, realistic: int, colour: int,  # 滑条int
            positive_prompt: str,  # 文本str
            negative_prompt: str,  # 文本str
            # 场景参数：
            compose:str, effect:str,  # 下拉框
            emote: bool, action: bool, body: bool,  # 勾选bool
            perspective: int, dynamic: int,  # 滑条int
            depth: int, distance: int,  # 滑条int
            # 剧本参数：
            text: str,  # 文本str
            split: bool,  # 勾选bool
            split_length: int,  # 滑条int
            split_random,  # 滑条int
            # 角色参数：
            r1: str, r2: str,  # 文本str
            r3: str, r4: str,  # 文本str
            ):

        # ======================自动获取str剧本格式================================
        print("text原文本已收到")
        # ========================翻译为英文=====================================

        # ========================分行：剧本str格式，并转换为list格式==================
        split_length = split_length + random.randint(-split_random, split_random)  # 根据随机加减分割长度
        if split:  # 如果勾选智能分行
            # 暂时还没写怎么智能分行
            lines = [x.strip() for x in text.split('\n') if x.strip()]  # 按照回车分行，去除空行。输入str，返回list
        else:  # 如果没有勾选智能分行
            lines = [x.strip() for x in text.split('\n') if x.strip()]  # 按照回车分行，去除空行。输入str，返回list
            #如果多分出一行，或分行出现错误，只有可能是这里分行出错导致的


        lines = [x for x in lines if len(x) > 0]  # 过滤列表中长度为零的元素

        print(len(lines))#打印任务长度
        """
        剧本分行
        输入：分好行的str
        text = "Line 1,Line 2,Line 3"
        输出：列表lines
        lines = ["Line 1",
                "Line 2",
                "Line 3"]
        """
        # ======================添加全局提示词===============================
        # 根据参数设置获取提示词
        age_1 = choice_age(age)#时代背景世界观
        style_1 = choice_style(style)#画风
        paint_1 = choice_paint(paint)#绘画方式

        light_1=choice_light(light)#光影

        aura = choice_aura(aura)  # 画面气氛
        realistic = choice_realistic(realistic)  # 写实程度
        colour = choice_colour(colour)  # 画面色彩

        # 汇总所有提示词，形成全局正面提示词
        overall_style = positive_prompt + ',' + age_1 + ',' + style_1 + ',' + paint_1 + ',' + light_1 + ',' +aura + ',' + realistic + ',' + colour

        # 添加全局正面提示词
        li = []
        for line in lines:  # 逐行读取
            args = {}
            args["prompt"] = line + "," + overall_style  # 单一画面描述 + 画风描述
            li.append(args)
        """
        输入：
        lines = ["Line 1",
                 "Line 2",
                 "Line 3"]
        输出：li
        [{'prompt': '剧本第一行 AA BB“hello” p p p p,,,,,,,  ,  全局正面提示词'},
        {'prompt': '剧本第二行,  全局正面提示词'},
        {'prompt': '剧本第三行,  全局正面提示词'}]
        """
        # ====================汇总并添加全局正负提示词==============================
        jobs = []
        for line in li:  # 逐行读取

            args = line
            args["negative_prompt"] = negative_prompt  # 全局负面提示词
            args["batch_size"] = 1  # int数值类型  batch size
            jobs.append(args)
        """
        输入：列表li
        [{'prompt': '剧本第一行 AA BB“hello” p p p p,,,,,,,  ,  全局正面提示词'},
        {'prompt': '剧本第二行,  全局正面提示词'},
        {'prompt': '剧本第三行,  全局正面提示词'}]

        输出：列表jobs，每一行代表一张图
        [{'prompt': '剧本第一行 AA BB“hello” p p p p,,,,,,,  ,  全局正面提示词','negative_prompt': '全局负面提示词','batch_size': 1},
        {'prompt': '剧本第二行,  全局正面提示词', 'negative_prompt': '全局负面提示词', 'batch_size': 1},
        {'prompt': '剧本第三行,  全局正面提示词', 'negative_prompt': '全局负面提示词', 'batch_size': 1}]
        """
        # ======================开始逐行处理数据===================================
        images = []
        all_prompts = []
        infotexts = []
        p.seed = -1

        for args in jobs:  # 开启循环：遍历每一个分句的所有内容
            # ======================添加局部场景内提示词============================
            compose_1 = choice_compose(compose)#每场构图
            effect_1 = choice_effect(effect)#每场镜头特效


            args["prompt"] = args["prompt"]+ ',' +compose_1+ ',' +effect_1+ ','


            # =======================剧本数据处理=================================
            args["prompt"] = Remove_comma(args["prompt"])  # 去掉多余的逗号，多余的逗号会造成出现畸形

            # ======================发起作图=====================================
            copy_p = copy.copy(p)
            for k, v in args.items():
                setattr(copy_p, k, v)
            proc = process_images(copy_p)
            images += proc.images

        return Processed(p, images, p.seed, "", all_prompts=all_prompts, infotexts=infotexts)






