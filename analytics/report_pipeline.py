"""
report_pipeline.py
Advanced trade visualization and report generation pipeline for EdgeX.
"""

import os
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objs as go

REPORTS_DIR = "reports"

def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

class ReportPipeline:
    def __init__(self, logger=None, base_dir=REPORTS_DIR):
        self.logger = logger
        self.base_dir = base_dir
        ensure_dir(base_dir)

    def save_trade_log(self, trade_log: List[Dict], name="trade_log.csv") -> None:
        df = pd.DataFrame(trade_log)
        path = os.path.join(self.base_dir, name)
        df.to_csv(path, index=False)
        if self.logger:
            self.logger.info(f"[ReportPipeline] Saved trade log to {path}")

    def plot_equity_curve(self, trades_df: pd.DataFrame, fname: str = "equity_curve.png") -> str:
        plt.figure(figsize=(12, 5))
        plt.plot(trades_df['timestamp'], trades_df['equity'], label='Equity Curve', color='blue')
        plt.fill_between(trades_df['timestamp'], trades_df['equity'], color='lightblue', alpha=0.25)
        plt.title("Equity Curve")
        plt.xlabel("Time")
        plt.ylabel("Account Equity")
        plt.grid(True)
        plt.legend()
        outpath = os.path.join(self.base_dir, fname)
        plt.tight_layout()
        plt.savefig(outpath)
        plt.close()
        if self.logger:
            self.logger.info(f"[ReportPipeline] Saved equity curve to {outpath}")
        return outpath

    def plot_drawdown(self, trades_df: pd.DataFrame, fname: str = "drawdown.png") -> str:
        equity = trades_df['equity']
        high = np.maximum.accumulate(equity)
        drawdown = (high - equity) / high
        plt.figure(figsize=(12, 3))
        plt.plot(trades_df['timestamp'], drawdown, label='Drawdown', color='red')
        plt.title("Drawdown Over Time")
        plt.xlabel("Time")
        plt.ylabel("Drawdown (%)")
        plt.grid(True)
        plt.legend()
        outpath = os.path.join(self.base_dir, fname)
        plt.tight_layout()
        plt.savefig(outpath)
        plt.close()
        if self.logger:
            self.logger.info(f"[ReportPipeline] Saved drawdown chart to {outpath}")
        return outpath

    def plot_trade_annotations(self, price_df: pd.DataFrame, trades_df: pd.DataFrame, fname: str = "trade_annotations.png") -> str:
        plt.figure(figsize=(12, 6))
        plt.plot(price_df.index, price_df['close'], label='Close Price', alpha=0.7)
        for _, trade in trades_df.iterrows():
            color = 'green' if "BUY" in trade["action"] else 'red'
            marker = '^' if "BUY" in trade["action"] else 'v'
            plt.scatter(trade["timestamp"], trade["entry_price"], color=color, marker=marker, s=90,
                        label=f'{trade["action"]} {trade["symbol"]} - {trade.get("reason", "")}')
        plt.title("Trade Signals Annotated on Price Chart")
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.legend(loc='best')
        outpath = os.path.join(self.base_dir, fname)
        plt.tight_layout()
        plt.savefig(outpath)
        plt.close()
        if self.logger:
            self.logger.info(f"[ReportPipeline] Saved trade annotation chart to {outpath}")
        return outpath

    def plot_sharpe_by_month(self, trades_df: pd.DataFrame, fname: str = "sharpe_by_month.png") -> str:
        trades_df['timestamp'] = pd.to_datetime(trades_df['timestamp'])
        trades_df['month'] = trades_df['timestamp'].dt.to_period('M')
        monthly_returns = trades_df.groupby('month')['pnl'].sum()
        monthly_sharpe = monthly_returns / monthly_returns.std() * np.sqrt(12)
        plt.figure(figsize=(10, 4))
        monthly_sharpe.plot(kind='bar', color='skyblue')
        plt.title("Sharpe Ratio by Month")
        plt.ylabel("Sharpe Ratio")
        plt.xlabel("Month")
        outpath = os.path.join(self.base_dir, fname)
        plt.tight_layout()
        plt.savefig(outpath)
        plt.close()
        if self.logger:
            self.logger.info(f"[ReportPipeline] Saved Sharpe by month chart to {outpath}")
        return outpath

    def plot_win_loss_ratio_by_symbol(self, trades_df: pd.DataFrame, fname: str = "win_loss_ratio.png") -> str:
        trades_df['win'] = trades_df['pnl'] > 0
        grouped = trades_df.groupby('symbol')['win'].mean()
        plt.figure(figsize=(12, 6))
        grouped.plot(kind='bar', color='lightgreen')
        plt.title("Win Ratio by Symbol")
        plt.ylabel("Win Ratio")
        plt.xlabel("Symbol")
        outpath = os.path.join(self.base_dir, fname)
        plt.tight_layout()
        plt.savefig(outpath)
        plt.close()
        if self.logger:
            self.logger.info(f"[ReportPipeline] Saved Win/Loss ratio by symbol chart to {outpath}")
        return outpath

    def export_trade_log_excel(self, trades_df: pd.DataFrame, fname: str = "trade_log.xlsx") -> str:
        path = os.path.join(self.base_dir, fname)
        trades_df.to_excel(path, index=False)
        if self.logger:
            self.logger.info(f"[ReportPipeline] Exported trade log to Excel at {path}")
        return path

    def export_trade_log_json(self, trades_df: pd.DataFrame, fname: str = "trade_log.json") -> str:
        path = os.path.join(self.base_dir, fname)
        trades_df.to_json(path, orient='records', date_format='iso')
        if self.logger:
            self.logger.info(f"[ReportPipeline] Exported trade log to JSON at {path}")
        return path

    # Additional methods for embedding into dashboards can be added here...
