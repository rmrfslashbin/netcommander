#!/usr/bin/env python3
"""
NetCommander Authentication Test Script

This script tests various authentication approaches to understand
how the Synaccess netCommander device handles web authentication.
"""

import asyncio
import aiohttp
import logging
import os
import sys
from typing import Optional
from dotenv import load_dotenv
from urllib.parse import urljoin
import json

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress noisy aiohttp logs
logging.getLogger('aiohttp').setLevel(logging.WARNING)


class NetCommanderAuthTester:
    """Test various authentication approaches"""
    
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.base_url = f"http://{host}"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Create persistent session"""
        self.session = aiohttp.ClientSession(
            cookie_jar=aiohttp.CookieJar(),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up session"""
        if self.session:
            await self.session.close()
            
    async def test_homepage_analysis(self):
        """Analyze the homepage to understand login mechanism"""
        logger.info("=== Testing Homepage Analysis ===")
        
        try:
            async with self.session.get(self.base_url) as resp:
                logger.info(f"Homepage status: {resp.status}")
                logger.info(f"Headers: {dict(resp.headers)}")
                
                if resp.status == 401:
                    logger.info("Homepage requires authentication (401)")
                    # Check if WWW-Authenticate header exists
                    if 'WWW-Authenticate' in resp.headers:
                        logger.info(f"Auth type: {resp.headers['WWW-Authenticate']}")
                        
                text = await resp.text()
                logger.debug(f"Response preview: {text[:500]}...")
                
                # Look for login forms
                if '<form' in text.lower():
                    logger.info("Found form element - likely form-based auth")
                if 'login' in text.lower():
                    logger.info("Found 'login' keyword in response")
                    
                return resp.status, text
                
        except Exception as e:
            logger.error(f"Homepage test failed: {e}")
            return None, None
            
    async def test_basic_auth(self):
        """Test standard HTTP Basic Authentication"""
        logger.info("\n=== Testing Basic Authentication ===")
        
        auth = aiohttp.BasicAuth(self.username, self.password)
        
        try:
            # Test on homepage
            async with self.session.get(self.base_url, auth=auth) as resp:
                logger.info(f"Basic auth homepage status: {resp.status}")
                
            # Test on cmd.cgi
            async with self.session.get(f"{self.base_url}/cmd.cgi", auth=auth) as resp:
                logger.info(f"Basic auth cmd.cgi status: {resp.status}")
                text = await resp.text()
                logger.debug(f"Response: {text[:200]}...")
                
                return resp.status == 200
                
        except Exception as e:
            logger.error(f"Basic auth test failed: {e}")
            return False
            
    async def test_form_login(self):
        """Test form-based login (common in embedded devices)"""
        logger.info("\n=== Testing Form-Based Login ===")
        
        # Common login endpoints to try
        login_endpoints = [
            '/login.cgi',
            '/login',
            '/login.html',
            '/index.cgi',
            '/'
        ]
        
        for endpoint in login_endpoints:
            logger.info(f"Trying login endpoint: {endpoint}")
            
            login_data = {
                'username': self.username,
                'password': self.password,
                # Common variations
                'user': self.username,
                'pass': self.password,
                'pwd': self.password,
                'passwd': self.password
            }
            
            try:
                async with self.session.post(
                    urljoin(self.base_url, endpoint),
                    data=login_data,
                    allow_redirects=True
                ) as resp:
                    logger.info(f"POST {endpoint} status: {resp.status}")
                    logger.info(f"Final URL: {resp.url}")
                    
                    # Check cookies
                    cookies = self.session.cookie_jar.filter_cookies(self.base_url)
                    if cookies:
                        logger.info(f"Cookies set: {list(cookies.keys())}")
                        
                    if resp.status == 200:
                        # Test if we're authenticated by trying a command
                        return await self.test_authenticated_command()
                        
            except Exception as e:
                logger.debug(f"Endpoint {endpoint} failed: {e}")
                
        return False
        
    async def test_command_with_auth(self):
        """Test the $A1 login command as documented"""
        logger.info("\n=== Testing $A1 Login Command ===")
        
        # Try different URL formats
        formats = [
            f"/cmd.cgi?$A1,{self.username},{self.password}",
            f"/cmd.cgi?cmd=$A1,{self.username},{self.password}",
            f"/cmd.cgi?cmd=$A1&arg1={self.username}&arg2={self.password}",
        ]
        
        for url_format in formats:
            logger.info(f"Trying format: {url_format}")
            
            try:
                async with self.session.get(
                    urljoin(self.base_url, url_format)
                ) as resp:
                    logger.info(f"Status: {resp.status}")
                    text = await resp.text()
                    logger.info(f"Response: {text[:100]}...")
                    
                    # Check for success indicators
                    if "$A0" in text:
                        logger.info("Found $A0 (success) in response!")
                        return True
                        
            except Exception as e:
                logger.debug(f"Format failed: {e}")
                
        return False
        
    async def test_authenticated_command(self):
        """Test if we can execute a command (status check)"""
        logger.info("\n=== Testing Status Command ===")
        
        try:
            # Try the $A5 status command
            async with self.session.get(
                f"{self.base_url}/cmd.cgi?$A5"
            ) as resp:
                logger.info(f"Status command response: {resp.status}")
                text = await resp.text()
                logger.info(f"Response text: {text}")
                
                # Look for expected response format
                if resp.status == 200 and ('$A0' in text or ',' in text):
                    logger.info("✅ Successfully executed authenticated command!")
                    return True
                    
        except Exception as e:
            logger.error(f"Status command failed: {e}")
            
        return False
        
    async def test_combined_approach(self):
        """Try Basic Auth + command in single request"""
        logger.info("\n=== Testing Combined Basic Auth + Command ===")
        
        auth = aiohttp.BasicAuth(self.username, self.password)
        
        try:
            # First establish session with basic auth
            async with self.session.get(self.base_url, auth=auth) as resp:
                logger.info(f"Initial auth status: {resp.status}")
                
            # Then try command
            async with self.session.get(
                f"{self.base_url}/cmd.cgi?$A5",
                auth=auth
            ) as resp:
                logger.info(f"Command with auth status: {resp.status}")
                text = await resp.text()
                logger.info(f"Response: {text}")
                
                return resp.status == 200
                
        except Exception as e:
            logger.error(f"Combined approach failed: {e}")
            return False


async def main():
    """Run all authentication tests"""
    
    # Load environment variables
    load_dotenv()
    
    host = os.getenv('NETCOMMANDER_HOST')
    username = os.getenv('NETCOMMANDER_USER')
    password = os.getenv('NETCOMMANDER_PASSWORD')
    
    if not all([host, username, password]):
        logger.error("Missing required environment variables!")
        logger.error("Please create a .env file with:")
        logger.error("NETCOMMANDER_HOST=<device_ip>")
        logger.error("NETCOMMANDER_USER=<username>")
        logger.error("NETCOMMANDER_PASSWORD=<password>")
        sys.exit(1)
        
    logger.info(f"Testing authentication for {host}")
    logger.info(f"Username: {username}")
    logger.info("=" * 50)
    
    async with NetCommanderAuthTester(host, username, password) as tester:
        # Run tests in sequence
        results = {}
        
        # 1. Analyze homepage
        status, html = await tester.test_homepage_analysis()
        results['homepage'] = status
        
        # 2. Try basic auth
        results['basic_auth'] = await tester.test_basic_auth()
        
        # 3. Try form login
        results['form_login'] = await tester.test_form_login()
        
        # 4. Try command-based login
        results['command_login'] = await tester.test_command_with_auth()
        
        # 5. Try combined approach
        results['combined'] = await tester.test_combined_approach()
        
        # Summary
        logger.info("\n" + "=" * 50)
        logger.info("AUTHENTICATION TEST SUMMARY")
        logger.info("=" * 50)
        
        for test, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test:20} {status}")
            
        # Recommendations
        logger.info("\n" + "=" * 50)
        logger.info("RECOMMENDATIONS")
        logger.info("=" * 50)
        
        if results['basic_auth']:
            logger.info("✅ Device supports Basic Auth - use this approach")
        elif results['form_login']:
            logger.info("✅ Device uses form-based login - implement session management")
        elif results['command_login']:
            logger.info("✅ Device accepts command-based auth - use $A1 command")
        else:
            logger.info("❌ No working auth method found - need packet capture")
            logger.info("Next steps:")
            logger.info("1. Use browser dev tools to capture working login")
            logger.info("2. Check for JavaScript-based authentication")
            logger.info("3. Look for custom headers or tokens")


if __name__ == "__main__":
    asyncio.run(main())