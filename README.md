# astrbot-plugin-githubweekly

正确操作应该是像这个插件一样使用命令来进行操作,,而不是像上一个插件进行消息拦截从而获取到开头的命令,
使用命令的逻辑也许是astrbot会自动进行一次消息拦截然后进行命令解析,然后根据命令进行操作,

获取 GitHub 最近一周的热门项目。

目标：在Astrbot中创建一个自动获取和展示GitHub热点项目的插件

fork一下astrbot的插件模板项目,然后在此基础上修改,添加的功能,
能够定时主动给我发周报,(之前没有设计过这个功能,)
可以选择对话账号进行选择性发送,
发送命令,接收命令然后发送周报,
`/githubweekly latest`（获取最新周报）
`/githubweekly list [N]`（列出往期）
`/githubweekly read [N]`（查看指定周报）
`/githubweekly github`（给出链接进入信息源的项目仓库）
信息源的项目仓库:https://github.com/itcoffee66/githubweekly,其中有md格式的文本文档,
https://github.com/itcoffee66/githubweekly/blob/main/_weekly/100.md

使用 RSS 订阅软件可以快速知道本周 GitHub 热点项目
订阅地址：[https://itcoffee66.github.io/githubweekly/feed.xml](https://itcoffee66.github.io/githubweekly/feed.xml)
RSS里面给出的链接是:https://itcoffee66.github.io/githubweekly/96.html,即他人的thml界面,

关于api,多去查看astrbot的源码

先只实现前两个命令,`/githubweekly latest`（获取最新周报）`/githubweekly list [N]`（列出往期）直接从rss订阅里面取出来相关链接,然后将对应的html链接发送给用户即可,或者参考现成RSS订阅软件,开源项目之类的
注意要实现简单的文件缓存，避免每次命令都请求网络,导致响应时间过长,
feedparser（第三方库，更简单）
xml.etree.ElementTree（Python标准库，无需额外依赖）
每天中文十二点推送消息给我,插件内定时（依赖Astrbot运行稳定性）
main中已经存在了一个基本的指令模板,根据模板为我编写新的指令,
为我适时的编写用于logger的信息,

主动消息指的是机器人主动推送消息。某些平台可能不支持主动消息发送。
如果是一些定时任务或者不想立即发送消息，可以使用 event.unified_msg_origin 得到一个字符串并将其存储，然后在想发送消息的时候使用 self.context.send_message(unified_msg_origin, chains) 来发送消息。
from astrbot.api.event import MessageChain
@filter.command("helloworld")
async def helloworld(self, event: AstrMessageEvent):
    umo = event.unified_msg_origin
    message_chain = MessageChain().message("Hello!").file_image("path/to/image.jpg")
    await self.context.send_message(event.unified_msg_origin, message_chain)
通过这个特性，你可以将 unified_msg_origin 存储起来，然后在需要的时候发送消息。

插件存储
简单 KV 存储
插件可以使用 AstrBot 提供的简单 KV 存储功能来存储一些配置信息或临时数据。该存储是基于插件维度的，每个插件有独立的存储空间，互不干扰。
class Main(star.Star):
    @filter.command("hello")
    async def hello(self, event: AstrMessageEvent):
        """Aloha!"""
        await self.put_kv_data("greeted", True)
        greeted = await self.get_kv_data("greeted", False)
        await self.delete_kv_data("greeted")
存储大文件规范
为了规范插件存储大文件的行为，请将大文件存储于 data/plugin_data/{plugin_name}/ 目录下。
你可以通过以下代码获取插件数据目录：
from astrbot.core.utils.astrbot_path import get_astrbot_data_path
plugin_data_path = get_astrbot_data_path() / "plugin_data" / self.name # self.name 为插件名称



第二步`/githubweekly MDlatest`（获取最新周报）`/githubweekly MDlist [N]`（列出往期）,从md文件中读取内容,得到仓库内的图片,然后清洗md格式,只保留文本内容和换行(保持排版清晰方便看),

第三步,`/githubweekly MYlatest`（获取最新周报）`/githubweekly MYlist [N]`（列出往期）学习做一个爬虫类似程序(还要学习如何实现),自动获取每周排行榜,每周star数量增长榜(有待添加更多目标)等信息,将相关数据进行数据库式的存储

# rss的xml文件

<feed xmlns="http://www.w3.org/2005/Atom">
<id>https://itcoffee66.github.io/githubweekly/</id>
<title>Github Weekly</title>
<subtitle>每周分享GitHub热门开源项目，涵盖AI、开发工具、框架等领域。 B站、YouTube同步发布视频版本，搜：IT咖啡馆</subtitle>
<updated>2026-03-19T01:43:10+08:00</updated>
<author>
<name>IT咖啡馆</name>
<uri>https://itcoffee66.github.io/githubweekly/</uri>
</author>
<link rel="self" type="application/atom+xml" href="https://itcoffee66.github.io/githubweekly/feed.xml"/>
<link rel="alternate" type="text/html" hreflang="zh-CN" href="https://itcoffee66.github.io/githubweekly/"/>
<generator uri="https://jekyllrb.com/" version="4.4.1">Jekyll</generator>
<rights> © 2026 IT咖啡馆 </rights>
<icon>/githubweekly/assets/img/favicons/favicon.ico</icon>
<logo>/githubweekly/asset/it-coffee-circle.png</logo>
<entry>
<title>GitHub一周热点第106期</title>
<link href="https://itcoffee66.github.io/githubweekly/106.html" rel="alternate" type="text/html" title="GitHub一周热点第106期"/>
<published>2026-03-07T00:00:00+08:00</published>
<updated>2026-03-07T00:00:00+08:00</updated>
<id>https://itcoffee66.github.io/githubweekly/106.html</id>
<content type="text/html" src="https://itcoffee66.github.io/githubweekly/106.html"/>
<author>
<name>IT咖啡馆</name>
</author>
<summary>阿里的openclaw替代、WiFi 感知人体活动、实时全球情报监控、代码仓库生成知识图谱和字节的多智能体框架</summary>
</entry>
<entry>
<title>GitHub 一周热点第 105 期</title>
<link href="https://itcoffee66.github.io/githubweekly/105.html" rel="alternate" type="text/html" title="GitHub 一周热点第 105 期"/>
<published>2026-02-28T00:00:00+08:00</published>
<updated>2026-02-28T00:00:00+08:00</updated>
<id>https://itcoffee66.github.io/githubweekly/105.html</id>
<content type="text/html" src="https://itcoffee66.github.io/githubweekly/105.html"/>
<author>
<name>IT咖啡馆</name>
</author>
<summary>Rust 版 OpenClaw 替代、本地语音克隆工具、Qwen 系列最新模型、AI 渗透测试系统和精美源码图片生成工具</summary>
</entry>
<entry>
<title>GitHub一周热点第104期</title>
<link href="https://itcoffee66.github.io/githubweekly/104.html" rel="alternate" type="text/html" title="GitHub一周热点第104期"/>
<published>2026-02-14T00:00:00+08:00</published>
<updated>2026-02-14T00:00:00+08:00</updated>
<id>https://itcoffee66.github.io/githubweekly/104.html</id>
<content type="text/html" src="https://itcoffee66.github.io/githubweekly/104.html"/>
<author>
<name>IT咖啡馆</name>
</author>
<summary>智谱新一代旗舰模型、AI 编码助手配置管理器、AI 渗透测试工具、安全Python 解释器和深度金融研究智能体</summary>
</entry>
<entry>
<title>GitHub一周热点第103期</title>
<link href="https://itcoffee66.github.io/githubweekly/103.html" rel="alternate" type="text/html" title="GitHub一周热点第103期"/>
<published>2026-02-07T00:00:00+08:00</published>
<updated>2026-02-07T00:00:00+08:00</updated>
<id>https://itcoffee66.github.io/githubweekly/103.html</id>
<content type="text/html" src="https://itcoffee66.github.io/githubweekly/103.html"/>
<author>
<name>IT咖啡馆</name>
</author>
<summary>超轻量NanoBot、编程智能体记忆工具Beads、聊天分析ChatLab等</summary>
</entry>
<entry>
<title>GitHub一周热点第102期</title>
<link href="https://itcoffee66.github.io/githubweekly/102.html" rel="alternate" type="text/html" title="GitHub一周热点第102期"/>
<published>2026-01-31T00:00:00+08:00</published>
<updated>2026-01-31T00:00:00+08:00</updated>
<id>https://itcoffee66.github.io/githubweekly/102.html</id>
<content type="text/html" src="https://itcoffee66.github.io/githubweekly/102.html"/>
<author>
<name>IT咖啡馆</name>
</author>
<summary>个人AI助理OpenClaw、React生成视频Remotion、Kimi K2.5开源模型等</summary>
</entry>
<entry>
<title>GitHub一周热点第101期</title>
<link href="https://itcoffee66.github.io/githubweekly/101.html" rel="alternate" type="text/html" title="GitHub一周热点第101期"/>
<published>2026-01-24T00:00:00+08:00</published>
<updated>2026-01-24T00:00:00+08:00</updated>
<id>https://itcoffee66.github.io/githubweekly/101.html</id>
<content type="text/html" src="https://itcoffee66.github.io/githubweekly/101.html"/>
<author>
<name>IT咖啡馆</name>
</author>
<summary>开源版Cowork、数据工程实战课程、浏览器MCP、专业设计agent skill等</summary>
</entry>
<entry>
<title>GitHub一周热点第99期</title>
<link href="https://itcoffee66.github.io/githubweekly/99.html" rel="alternate" type="text/html" title="GitHub一周热点第99期"/>
<published>2026-01-03T00:00:00+08:00</published>
<updated>2026-01-03T00:00:00+08:00</updated>
<id>https://itcoffee66.github.io/githubweekly/99.html</id>
<content type="text/html" src="https://itcoffee66.github.io/githubweekly/99.html"/>
<author>
<name>IT咖啡馆</name>
</author>
<summary>AI编码代理编排平台vibe-kanban、Claude skills、AI生成UI工具A2UI等</summary>
</entry>
<entry>
<title>GitHub一周热点第100期</title>
<link href="https://itcoffee66.github.io/githubweekly/100.html" rel="alternate" type="text/html" title="GitHub一周热点第100期"/>
<published>2026-01-03T00:00:00+08:00</published>
<updated>2026-01-03T00:00:00+08:00</updated>
<id>https://itcoffee66.github.io/githubweekly/100.html</id>
<content type="text/html" src="https://itcoffee66.github.io/githubweekly/100.html"/>
<author>
<name>IT咖啡馆</name>
</author>
<summary>开源AI编程代理OpenCode、AI开发技能框架Superpowers、字节电脑操作Agent等</summary>
</entry>
<entry>
<title>GitHub一周热点第98期</title>
<link href="https://itcoffee66.github.io/githubweekly/98.html" rel="alternate" type="text/html" title="GitHub一周热点第98期"/>
<published>2025-12-20T00:00:00+08:00</published>
<updated>2025-12-20T00:00:00+08:00</updated>
<id>https://itcoffee66.github.io/githubweekly/98.html</id>
<content type="text/html" src="https://itcoffee66.github.io/githubweekly/98.html"/>
<author>
<name>IT咖啡馆</name>
</author>
<summary>腾讯文档理解框架WeKnora、微软TTS框架VibeVoice、Claude记忆插件等</summary>
</entry>
<entry>
<title>GitHub一周热点第97期</title>
<link href="https://itcoffee66.github.io/githubweekly/97.html" rel="alternate" type="text/html" title="GitHub一周热点第97期"/>
<published>2025-12-13T00:00:00+08:00</published>
<updated>2025-12-13T00:00:00+08:00</updated>
<id>https://itcoffee66.github.io/githubweekly/97.html</id>
<content type="text/html" src="https://itcoffee66.github.io/githubweekly/97.html"/>
<author>
<name>IT咖啡馆</name>
</author>
<summary>手机智能助理Open-AutoGLM、AI画架构图工具、AI编码指导agents.md等</summary>
</entry>
<entry>
<title>GitHub一周热点第96期</title>
<link href="https://itcoffee66.github.io/githubweekly/96.html" rel="alternate" type="text/html" title="GitHub一周热点第96期"/>
<published>2025-12-06T00:00:00+08:00</published>
<updated>2025-12-06T00:00:00+08:00</updated>
<id>https://itcoffee66.github.io/githubweekly/96.html</id>
<content type="text/html" src="https://itcoffee66.github.io/githubweekly/96.html"/>
<author>
<name>IT咖啡馆</name>
</author>
<summary>AI绘图模型Flux2、腾讯视频生成HunyuanVideo、AI动态记忆Cognee等开源项目推荐</summary>
</entry>
</feed>

# 周报md格式文档内容的格式

---
title: "GitHub 一周热点第 105 期"
date: "2026-02-28"
description: "Rust 版 OpenClaw 替代、本地语音克隆工具、Qwen 系列最新模型、AI 渗透测试系统和精美源码图片生成工具"
---

## 视频
[本期视频链接](https://www.bilibili.com/video/BV1GkP5zREL7)

GitHub 一周热点第 105 期（2025/2/15 - 2026/2/28），本期内容包括 Rust 编写的 OpenClaw 替代、本地语音克隆工具、Qwen 系列最新模型、AI 渗透测试系统和精美源码图片生成工具。
最后还有 2 份资料分享。
一转眼春节假期就过完了，不知道大家都有没有休息够，已经进入工作状态，还是依然在怀念春节？话不多说，我们进入正式内容。
如果觉得内容不错，别忘了点赞关注支持一下。

## 1. zeroclaw
- 项目名称：zeroclaw – Rust 版 OpenClaw 替代
- 官网链接：https://github.com/zeroclaw-labs/zeroclaw

随着 OpenClaw 红遍了大江南北，现在各路衍生的龙虾也是遍地开花，ZeroClaw 就是 Rust 编写的 OpenClaw 替代，它是一个高性能、低资源占用、可组合的自主智能体运行时。ZeroClaw 是面向 agent 工作流的运行时操作系统 — 它抽象了模型、工具、记忆和执行层，使 agent 可以一次构建、随处运行。

都说 Rust 重写一切，看来 OpenClaw 也没有逃过。与很多基于 Node.js 或 Python 的智能体相比，ZeroClaw 着重性能、模块化设计与安全默认策略。可以看到和 OpenClaw、NanoBot、PicoClaw 的对比上，ZeroClaw 在内存需求、启动速度、包体积方面都有优势，这其实也是依赖于 Rust 自身的优势。

![图片](/asset/post105/1-1.png)

还要说一点就是他的 Trait 驱动的可插拔架构，它通过 Rust 的 trait 接口实现核心系统的模块化：providers、channels、memory、tools 都是可插拔的组件，你可以根据需要去替换。

![图片](/asset/post105/1-2.png)

另外就是它小体积和低消耗的优点，可以更好的在小型设备上发挥。还有就是它强化了安全方面的设计。

ZeroClaw 的形象是一只螃蟹，现在 AI 圈变成一场海鲜大战，螃蟹龙虾大打出手。

## 2. voicebox
- 项目名称：voicebox – 本地语音克隆工具
- 官网链接：https://github.com/jamiepine/voicebox

Voicebox 是本地运行的语音克隆工具。被称为"语音克隆领域的 Ollama"，Voicebox 基于 Qwen3-TTS，仅需几秒钟音频即可克隆任意声音，完全在本地运行。

![图片](/asset/post105/2-1.png)

使用上可以直接在项目的网站下载，根据自己的系统选择版本。Voicebox 可以快速下载语音模型，从几秒钟的音频中克隆任意声音，并使用编辑工具创作多声部项目。而且无需订阅，无需上传云端，语音数据不离开设备，兼顾效果与隐私。

整体来说我觉得它的 UI 做得挺不错的，比用 Streamlit 简单做的 UI 要友好太多了，尤其对于新手上手来说，体验会好很多，除了声音克隆用 Qwen-TTS，还支持使用 Whisper 来做翻译，都可以快速下载模型。

还有一点我非常喜欢的就是它对 Mac 友好，MLX 后端带原生 Metal 加速，苹果芯片的推理速度快 4-5 倍。

前几天评论有说到感觉 Qwen 没什么人用，其实很多的创业和开源项目，背后都选择用 Qwen 的衍生模型，还是很多的。

## 3. Qwen3.5
- 项目名称：Qwen3.5 – Qwen 最新模型
- GitHub 链接：https://github.com/QwenLM/Qwen3.5

今年的过年期间绝对是属于 AI 的，就在除夕当天，Qwen 发布了开源大模型的最新版本 Qwen3.5。

在近期的众多模型中，Qwen3.5 确实是我最关注的，因为在开源领域的影响力 Qwen 确实最大。所以我也第一时间去做了上手测试，相关内容可以参考一下我之前发布的视频内容。

![图片](/asset/post105/3-1.png)

值得注意一点就是 Qwen3.5 是一个原生多模态模型，也就是从训练之初就让视觉与语言在统一表征空间中联合学习，这个也是目前模型发展的一个趋势，在 GUI 理解、视频分析等场景中就可以一模到底了。这次模型采用创新的混合架构，将线性注意力（Gated Delta Networks）与稀疏混合专家（MoE）相结合，力争在能力、速度与成本之间达成一个最优的结果。

除夕当天开源的是 Qwen3.5-397B-A17B，也就是 397B 总参数，激活 17B。属于是旗舰模型体积比较大，本地很难跑。

这周 Qwen3.5 又推出了中等规模模型系列：Qwen3.5-122B-A10B、Qwen3.5-35B-A3B、Qwen3.5-27B 等，这当中尤其是 Qwen3.5-35B-A3B 最被关注，这个大小可以在很多本地和边缘设备上运行了。

![图片](/asset/post105/3-2.png)

那我也简单地在本地使用了一下，比如我之前测试时候那个复现春晚会场的 case，包含了图像理解和编程，结果来说和 QwenChat 上的效果差距是挺大的，另外也试了一些图片的理解，我觉得还是挺不错的。

还有就是我感觉速度非常快，比如现在非常多的本地结合 OpenClaw 使用，会是一个好选择，就像我在前几天视频做了图片处理，我觉得换成 Qwen3.5 会效果更好。

---

## 4. pentagi
- 项目名称：pentagi – AI 渗透测试系统
- GitHub 链接：https://github.com/vxcontrol/pentagi

PentAGI 是由 VXControl 团队开发的开源全自动 AI 渗透测试与红队工作流系统，目标是让 AI 不只是"生成漏洞清单"，而是像资深安全工程师一样计划、执行、验证与报告渗透测试任务。你只需输入一个目标域名，系统自动执行侦察、端口扫描、漏洞挖掘，甚至生成完整报告，全程无需人工介入。

项目安装的话需要有 docker，然后下载 installer 去安装。过程中会进行各种配置，像大模型、Search engine、SSL 等。安装好之后有一个 Web UI 可以访问。

它整合 20+ 主流安全工具：包括 nmap、Metasploit、sqlmap、nikto、gobuster、hydra 等，AI 自主调度，动态决策攻击流程。同时它的所有操作均在沙盒 Docker 环境中进行，完全隔离。

![图片](/asset/post105/4-1.png)

项目很好的一点是给出了自己很详细的架构信息，可以直接查看到整体的系统背景，还有容器架构、实体关系、代理互动、记忆系统等内容的具体设计，都是很有研究和学习价值的。

---

## 5. carbon
- 项目名称：carbon – 精美源码图片生成工具
- GitHub 链接：https://github.com/carbon-app/carbon

Carbon 能够轻松地将你的源码生成漂亮的图片并分享，比如你看到各种文章里好看的代码片段，Carbon 就可以帮你快速地生成。

![图片](/asset/post105/5-1.png)

最简单的方式你可以直接访问 Carbon 的网站，它的界面简洁明了，操作起来也很方便，直接把代码替换成自己的就可以，它支持多种编程语言，像 JavaScript、Python、C++ 等主流语言都能很好地展示出来。还可以根据自己的喜欢来切换不同的显示样式。

你还可以把它保存成 PWA 应用，然后离线使用，另外它还有各种编辑器的插件和 CLI 工具，总之它是一个非常实用的小工具，尤其对于开发者来说非常实用。

---

## one more thing

最后还是分享 2 个资料，第一份是《2026 年具身智能产业发展研究报告》，36 氪研究院出的报告，今年的春晚看了吗，各种机器人的参与，好多人都说再过些年这春晚将会是机器人演给机器人看了，所以具身智能机器人的发展在 2026 必然还是热点中的热点。

第二个是《预见 2026：中国行业趋势报告》，这个是罗兰贝格的《预见》系列年度报告的最新内容，包括汽车、政府与公共、消费品与零售、大健康、能源、工业产品与服务、高科技等关键领域提供趋势解析与前沿洞察，整体质量是蛮高的。

有需要的可以告诉我，以上就是本周的全部内容，那我们下次再见。




# Supports

- [AstrBot Repo](https://github.com/AstrBotDevs/AstrBot)
- [AstrBot Plugin Development Docs (Chinese)](https://docs.astrbot.app/dev/star/plugin-new.html)
- [AstrBot Plugin Development Docs (English)](https://docs.astrbot.app/en/dev/star/plugin-new.html)
