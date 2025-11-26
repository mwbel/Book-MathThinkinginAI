#!/usr/bin/env python3
"""
Gemini API 监控和自动化脚本
定期检查使用情况，自动管理 API key 状态
"""

import time
import schedule
from datetime import datetime
from gemini_api_manager import GeminiAPIManager
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeminiMonitor:
    def __init__(self):
        self.manager = GeminiAPIManager()

    def check_all_keys(self):
        """检查所有 API keys 状态"""
        logger.info("🔍 检查所有 API keys 状态...")

        for api_key_info in self.manager.config["api_keys"]:
            name = api_key_info["name"]
            key = api_key_info["key"]

            if not api_key_info.get("active", True):
                logger.info(f"⏸️  {name}: 已禁用")
                continue

            # 测试 API key
            is_valid = self.manager.test_api_key(key)
            daily_usage = self.manager.get_daily_usage(key)
            daily_limit = api_key_info["daily_limit"]

            usage_percent = (daily_usage / daily_limit * 100) if daily_limit > 0 else 0

            if is_valid:
                if usage_percent >= 90:
                    logger.warning(f"⚠️  {name}: 即将用完 ({usage_percent:.1f}%)")
                elif usage_percent >= 100:
                    logger.error(f"❌ {name}: 已用完 ({daily_usage}/{daily_limit})")
                    # 可以选择自动禁用
                    # self.manager.set_active_key(name, False)
                else:
                    logger.info(f"✅ {name}: 正常 ({usage_percent:.1f}%)")
            else:
                logger.error(f"❌ {name}: API key 无效")

    def reset_daily_usage(self):
        """重置过期的使用数据"""
        logger.info("🔄 重置过期使用数据...")
        today = datetime.now().strftime("%Y-%m-%d")

        # 删除 7 天前的数据
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - 7)

        for api_key in list(self.manager.usage_data.keys()):
            dates_to_remove = []
            for date_str in self.manager.usage_data[api_key].keys():
                if date_str != "last_error_time" and date_str != "last_error":
                    try:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        if date_obj < cutoff_date:
                            dates_to_remove.append(date_str)
                    except ValueError:
                        continue

            for date_str in dates_to_remove:
                del self.manager.usage_data[api_key][date_str]
                logger.info(f"🗑️  删除过期数据: {api_key} - {date_str}")

        self.manager.save_usage()

    def generate_daily_report(self):
        """生成每日报告"""
        logger.info("📊 生成每日使用报告...")
        report = self.manager.get_usage_report()

        # 保存报告到文件
        today = datetime.now().strftime("%Y-%m-%d")
        report_file = f"gemini_daily_report_{today}.txt"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"Gemini API 每日使用报告 - {today}\n")
            f.write("=" * 50 + "\n\n")
            f.write(report)

        logger.info(f"📄 报告已保存到: {report_file}")

        # 打印简报
        total_usage = 0
        total_limit = 0

        for api_key_info in self.manager.config["api_keys"]:
            if api_key_info.get("active", True):
                total_usage += self.manager.get_daily_usage(api_key_info["key"])
                total_limit += api_key_info["daily_limit"]

        usage_percent = (total_usage / total_limit * 100) if total_limit > 0 else 0
        logger.info(f"📈 今日总使用: {total_usage}/{total_limit} ({usage_percent:.1f}%)")

    def auto_switch_keys(self):
        """自动切换到可用的 API key"""
        logger.info("🔄 自动检查并切换 API key...")

        current_key = self.manager.get_current_api_key()
        if current_key:
            logger.info(f"✅ 当前 API key 可用")
        else:
            logger.warning("⚠️  没有可用的 API key，尝试重新启用冷却中的 key...")
            # 这里可以实现更复杂的重新启用逻辑

    def run_monitoring(self):
        """运行监控任务"""
        logger.info("🚀 启动 Gemini API 监控服务...")

        # 立即执行一次检查
        self.check_all_keys()
        self.generate_daily_report()

        # 定时任务
        schedule.every(1).hours.do(self.check_all_keys)  # 每小时检查一次
        schedule.every().day.at("08:00").do(self.generate_daily_report)  # 每天 8 点生成报告
        schedule.every().day.at("00:05").do(self.reset_daily_usage)  # 每天 0 点重置过期数据
        schedule.every(30).minutes.do(self.auto_switch_keys)  # 每 30 分钟自动切换

        logger.info("⏰ 定时任务已设置:")
        logger.info("   - 每小时检查 API keys 状态")
        logger.info("   - 每天 08:00 生成使用报告")
        logger.info("   - 每天 00:05 清理过期数据")
        logger.info("   - 每 30 分钟自动切换 API key")
        logger.info("按 Ctrl+C 停止监控...")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("🛑 监控服务已停止")

def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="Gemini API 监控工具")
    parser.add_argument("action", choices=["monitor", "check", "report", "reset"],
                       help="要执行的操作")

    args = parser.parse_args()

    monitor = GeminiMonitor()

    if args.action == "monitor":
        monitor.run_monitoring()
    elif args.action == "check":
        monitor.check_all_keys()
    elif args.action == "report":
        monitor.generate_daily_report()
    elif args.action == "reset":
        monitor.reset_daily_usage()

if __name__ == "__main__":
    main()