"""
Test script to demonstrate the Intelligent Rate Limiter
Simulates normal and anomalous traffic patterns
"""

import asyncio
import aiohttp
import random
from datetime import datetime
import sys

BASE_URL = "http://localhost:8000"

class TrafficSimulator:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        await self.session.close()
    
    async def make_request(self, endpoint: str, client_name: str = "normal"):
        """Make a single request"""
        try:
            async with self.session.get(
                f"{self.base_url}{endpoint}",
                headers={"X-Forwarded-For": client_name}
            ) as response:
                status = response.status
                headers = dict(response.headers)
                
                limit = headers.get('X-RateLimit-Limit', 'N/A')
                remaining = headers.get('X-RateLimit-Remaining', 'N/A')
                
                if status == 200:
                    print(f"✅ [{client_name}] {endpoint} - Limit: {limit}, Remaining: {remaining}")
                elif status == 429:
                    print(f"🚫 [{client_name}] {endpoint} - RATE LIMITED! (Limit: {limit})")
                    
                return status, headers
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None, {}
    
    async def simulate_normal_traffic(self, duration: int = 30):
        """Simulate normal traffic pattern"""
        print(f"\n{'='*60}")
        print("🟢 Simulating NORMAL traffic pattern...")
        print(f"{'='*60}\n")
        
        endpoints = ["/", "/api/data", "/api/process"]
        
        for i in range(duration):
            endpoint = random.choice(endpoints)
            await self.make_request(endpoint, "normal_user")
            await asyncio.sleep(random.uniform(0.5, 1.5))
        
        print(f"\n✅ Normal traffic simulation completed\n")
    
    async def simulate_anomalous_traffic(self, duration: int = 20):
        """Simulate anomalous traffic (potential DDoS)"""
        print(f"\n{'='*60}")
        print("🔴 Simulating ANOMALOUS traffic pattern (rapid requests)...")
        print(f"{'='*60}\n")
        
        endpoint = "/api/heavy-operation"
        
        tasks = []
        for i in range(duration):
            # Rapid fire requests
            for _ in range(5):
                task = self.make_request(endpoint, "suspicious_user")
                tasks.append(task)
            
            if len(tasks) >= 10:
                await asyncio.gather(*tasks)
                tasks = []
            
            await asyncio.sleep(0.1)
        
        if tasks:
            await asyncio.gather(*tasks)
        
        print(f"\n✅ Anomalous traffic simulation completed\n")
    
    async def simulate_burst_traffic(self):
        """Simulate sudden burst of traffic"""
        print(f"\n{'='*60}")
        print("🟡 Simulating BURST traffic pattern...")
        print(f"{'='*60}\n")
        
        # Sudden burst
        tasks = []
        for i in range(50):
            task = self.make_request("/api/data", f"burst_user_{i%5}")
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        print(f"\n✅ Burst traffic simulation completed\n")
    
    async def check_stats(self):
        """Check current system statistics"""
        print(f"\n{'='*60}")
        print("📊 Current System Statistics")
        print(f"{'='*60}\n")
        
        try:
            async with self.session.get(f"{self.base_url}/admin/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Total Requests: {data['total_requests']}")
                    print(f"Unique Clients: {data['unique_clients']}")
                    print(f"Model Trained: {data['model_trained']}")
                    print(f"\nEndpoint Distribution:")
                    for endpoint, count in data['endpoints'].items():
                        print(f"  {endpoint}: {count}")
        except Exception as e:
            print(f"❌ Error fetching stats: {e}")
        
        print()
    
    async def check_model_info(self):
        """Check ML model information"""
        print(f"\n{'='*60}")
        print("🤖 ML Model Information")
        print(f"{'='*60}\n")
        
        try:
            async with self.session.get(f"{self.base_url}/admin/model-info") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Status: {data['status']}")
                    if data['status'] != 'not_initialized':
                        print(f"Anomaly Detection Threshold: {data.get('anomaly_threshold', 'N/A')}")
                        print(f"Features Used: {', '.join(data.get('features', []))}")
        except Exception as e:
            print(f"❌ Error fetching model info: {e}")
        
        print()


async def run_demo():
    """Run complete demonstration"""
    print("\n" + "="*60)
    print("🚀 Intelligent Rate Limiter - Demo Script")
    print("="*60 + "\n")
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    await asyncio.sleep(2)
    
    async with TrafficSimulator() as sim:
        # Check initial state
        await sim.check_stats()
        await sim.check_model_info()
        
        # Phase 1: Normal traffic
        await sim.simulate_normal_traffic(duration=20)
        await sim.check_stats()
        
        # Wait a bit
        print("⏸️  Pausing for 3 seconds...\n")
        await asyncio.sleep(3)
        
        # Phase 2: Burst traffic
        await sim.simulate_burst_traffic()
        await sim.check_stats()
        
        # Wait a bit
        print("⏸️  Pausing for 3 seconds...\n")
        await asyncio.sleep(3)
        
        # Phase 3: Anomalous traffic
        await sim.simulate_anomalous_traffic(duration=15)
        await sim.check_stats()
        
        # Final statistics
        print("\n" + "="*60)
        print("📈 FINAL STATISTICS")
        print("="*60)
        await sim.check_stats()
        await sim.check_model_info()
        
        print("\n" + "="*60)
        print("✅ Demo completed!")
        print("="*60 + "\n")
        print("💡 The system has now learned from the traffic patterns.")
        print("   Subsequent anomalous traffic will be rate-limited more aggressively.\n")


async def run_continuous_test():
    """Run continuous test to build up training data"""
    print("\n🔄 Running continuous test to build ML training data...")
    print("   Press Ctrl+C to stop\n")
    
    async with TrafficSimulator() as sim:
        try:
            while True:
                # Mix of normal and occasional anomalous traffic
                if random.random() < 0.8:
                    await sim.make_request(
                        random.choice(["/", "/api/data", "/api/process"]),
                        f"user_{random.randint(1, 10)}"
                    )
                    await asyncio.sleep(random.uniform(0.3, 2.0))
                else:
                    # Anomalous burst
                    for _ in range(random.randint(5, 15)):
                        await sim.make_request("/api/heavy-operation", "attacker")
                        await asyncio.sleep(0.05)
                    await asyncio.sleep(random.uniform(5, 10))
                    
        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping continuous test...")
            await sim.check_stats()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        asyncio.run(run_continuous_test())
    else:
        asyncio.run(run_demo())
