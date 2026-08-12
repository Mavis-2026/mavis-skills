"""
scripts/cleanup_old_reports.py
清理 15 天前的复盘报告
8-12 用户规则: 报告存沙箱只存半个月, 半个月后覆盖
"""
import os
import re
import time
from pathlib import Path
from datetime import datetime, timedelta


REPORTS_DIR = Path("/workspace/docs/reports")
KEEP_DAYS = 15  # 保留 15 天


def parse_date_from_filename(filename: str):
    """从文件名提取日期: daily-review-YYYY-MM-DD-main.html"""
    m = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if m:
        try:
            return datetime.strptime(m.group(1), '%Y-%m-%d').date()
        except ValueError:
            return None
    return None


def cleanup_old_reports(reports_dir: Path = REPORTS_DIR, keep_days: int = KEEP_DAYS, dry_run: bool = False):
    """清理 keep_days 天前的报告

    Args:
        reports_dir: 报告目录
        keep_days: 保留天数
        dry_run: 只显示要删的不真删
    """
    if not reports_dir.exists():
        print(f"  ⚠️ 目录不存在: {reports_dir}")
        return 0

    cutoff_date = datetime.now().date() - timedelta(days=keep_days)
    today = datetime.now().date()
    print(f"  📅 今天是 {today}, 保留 {keep_days} 天, 删 {cutoff_date} 之前")

    deleted = 0
    kept = 0
    for f in reports_dir.iterdir():
        if not f.is_file():
            continue
        # 只清理复盘报告 (其他文件不动)
        if not (f.name.startswith("daily-review-") or f.name.startswith("weekly-review-")):
            continue
        file_date = parse_date_from_filename(f.name)
        if file_date is None:
            kept += 1
            continue
        if file_date < cutoff_date:
            if dry_run:
                print(f"  🗑️ [DRY-RUN] 删: {f.name} ({file_date})")
            else:
                f.unlink()
                print(f"  🗑️ 删: {f.name} ({file_date})")
            deleted += 1
        else:
            kept += 1

    print(f"\n  ✅ 删 {deleted} 个, 留 {kept} 个")
    return deleted


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="只显示要删的不真删")
    p.add_argument("--keep-days", type=int, default=KEEP_DAYS, help=f"保留天数(默认 {KEEP_DAYS})")
    p.add_argument("--reports-dir", default=str(REPORTS_DIR), help="报告目录")
    args = p.parse_args()
    cleanup_old_reports(
        reports_dir=Path(args.reports_dir),
        keep_days=args.keep_days,
        dry_run=args.dry_run,
    )
