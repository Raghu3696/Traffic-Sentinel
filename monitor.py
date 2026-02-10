"""
Visualization script for the Intelligent Rate Limiter
Shows real-time rate limit adjustments and anomaly detection
"""

import asyncio
import aiohttp
from datetime import datetime
import time

class RateLimiterMonitor:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        await self.session.close()
    
    async def get_stats(self):
        """Fetch current statistics"""
        async with self.session.get(f"{self.base_url}/admin/stats") as response:
            if response.status == 200:
                return await response.json()
        return None
    
    async def get_limits(self):
        """Fetch current limits"""
        async with self.session.get(f"{self.base_url}/admin/limits") as response:
            if response.status == 200:
                return await response.json()
        return None
    
    async def get_model_info(self):
        """Fetch model information"""
        async with self.session.get(f"{self.base_url}/admin/model-info") as response:
            if response.status == 200:
                return await response.json()
        return None
    
    def print_dashboard(self, stats, limits, model_info):
        """Print a nice dashboard"""
        # Clear screen (works on Unix-like systems)
        print("\033[2J\033[H")
        
        print("=" * 80)
        print(" 🚦 INTELLIGENT RATE LIMITER - REAL-TIME MONITOR".center(80))
        print("=" * 80)
        print()
        
        # Current time
        print(f"⏰ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Model status
        if model_info:
            status_emoji = "✅" if model_info['status'] == 'trained' else "⚠️"
            print(f"🤖 ML Model Status: {status_emoji} {model_info['status'].upper()}")
            if model_info['status'] == 'trained':
                print(f"   Anomaly Threshold: {model_info.get('anomaly_threshold', 'N/A')}")
        print()
        
        # Traffic statistics
        if stats:
            print("📊 Traffic Statistics:")
            print(f"   Total Requests: {stats['total_requests']}")
            print(f"   Unique Clients: {stats['unique_clients']}")
            print()
            
            if stats['endpoints']:
                print("📍 Endpoint Distribution:")
                for endpoint, count in sorted(stats['endpoints'].items(), key=lambda x: x[1], reverse=True):
                    bar_length = min(50, count // 10)
                    bar = "█" * bar_length
                    print(f"   {endpoint:30} {bar} {count}")
                print()
        
        # Current limits
        if limits:
            print("⚙️  Rate Limit Configuration:")
            print(f"   Base Limit: {limits['base_limit']} requests / {limits['window_seconds']}s")
            print()
        
        print("=" * 80)
        print("Press Ctrl+C to stop monitoring".center(80))
        print("=" * 80)
    
    async def monitor_loop(self, interval: int = 2):
        """Continuously monitor and display dashboard"""
        try:
            while True:
                stats = await self.get_stats()
                limits = await self.get_limits()
                model_info = await self.get_model_info()
                
                self.print_dashboard(stats, limits, model_info)
                
                await asyncio.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped")


async def main():
    print("🚀 Starting Rate Limiter Monitor...")
    print("   Make sure the API is running on http://localhost:8000")
    print()
    await asyncio.sleep(2)
    
    async with RateLimiterMonitor() as monitor:
        await monitor.monitor_loop()


if __name__ == "__main__":
    asyncio.run(main())
