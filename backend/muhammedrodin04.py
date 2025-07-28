#!/usr/bin/env python3
"""
API Call Tool - muhammedrodin04
A tool for making multiple API calls for testing and automation purposes
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import argparse
import sys

class APICallTool:
    def __init__(self):
        self.session = None
        self.results = []
        
    async def create_session(self):
        """Create aiohttp session"""
        self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def make_single_call(self, url: str, method: str = "GET", 
                              headers: Optional[Dict] = None, 
                              data: Optional[Dict] = None,
                              params: Optional[Dict] = None) -> Dict:
        """Make a single API call"""
        try:
            start_time = time.time()
            
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            ) as response:
                end_time = time.time()
                response_time = round((end_time - start_time) * 1000, 2)  # ms
                
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "url": url,
                    "method": method,
                    "status_code": response.status,
                    "response_time_ms": response_time,
                    "response_data": response_data,
                    "success": 200 <= response.status < 300
                }
                
                return result
                
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "url": url,
                "method": method,
                "status_code": 0,
                "response_time_ms": 0,
                "error": str(e),
                "success": False
            }
    
    async def make_multiple_calls(self, url: str, count: int = 10, 
                                 method: str = "GET", 
                                 headers: Optional[Dict] = None,
                                 data: Optional[Dict] = None,
                                 params: Optional[Dict] = None,
                                 delay: float = 0.1) -> List[Dict]:
        """Make multiple API calls"""
        await self.create_session()
        
        print(f"🚀 Starting {count} API calls to {url}")
        print(f"Method: {method}")
        print(f"Delay between calls: {delay}s")
        print("-" * 50)
        
        tasks = []
        for i in range(count):
            if delay > 0:
                await asyncio.sleep(delay)
            
            task = self.make_single_call(url, method, headers, data, params)
            tasks.append(task)
            print(f"📡 Call {i+1}/{count} initiated")
        
        # Wait for all calls to complete
        results = await asyncio.gather(*tasks)
        
        await self.close_session()
        
        # Print summary
        self.print_summary(results)
        
        return results
    
    def print_summary(self, results: List[Dict]):
        """Print summary of API call results"""
        print("\n" + "="*60)
        print("📊 API CALL SUMMARY")
        print("="*60)
        
        total_calls = len(results)
        successful_calls = sum(1 for r in results if r.get("success", False))
        failed_calls = total_calls - successful_calls
        
        if successful_calls > 0:
            avg_response_time = sum(r.get("response_time_ms", 0) for r in results if r.get("success", False)) / successful_calls
        else:
            avg_response_time = 0
        
        print(f"Total Calls: {total_calls}")
        print(f"✅ Successful: {successful_calls}")
        print(f"❌ Failed: {failed_calls}")
        print(f"⚡ Average Response Time: {avg_response_time:.2f}ms")
        
        # Status code breakdown
        status_codes = {}
        for result in results:
            status = result.get("status_code", 0)
            status_codes[status] = status_codes.get(status, 0) + 1
        
        print(f"\n📋 Status Code Breakdown:")
        for status, count in sorted(status_codes.items()):
            print(f"  {status}: {count} calls")
        
        # Show failed calls
        failed_results = [r for r in results if not r.get("success", False)]
        if failed_results:
            print(f"\n❌ Failed Calls Details:")
            for i, result in enumerate(failed_results[:5]):  # Show first 5 failures
                print(f"  {i+1}. Error: {result.get('error', 'Unknown error')}")
    
    def save_results(self, results: List[Dict], filename: str = "api_results.json"):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"💾 Results saved to {filename}")

async def main():
    parser = argparse.ArgumentParser(description="API Call Tool by muhammedrodin04")
    parser.add_argument("url", help="API endpoint URL")
    parser.add_argument("-c", "--count", type=int, default=10, help="Number of calls to make")
    parser.add_argument("-m", "--method", default="GET", help="HTTP method (GET, POST, PUT, DELETE)")
    parser.add_argument("-d", "--delay", type=float, default=0.1, help="Delay between calls in seconds")
    parser.add_argument("-H", "--headers", help="Headers as JSON string")
    parser.add_argument("--data", help="Request data as JSON string")
    parser.add_argument("--params", help="URL parameters as JSON string")
    parser.add_argument("-o", "--output", help="Output file for results")
    
    args = parser.parse_args()
    
    # Parse JSON arguments
    headers = json.loads(args.headers) if args.headers else None
    data = json.loads(args.data) if args.data else None
    params = json.loads(args.params) if args.params else None
    
    tool = APICallTool()
    
    try:
        results = await tool.make_multiple_calls(
            url=args.url,
            count=args.count,
            method=args.method.upper(),
            headers=headers,
            data=data,
            params=params,
            delay=args.delay
        )
        
        if args.output:
            tool.save_results(results, args.output)
        
    except KeyboardInterrupt:
        print("\n⏹️  API calls interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Example usage if run directly
    if len(sys.argv) == 1:
        print("🔧 API Call Tool - muhammedrodin04")
        print("\nExample usage:")
        print("python muhammedrodin04.py https://api.example.com/endpoint -c 50 -d 0.5")
        print("python muhammedrodin04.py https://httpbin.org/get -c 20 --method GET")
        print("python muhammedrodin04.py https://httpbin.org/post -c 10 --method POST --data '{\"key\":\"value\"}'")
        print("\nOptions:")
        print("  -c, --count     Number of API calls to make")
        print("  -m, --method    HTTP method (GET, POST, PUT, DELETE)")
        print("  -d, --delay     Delay between calls in seconds")
        print("  -H, --headers   Headers as JSON string")
        print("  --data          Request data as JSON string")
        print("  --params        URL parameters as JSON string")
        print("  -o, --output    Save results to file")
    else:
        asyncio.run(main())