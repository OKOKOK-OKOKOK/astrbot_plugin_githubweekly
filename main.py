import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

import feedparser
import aiohttp
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

RSS_URL = "https://itcoffee66.github.io/githubweekly/feed.xml"
CACHE_HOURS = 24
DEFAULT_LIST_COUNT = 10

@register("astrbot_plugin_githubweekly", "OKOKOK-OKOKOK", "获取 GitHub 最近一周的热门项目", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.cache_file: Optional[Path] = None
        self.rss_data: Optional[Dict] = None
        self.subscribed_users: List[str] = []

    async def initialize(self):
        """插件初始化方法"""
        from astrbot.core.utils.astrbot_path import get_astrbot_data_path
        
        data_path = Path(get_astrbot_data_path())
        self.cache_file = data_path / "plugin_data" / self.name / "rss_cache.json"
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"GitHubWeekly插件初始化完成，缓存文件路径: {self.cache_file}")
        
        await self.load_subscribed_users()
        
        await self.load_cache()
        
        asyncio.create_task(self.start_scheduler())

    async def load_subscribed_users(self):
        """加载订阅用户列表"""
        try:
            users = await self.get_kv_data("subscribed_users", [])
            self.subscribed_users = users if isinstance(users, list) else []
            logger.info(f"已加载 {len(self.subscribed_users)} 个订阅用户")
        except Exception as e:
            logger.error(f"加载订阅用户失败: {e}")
            self.subscribed_users = []

    async def save_subscribed_users(self):
        """保存订阅用户列表"""
        try:
            await self.put_kv_data("subscribed_users", self.subscribed_users)
            logger.info(f"已保存 {len(self.subscribed_users)} 个订阅用户")
        except Exception as e:
            logger.error(f"保存订阅用户失败: {e}")

    async def load_cache(self):
        """加载RSS缓存"""
        if not self.cache_file.exists():
            logger.info("缓存文件不存在，将首次获取RSS数据")
            return
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            cache_time = datetime.fromisoformat(cache_data.get('cache_time', ''))
            if datetime.now() - cache_time < timedelta(hours=CACHE_HOURS):
                self.rss_data = cache_data
                logger.info(f"从缓存加载RSS数据，缓存时间: {cache_time}")
            else:
                logger.info("缓存已过期，将重新获取RSS数据")
        except Exception as e:
            logger.error(f"加载缓存失败: {e}")

    async def save_cache(self, data: Dict):
        """保存RSS缓存"""
        try:
            data['cache_time'] = datetime.now().isoformat()
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"RSS数据已缓存，缓存时间: {data['cache_time']}")
        except Exception as e:
            logger.error(f"保存缓存失败: {e}")

    async def fetch_rss(self) -> Optional[Dict]:
        """获取RSS数据"""
        if self.rss_data:
            return self.rss_data
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(RSS_URL, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        logger.error(f"获取RSS失败，状态码: {response.status}")
                        return None
                    
                    xml_content = await response.text()
                    
            feed = feedparser.parse(xml_content)
            
            if not feed.entries:
                logger.error("RSS数据为空")
                return None
            
            entries = []
            for entry in feed.entries:
                entry_data = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', '')
                }
                entries.append(entry_data)
            
            result = {
                'feed_title': feed.feed.get('title', ''),
                'feed_subtitle': feed.feed.get('subtitle', ''),
                'entries': entries
            }
            
            self.rss_data = result
            await self.save_cache(result)
            
            logger.info(f"成功获取RSS数据，共 {len(entries)} 条记录")
            return result
            
        except asyncio.TimeoutError:
            logger.error("获取RSS超时")
            return None
        except Exception as e:
            logger.error(f"获取RSS失败: {e}")
            return None

    async def start_scheduler(self):
        """启动定时任务"""
        while True:
            now = datetime.now()
            target_time = now.replace(hour=12, minute=0, second=0, microsecond=0)
            
            if now >= target_time:
                target_time += timedelta(days=1)
            
            wait_seconds = (target_time - now).total_seconds()
            logger.info(f"下次推送时间: {target_time}，等待 {wait_seconds:.0f} 秒")
            
            await asyncio.sleep(wait_seconds)
            
            await self.daily_push()

    async def daily_push(self):
        """每日推送"""
        logger.info("开始执行每日推送任务")
        
        rss_data = await self.fetch_rss()
        if not rss_data or not rss_data['entries']:
            logger.error("推送失败：无法获取RSS数据")
            return
        
        latest_entry = rss_data['entries'][0]
        
        message = f"📰 GitHub Weekly 每日推送\n\n"
        message += f"📌 {latest_entry['title']}\n"
        message += f"🔗 {latest_entry['link']}\n"
        message += f"📅 {latest_entry['published']}\n"
        message += f"📝 {latest_entry['summary']}\n"
        message += f"\n💡 使用 /githubweekly list 查看更多往期周报"
        
        logger.info(f"准备推送最新周报: {latest_entry['title']}")
        
        if not self.subscribed_users:
            logger.warning("没有订阅用户，跳过推送")
            return
        
        for user_origin in self.subscribed_users:
            try:
                from astrbot.api.event import MessageChain
                message_chain = MessageChain().message(message)
                await self.context.send_message(user_origin, message_chain)
                logger.info(f"已向用户 {user_origin} 推送周报")
            except Exception as e:
                logger.error(f"向用户 {user_origin} 推送失败: {e}")

    @filter.command("githubweekly")
    async def githubweekly(self, event: AstrMessageEvent):
        """GitHub Weekly 主命令"""
        message_str = event.message_str.strip()
        
        if not message_str:
            yield event.plain_result("📰 GitHub Weekly 使用帮助\n\n"
                                    "🔹 /githubweekly latest - 获取最新周报\n"
                                    "🔹 /githubweekly list [N] - 列出往期周报（默认10条）\n"
                                    "🔹 /githubweekly subscribe - 订阅每日推送\n"
                                    "🔹 /githubweekly unsubscribe - 取消订阅\n"
                                    "🔹 /githubweekly status - 查看订阅状态")
            return
        
        parts = message_str.split()
        command = parts[0].lower()
        
        if command == "latest":
            async for result in self.cmd_latest(event):
                yield result
        elif command == "list":
            count = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else DEFAULT_LIST_COUNT
            async for result in self.cmd_list(event, count):
                yield result
        elif command == "subscribe":
            async for result in self.cmd_subscribe(event):
                yield result
        elif command == "unsubscribe":
            async for result in self.cmd_unsubscribe(event):
                yield result
        elif command == "status":
            async for result in self.cmd_status(event):
                yield result
        else:
            yield event.plain_result("❌ 未知命令，使用 /githubweekly 查看帮助")

    async def cmd_latest(self, event: AstrMessageEvent):
        """获取最新周报"""
        logger.info(f"用户 {event.get_sender_name()} 请求获取最新周报")
        
        rss_data = await self.fetch_rss()
        if not rss_data or not rss_data['entries']:
            yield event.plain_result("❌ 获取周报失败，请稍后重试")
            return
        
        latest = rss_data['entries'][0]
        
        message = f"📰 GitHub Weekly 最新周报\n\n"
        message += f"📌 {latest['title']}\n"
        message += f"🔗 {latest['link']}\n"
        message += f"📅 {latest['published']}\n"
        message += f"📝 {latest['summary']}\n"
        
        yield event.plain_result(message)
        logger.info(f"已向用户 {event.get_sender_name()} 发送最新周报")

    async def cmd_list(self, event: AstrMessageEvent, count: int):
        """列出往期周报"""
        logger.info(f"用户 {event.get_sender_name()} 请求列出 {count} 条往期周报")
        
        rss_data = await self.fetch_rss()
        if not rss_data or not rss_data['entries']:
            yield event.plain_result("❌ 获取周报失败，请稍后重试")
            return
        
        entries = rss_data['entries'][:count]
        
        message = f"📰 GitHub Weekly 往期周报（共 {len(entries)} 条）\n\n"
        
        for idx, entry in enumerate(entries, 1):
            message += f"{idx}. {entry['title']}\n"
            message += f"   🔗 {entry['link']}\n"
            message += f"   📅 {entry['published']}\n\n"
        
        yield event.plain_result(message)
        logger.info(f"已向用户 {event.get_sender_name()} 发送 {len(entries)} 条往期周报")

    async def cmd_subscribe(self, event: AstrMessageEvent):
        """订阅每日推送"""
        user_origin = event.unified_msg_origin
        user_name = event.get_sender_name()
        
        if user_origin in self.subscribed_users:
            yield event.plain_result("✅ 您已经订阅了每日推送")
            logger.info(f"用户 {user_name} 尝试重复订阅")
            return
        
        self.subscribed_users.append(user_origin)
        await self.save_subscribed_users()
        
        yield event.plain_result("✅ 订阅成功！您将在每天12:00收到最新周报推送")
        logger.info(f"用户 {user_name} 已订阅每日推送")

    async def cmd_unsubscribe(self, event: AstrMessageEvent):
        """取消订阅"""
        user_origin = event.unified_msg_origin
        user_name = event.get_sender_name()
        
        if user_origin not in self.subscribed_users:
            yield event.plain_result("❌ 您还没有订阅每日推送")
            logger.info(f"用户 {user_name} 尝试取消订阅，但未订阅")
            return
        
        self.subscribed_users.remove(user_origin)
        await self.save_subscribed_users()
        
        yield event.plain_result("✅ 已取消订阅")
        logger.info(f"用户 {user_name} 已取消订阅")

    async def cmd_status(self, event: AstrMessageEvent):
        """查看订阅状态"""
        user_origin = event.unified_msg_origin
        user_name = event.get_sender_name()
        
        is_subscribed = user_origin in self.subscribed_users
        
        status = "✅ 已订阅" if is_subscribed else "❌ 未订阅"
        message = f"📊 订阅状态\n\n"
        message += f"用户: {user_name}\n"
        message += f"状态: {status}\n"
        message += f"推送时间: 每天12:00\n"
        
        if is_subscribed:
            message += f"\n💡 使用 /githubweekly unsubscribe 取消订阅"
        else:
            message += f"\n💡 使用 /githubweekly subscribe 订阅每日推送"
        
        yield event.plain_result(message)
        logger.info(f"用户 {user_name} 查看订阅状态: {status}")

    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令"""
        user_name = event.get_sender_name()
        message_str = event.message_str
        message_chain = event.get_messages()
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!")

    async def terminate(self):
        """插件销毁方法"""
        logger.info("GitHubWeekly插件已停止")
