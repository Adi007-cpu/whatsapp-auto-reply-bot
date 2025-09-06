from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random

class WhatsAppBot:
    def __init__(self, target_contact, headless=False):
        self.target_contact = target_contact
        self.driver = None
        self.processed_messages = set()  # Track multiple messages
        self.setup_driver(headless)
        
    def setup_driver(self, headless):
        """Setup Chrome driver with stealth options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        
        # Anti-detection measures
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def wait_for_whatsapp_load(self):
        """Wait for WhatsApp Web to fully load"""
        print("Loading WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")
        
        print("Please scan the QR code...")
        print("Waiting for WhatsApp to load (this may take up to 2 minutes)...")
        
        # More flexible waiting - look for any signs WhatsApp has loaded
        max_attempts = 60
        for attempt in range(max_attempts):
            try:
                # Check for various elements that indicate WhatsApp has loaded
                selectors_to_check = [
                    "[data-testid='chat-list']",  # Chat list (after login)
                    "canvas[aria-label*='QR code']",  # QR code canvas
                    "[data-testid='qr-code']",  # QR code container
                    "div._2EoyP",  # WhatsApp logo area
                    "div[data-testid='intro-md-beta-logo-dark']",
                    "div[data-testid='intro-md-beta-logo-light']",
                    "div._3WByx",  # Main container
                    "header[data-testid='chatlist-header']",  # Chat list header
                    "div[aria-label='Chat list']",  # Chat list aria-label
                    "span[data-testid='phone-number']"  # Phone number display
                ]
                
                for selector in selectors_to_check:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"WhatsApp Web loaded! (Found: {selector})")
                        time.sleep(5)  # Give extra time for full load
                        return True
                
                # Also check page title
                if "WhatsApp" in self.driver.title:
                    print("WhatsApp Web loaded! (Detected via title)")
                    time.sleep(5)
                    return True
                
                print(f"Attempt {attempt + 1}/{max_attempts} - Still loading...")
                time.sleep(2)
                
            except Exception as e:
                print(f"Check attempt {attempt + 1} failed: {e}")
                time.sleep(2)
        
        print("Failed to load WhatsApp Web - timeout reached")
        print("Debugging page state:")
        self.debug_page_state()
        return False
    
    def find_and_open_chat(self):
        """Find and open the target contact's chat"""
        try:
            # Try multiple methods to find the contact
            contact_selectors = [
                f"//span[@title='{self.target_contact}']",
                f"//span[contains(text(), '{self.target_contact}')]",
                f"//div[contains(@aria-label, '{self.target_contact}')]"
            ]
            
            chat_element = None
            for selector in contact_selectors:
                try:
                    chat_element = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
            
            if not chat_element:
                # Try searching for the contact
                self.search_contact()
                chat_element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[@title='{self.target_contact}']"))
                )
            
            chat_element.click()
            print(f"Opened chat with {self.target_contact}")
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"Could not open chat: {e}")
            return False
    
    def search_contact(self):
        """Search for contact using search box"""
        try:
            search_box = self.driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true'][data-testid='chat-list-search']")
            search_box.click()
            search_box.clear()
            search_box.send_keys(self.target_contact)
            time.sleep(2)
        except Exception as e:
            print(f"Could not search for contact: {e}")
    
    def get_latest_messages(self):
        """Get all recent incoming messages"""
        try:
            # Multiple selectors for different message types
            message_selectors = [
                "div[data-testid='conversation-panel-messages'] div.message-in span.selectable-text",
                "div.message-in span[dir='ltr']",
                "div.message-in div._11JPr.selectable-text.copyable-text span",
                "div.message-in span.selectable-text span"
            ]
            
            all_messages = []
            for selector in message_selectors:
                try:
                    found_messages = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if found_messages:
                        # Get the last 5 messages to catch multiple new ones
                        recent_messages = found_messages[-5:] if len(found_messages) > 5 else found_messages
                        all_messages = recent_messages
                        break
                except:
                    continue
            
            return all_messages
            
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
    
    def send_message(self, message):
        """Send a message with faster typing"""
        try:
            # Find message input box with multiple selectors
            input_selectors = [
                "div[contenteditable='true'][data-testid='conversation-compose-box-input']",
                "div[contenteditable='true'][title='Type a message']",
                "div[contenteditable='true'][aria-label='Type a message']"
            ]
            
            msg_box = None
            for selector in input_selectors:
                try:
                    msg_box = WebDriverWait(self.driver, 5).until(  # Reduced from 10 to 5
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not msg_box:
                print("Could not find message input box")
                return False
            
            msg_box.click()
            
            # Faster typing - just send the whole message at once
            msg_box.clear()
            msg_box.send_keys(message)
            
            time.sleep(random.uniform(0.3, 0.8))  # Reduced delay
            msg_box.send_keys(Keys.ENTER)
            
            print(f"Sent: {message}")
            return True
            
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    def get_message_id(self, message_element):
        """Get a unique identifier for the message"""
        try:
            # Try to get timestamp or other unique attribute
            parent = message_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'message-in')][1]")
            return parent.get_attribute('data-id') or parent.get_attribute('innerHTML')[:50]
        except:
            return message_element.text[:50]  # Fallback to text content
    
    def run(self, auto_replies=None):
        """Main bot loop"""
        if auto_replies is None:
            auto_replies = [
                "Thanks for your message! I'll get back to you soon.",
                "Got it! 👍",
                "I'm currently away but I saw your message.",
                "Auto-reply: I'll respond when I'm back online."
            ]
        
        if not self.wait_for_whatsapp_load():
            return
        
        if not self.find_and_open_chat():
            return
        
        print("Bot is running... Press Ctrl+C to stop")
        
        try:
            while True:
                messages = self.get_latest_messages()
                
                if messages:
                    # Process all new messages
                    for message_element in messages:
                        message_id = self.get_message_id(message_element)
                        message_text = message_element.text.strip()
                        
                        # Skip if we've already processed this message
                        if message_id not in self.processed_messages and message_text:
                            print(f"New message: {message_text}")
                            self.processed_messages.add(message_id)
                            
                            # Shorter delay for faster response
                            delay = random.uniform(1, 3)  # Reduced from 2-8 seconds
                            print(f"Replying in {delay:.1f} seconds...")
                            time.sleep(delay)
                            
                            # Send random auto-reply
                            reply = random.choice(auto_replies)
                            if self.send_message(reply):
                                # Shorter wait between messages
                                time.sleep(random.uniform(1, 2))  # Reduced from 3-7 seconds
                
                # Check more frequently
                time.sleep(random.uniform(1, 2))  # Reduced from 2-5 seconds
                
        except KeyboardInterrupt:
            print("\nBot stopped by user")
        except Exception as e:
            print(f"Bot error: {e}")
        finally:
            self.cleanup()
    
    def debug_page_state(self):
        """Debug function to see what's on the page"""
        try:
            print(f"Current URL: {self.driver.current_url}")
            print(f"Page title: {self.driver.title}")
            
            # Check for common WhatsApp elements
            common_elements = {
                "QR Code Canvas": "canvas",
                "QR Code Container": "[data-testid='qr-code']",
                "Chat List": "[data-testid='chat-list']", 
                "Main Container": "div[id='app']",
                "WhatsApp Logo": "div._2EoyP",
                "Phone Input": "input[type='tel']",
                "Any Canvas": "canvas",
                "Any Button": "button",
                "Any Div": "div"
            }
            
            for name, selector in common_elements.items():
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"{name}: {len(elements)} found")
                
        except Exception as e:
            print(f"Debug error: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

# Usage
if __name__ == "__main__":
    # Configuration
    TARGET_CONTACT = "Friend Name"  # Replace with actual contact name
    
    # Custom auto-replies (optional)
    CUSTOM_REPLIES = [
        "Thanks for the message! I'll respond soon 😊",
        "Got your message! Talk to you later.",
        "Auto-reply: I'm currently busy but I saw your message.",
    ]
    
    # Create and run bot
    bot = WhatsAppBot(TARGET_CONTACT)
    bot.run(CUSTOM_REPLIES)
