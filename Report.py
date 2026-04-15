"""
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                              ║
║                    █████╗ ███╗   ██╗ █████╗ ███╗   ███╗██╗██╗  ██╗ █████╗                  ║
║                   ██╔══██╗████╗  ██║██╔══██╗████╗ ████║██║██║  ██║██╔══██╗                 ║
║                   ███████║██╔██╗ ██║███████║██╔████╔██║██║███████║███████║                 ║
║                   ██╔══██║██║╚██╗██║██╔══██║██║╚██╔╝██║██║██╔══██║██╔══██║                 ║
║                   ██║  ██║██║ ╚████║██║  ██║██║ ╚═╝ ██║██║██║  ██║██║  ██║                 ║
║                   ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝                 ║
║                                                                                              ║
║                    ███████╗██████╗  ██████╗ ███████╗███████╗███╗   ██╗                     ║
║                    ██╔════╝██╔══██╗██╔═══██╗██╔════╝██╔════╝████╗  ██║                     ║
║                    █████╗  ██████╔╝██║   ██║█████╗  █████╗  ██╔██╗ ██║                     ║
║                    ██╔══╝  ██╔══██╗██║   ██║██╔══╝  ██╔══╝  ██║╚██╗██║                     ║
║                    ██║     ██║  ██║╚██████╔╝██║     ███████╗██║ ╚████║                     ║
║                    ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝                     ║
║                                                                                              ║
║                         TELEGRAM ULTIMATE REPORT BOT v5.0                                    ║
║                                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import os
import sys
import json
import random
import time
import uuid
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# ============ TELEGRAM IMPORTS ============
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.types import (
    InputReportReasonSpam,
    InputReportReasonViolence,
    InputReportReasonPornography,
    InputReportReasonChildAbuse,
    InputReportReasonCopyright,
    InputReportReasonFake,
    InputReportReasonGeoIrrelevant,
    InputReportReasonIllegalDrugs,
    InputReportReasonPersonalDetails,
    InputReportReasonOther
)

# Fixed imports for latest Telethon version
from telethon.errors import FloodWaitError, PeerIdInvalid, RPCError
try:
    from telethon.errors import UsernameNotOccupiedError
except ImportError:
    try:
        from telethon.errors.rpcerrorlist import UsernameNotOccupiedError
    except ImportError:
        # Fallback for older versions
        from telethon.errors import UsernameNotOccupied as UsernameNotOccupiedError

# ============ BOT IMPORTS ============
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes, ConversationHandler
)
from telegram.constants import ParseMode

# ============ CONFIGURATION - EDIT THESE ============
BOT_TOKEN = "8629322618:AAHfdHL9Y_BaFw8OZQpNSDhQEDj7izwzCyo"  # Get from @BotFather
OWNER_ID = 1124377372  # Your Telegram ID

# IMPORTANT: Get your own API credentials from https://my.telegram.org/apps
API_ID = 33480228  # Replace with your API ID
API_HASH = "90b04f615398d5991d24be911e89d4e6"  # Replace with your API Hash

# File paths
SESSIONS_FILE = "bot_sessions.json"
STATS_FILE = "bot_stats.json"
USERS_FILE = "bot_users.json"
REPORT_LOG = "bot_reports.log"

# States for conversation
WAITING_PHONE, WAITING_CODE, WAITING_PASSWORD, WAITING_SESSION_STRING = range(4)
WAITING_TARGET, WAITING_CATEGORY, WAITING_COUNT = range(10, 13)
WAITING_BOT_TARGET, WAITING_BOT_CATEGORY, WAITING_BOT_COUNT = range(20, 23)
WAITING_GROUP_LINK, WAITING_GROUP_CATEGORY, WAITING_GROUP_COUNT = range(30, 33)
WAITING_MESSAGE_LINK, WAITING_MESSAGE_CATEGORY, WAITING_MESSAGE_COUNT = range(40, 43)
WAITING_GRANT_ID, WAITING_REVOKE_ID = range(50, 52)

# ============ REPORT CATEGORIES ============
REPORT_CATEGORIES = {
    "spam": {"name": "📩 Spam", "reason": InputReportReasonSpam()},
    "violence": {"name": "💥 Violence", "reason": InputReportReasonViolence()},
    "child_abuse": {"name": "⚠️ Child Abuse", "reason": InputReportReasonChildAbuse()},
    "pornography": {"name": "🔞 Pornography", "reason": InputReportReasonPornography()},
    "copyright": {"name": "©️ Copyright", "reason": InputReportReasonCopyright()},
    "geo_irrelevant": {"name": "🌍 Geo Irrelevant", "reason": InputReportReasonGeoIrrelevant()},
    "fake": {"name": "🎭 Fake", "reason": InputReportReasonFake()},
    "drugs": {"name": "💊 Drugs", "reason": InputReportReasonIllegalDrugs()},
    "personal_details": {"name": "🔐 Personal Details", "reason": InputReportReasonPersonalDetails()},
    "other": {"name": "🚫 Other", "reason": InputReportReasonOther()}
}

# ============ DATA MANAGERS ============
class DataManager:
    def __init__(self):
        self.sessions = {}
        self.stats = {}
        self.users = {}
        self.load_all()
    
    def load_all(self):
        """Load all data from files"""
        try:
            if os.path.exists(SESSIONS_FILE):
                with open(SESSIONS_FILE, 'r') as f:
                    self.sessions = json.load(f)
        except: pass
        
        try:
            if os.path.exists(STATS_FILE):
                with open(STATS_FILE, 'r') as f:
                    self.stats = json.load(f)
        except: pass
        
        try:
            if os.path.exists(USERS_FILE):
                with open(USERS_FILE, 'r') as f:
                    self.users = json.load(f)
        except: pass
        
        # Initialize if empty
        if not self.stats:
            self.stats = {
                "total_reports": 0,
                "successful_reports": 0,
                "failed_reports": 0,
                "reports_by_category": {},
                "reports_by_target": {}
            }
    
    def save_sessions(self):
        with open(SESSIONS_FILE, 'w') as f:
            json.dump(self.sessions, f, indent=2)
    
    def save_stats(self):
        with open(STATS_FILE, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def save_users(self):
        with open(USERS_FILE, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def add_session(self, user_id: int, phone: str, session_string: str, session_type: str):
        if str(user_id) not in self.sessions:
            self.sessions[str(user_id)] = []
        self.sessions[str(user_id)].append({
            "phone": phone,
            "session_string": session_string,
            "type": session_type,
            "added": str(datetime.now()),
            "reports_sent": 0,
            "success_rate": 100
        })
        self.save_sessions()
        return True
    
    def get_sessions(self, user_id: int) -> List[Dict]:
        return self.sessions.get(str(user_id), [])
    
    def remove_session(self, user_id: int, index: int) -> bool:
        sessions = self.get_sessions(user_id)
        if 0 <= index < len(sessions):
            self.sessions[str(user_id)].pop(index)
            self.save_sessions()
            return True
        return False
    
    def update_session_stats(self, user_id: int, phone: str, success: bool):
        for s in self.sessions.get(str(user_id), []):
            if s['phone'] == phone:
                s['reports_sent'] = s.get('reports_sent', 0) + 1
                if not success:
                    s['success_rate'] = max(0, s.get('success_rate', 100) - 5)
                self.save_sessions()
                break
    
    def update_stats(self, category: str, target: str, success: bool):
        self.stats["total_reports"] += 1
        if success:
            self.stats["successful_reports"] += 1
        else:
            self.stats["failed_reports"] += 1
        
        if category not in self.stats["reports_by_category"]:
            self.stats["reports_by_category"][category] = 0
        self.stats["reports_by_category"][category] += 1
        
        self.save_stats()
    
    def get_stats(self, user_id: int = None) -> Dict:
        sessions = self.get_sessions(user_id) if user_id else []
        return {
            "total": self.stats["total_reports"],
            "successful": self.stats["successful_reports"],
            "failed": self.stats["failed_reports"],
            "success_rate": (self.stats["successful_reports"] / max(1, self.stats["total_reports"])) * 100,
            "user_sessions": len(sessions),
            "user_reports": sum(s.get('reports_sent', 0) for s in sessions)
        }
    
    def add_user(self, user_id: int, username: str = None):
        if str(user_id) not in self.users:
            self.users[str(user_id)] = {
                "user_id": user_id,
                "username": username,
                "first_seen": str(datetime.now()),
                "authorized": user_id == OWNER_ID
            }
            self.save_users()
    
    def is_authorized(self, user_id: int) -> bool:
        if user_id == OWNER_ID:
            return True
        return self.users.get(str(user_id), {}).get("authorized", False)
    
    def grant_access(self, user_id: int):
        self.users[str(user_id)] = self.users.get(str(user_id), {})
        self.users[str(user_id)]["authorized"] = True
        self.users[str(user_id)]["granted_by"] = OWNER_ID
        self.users[str(user_id)]["granted_at"] = str(datetime.now())
        self.save_users()
    
    def revoke_access(self, user_id: int):
        if str(user_id) in self.users:
            self.users[str(user_id)]["authorized"] = False
            self.save_users()

# ============ REPORT ENGINE ============
class ReportEngine:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.api_id = API_ID
        self.api_hash = API_HASH
    
    async def send_report(self, session_string: str, target: str, target_type: str, 
                          category: Dict, message_id: int = None) -> Tuple[bool, str]:
        """Send real report using Telegram API"""
        client = None
        try:
            client = TelegramClient(StringSession(session_string), self.api_id, self.api_hash)
            await client.connect()
            
            if not await client.is_user_authorized():
                return False, "Session not authorized"
            
            # Get entity
            try:
                if target_type == "message":
                    entity = await client.get_entity(target)
                else:
                    entity = await client.get_entity(target)
            except Exception as e:
                error_msg = str(e).lower()
                if "username" in error_msg or "not found" in error_msg:
                    return False, "Username not found"
                elif "invalid" in error_msg:
                    return False, "Invalid peer ID"
                else:
                    return False, f"Cannot find target: {str(e)[:30]}"
            
            report_id = uuid.uuid4().hex[:8].upper()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            
            report_text = f"""REPORT #{report_id}
Target: {target}
Type: {target_type.upper()}
Time: {timestamp}
Category: {category['name']}

This content violates Telegram Terms of Service. Please review and take action.

Report ID: {report_id}"""
            
            # Truncate to 200 chars as per Telegram API limit
            report_text = report_text[:200]
            
            # ==== REAL TELEGRAM API CALL ====
            if target_type == "message" and message_id:
                await client(ReportRequest(
                    peer=entity,
                    id=[message_id],
                    reason=category['reason'],
                    message=report_text
                ))
            else:
                await client(ReportPeerRequest(
                    peer=entity,
                    reason=category['reason'],
                    message=report_text
                ))
            
            await client.disconnect()
            return True, report_id
            
        except FloodWaitError as e:
            if client:
                await client.disconnect()
            wait_time = min(e.seconds, 60)
            await asyncio.sleep(wait_time)
            return False, f"Flood wait {wait_time}s"
        except RPCError as e:
            if client:
                await client.disconnect()
            return False, f"RPC Error: {str(e)[:30]}"
        except Exception as e:
            if client:
                await client.disconnect()
            return False, str(e)[:30]
        finally:
            if client:
                try:
                    await client.disconnect()
                except:
                    pass
    
    async def run_reports(self, user_id: int, target: str, target_type: str, 
                          category_key: str, report_count: int, message_id: int = None) -> Dict:
        """Run multiple reports using user's sessions"""
        
        sessions = self.data_manager.get_sessions(user_id)
        if not sessions:
            return {"success": 0, "failed": 0, "total": 0, "error": "No sessions"}
        
        category = REPORT_CATEGORIES[category_key]
        results = {"success": 0, "failed": 0, "total": report_count, "reports": []}
        
        session_index = 0
        sent = 0
        
        while sent < report_count:
            session = sessions[session_index % len(sessions)]
            phone = session['phone']
            session_string = session['session_string']
            
            success, report_id = await self.send_report(
                session_string, target, target_type, category, message_id
            )
            
            if success:
                results["success"] += 1
                self.data_manager.update_session_stats(user_id, phone, True)
                self.data_manager.update_stats(category['name'], target, True)
                # Log successful report
                with open(REPORT_LOG, 'a') as f:
                    f.write(f"{datetime.now()} | SUCCESS | {user_id} | {target} | {category['name']} | {report_id}\n")
            else:
                results["failed"] += 1
                self.data_manager.update_session_stats(user_id, phone, False)
                self.data_manager.update_stats(category['name'], target, False)
                # Log failed report
                with open(REPORT_LOG, 'a') as f:
                    f.write(f"{datetime.now()} | FAILED | {user_id} | {target} | {category['name']} | {report_id}\n")
            
            sent += 1
            session_index += 1
            
            # Delay between reports to avoid flood limits
            await asyncio.sleep(random.uniform(3, 5))
        
        return results

# ============ BOT HANDLERS ============
class ReportBot:
    def __init__(self):
        self.data_manager = DataManager()
        self.report_engine = ReportEngine(self.data_manager)
        self.application = None
        self.temp_data = {}
    
    def get_main_keyboard(self, user_id: int) -> InlineKeyboardMarkup:
        is_owner = user_id == OWNER_ID
        keyboard = [
            [InlineKeyboardButton("📢 Send Report", callback_data="report")],
            [InlineKeyboardButton("📱 Account / Session", callback_data="account_session")],
            [InlineKeyboardButton("📊 Statistics", callback_data="stats")],
            [InlineKeyboardButton("❓ Help", callback_data="help")],
        ]
        if is_owner:
            keyboard.append([InlineKeyboardButton("👑 Admin Panel", callback_data="admin_panel")])
        return InlineKeyboardMarkup(keyboard)
    
    def get_account_session_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("📱 My Sessions", callback_data="my_sessions")],
            [InlineKeyboardButton("➕ Add Account (Phone)", callback_data="add_phone_account")],
            [InlineKeyboardButton("📋 Add Session String", callback_data="add_session_string")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_report_type_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("👤 User Account", callback_data="report_user")],
            [InlineKeyboardButton("🤖 Bot", callback_data="report_bot")],
            [InlineKeyboardButton("👥 Group/Channel", callback_data="report_group")],
            [InlineKeyboardButton("💬 Specific Message", callback_data="report_message")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def get_category_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = []
        categories = list(REPORT_CATEGORIES.keys())
        for i in range(0, len(categories), 2):
            row = []
            for j in range(2):
                if i + j < len(categories):
                    cat = categories[i + j]
                    row.append(InlineKeyboardButton(
                        REPORT_CATEGORIES[cat]['name'], 
                        callback_data=f"cat_{cat}"
                    ))
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main")])
        return InlineKeyboardMarkup(keyboard)
    
    def get_admin_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton("➕ Grant Access", callback_data="admin_grant")],
            [InlineKeyboardButton("➖ Revoke Access", callback_data="admin_revoke")],
            [InlineKeyboardButton("📊 Global Stats", callback_data="admin_stats")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        self.data_manager.add_user(user.id, user.username)
        
        if not self.data_manager.is_authorized(user.id):
            await update.message.reply_text(
                f"❌ Access Denied!\n\nYour ID: `{user.id}`\nContact: @WORLDBANNER",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        welcome_text = f"""🎉 **Welcome to Anamika Report Bot**

🆔 **Your ID:** `{user.id}`
👤 **Username:** @{user.username or 'No username'}

**✅ Features:**
• Real Telegram API Reports
• Multi-Account Support  
• 10 Report Categories
• Detailed Statistics

**Select an option below:**
"""
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=self.get_main_keyboard(user.id),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user = update.effective_user
        await query.answer()
        
        if not self.data_manager.is_authorized(user.id) and user.id != OWNER_ID:
            await query.edit_message_text("❌ Access Denied!")
            return
        
        data = query.data
        
        # ============ MAIN MENU ============
        if data == "back_to_main":
            await query.edit_message_text(
                f"🎉 **Main Menu**\n\n🆔 ID: `{user.id}`\n\nSelect an option:",
                reply_markup=self.get_main_keyboard(user.id),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ============ ACCOUNT/SESSION ============
        elif data == "account_session":
            sessions = self.data_manager.get_sessions(user.id)
            text = f"""📱 **Session Management**

📲 **Your Sessions:** {len(sessions)}

Add your Telegram sessions to send reports."""
            await query.edit_message_text(
                text,
                reply_markup=self.get_account_session_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == "my_sessions":
            sessions = self.data_manager.get_sessions(user.id)
            if not sessions:
                await query.edit_message_text(
                    "📭 **No Sessions Found!**\n\nAdd a session to start reporting.",
                    reply_markup=self.get_account_session_keyboard(),
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            text = "📱 **Your Sessions:**\n\n"
            for i, s in enumerate(sessions, 1):
                text += f"{i}. 📞 `{s['phone']}`\n"
                text += f"   📨 Reports: {s.get('reports_sent', 0)}\n"
                text += f"   📈 Rate: {s.get('success_rate', 100):.0f}%\n\n"
            
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="account_session")]]
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == "add_phone_account":
            context.user_data["waiting_for"] = "phone"
            await query.edit_message_text(
                "📞 **Add Account via Phone Number**\n\n"
                "Send your phone number with country code:\n"
                "Example: `+919876543210`\n\n"
                "⚠️ Make sure you have access to this number for OTP verification.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == "add_session_string":
            context.user_data["waiting_for"] = "session_string"
            await query.edit_message_text(
                "📋 **Add Session String**\n\n"
                "Send your Telethon session string.\n\n"
                "Get it from @SessionStringBot\n\n"
                "⚠️ Only valid, authorized sessions will be accepted.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ============ REPORT ============
        elif data == "report":
            sessions = self.data_manager.get_sessions(user.id)
            if not sessions:
                await query.edit_message_text(
                    "⛔ **No Sessions Available!**\n\n"
                    "You need to add your own sessions first.\n\n"
                    "Go to 📱 **Account / Session** → ➕ **Add Account**",
                    reply_markup=self.get_account_session_keyboard(),
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            await query.edit_message_text(
                "🎯 **Select Target Type**\n\n"
                "What would you like to report?",
                reply_markup=self.get_report_type_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ============ USER REPORT ============
        elif data == "report_user":
            context.user_data["report_type"] = "user"
            context.user_data["waiting_for"] = "target"
            await query.edit_message_text(
                "👤 **Report User**\n\n"
                "Send the target username:\n"
                "Example: `@username` or `username`\n\n"
                "⚠️ Make sure the username exists.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ============ BOT REPORT ============
        elif data == "report_bot":
            context.user_data["report_type"] = "bot"
            context.user_data["waiting_for"] = "target"
            await query.edit_message_text(
                "🤖 **Report Bot**\n\n"
                "Send the bot username:\n"
                "Example: `@botusername`\n\n"
                "⚠️ Only public bots can be reported.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ============ GROUP REPORT ============
        elif data == "report_group":
            context.user_data["report_type"] = "group"
            context.user_data["waiting_for"] = "target"
            await query.edit_message_text(
                "👥 **Report Group/Channel**\n\n"
                "Send the public group/channel link:\n"
                "Example: `https://t.me/username`\n\n"
                "⚠️ Only public groups/channels are supported.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ============ MESSAGE REPORT ============
        elif data == "report_message":
            context.user_data["report_type"] = "message"
            context.user_data["waiting_for"] = "target"
            await query.edit_message_text(
                "💬 **Report Specific Message**\n\n"
                "Send the message link:\n"
                "Example: `https://t.me/channelname/123`\n\n"
                "⚠️ The link must be from a public channel/group.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ============ CATEGORY SELECTION ============
        elif data.startswith("cat_"):
            category = data.replace("cat_", "")
            context.user_data["category"] = category
            context.user_data["waiting_for"] = "count"
            await query.edit_message_text(
                f"✅ **Selected Category:** {REPORT_CATEGORIES[category]['name']}\n\n"
                f"🔢 **How many reports to send?** (1-100)\n\n"
                f"⚠️ More reports = higher chance of action, but also higher flood risk.\n\n"
                f"_Send a number only_",
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ============ STATS ============
        elif data == "stats":
            stats = self.data_manager.get_stats(user.id)
            sessions = self.data_manager.get_sessions(user.id)
            
            text = f"""📊 **Your Statistics**

━━━━━━━━━━━━━━━━━━━━━━
📈 **Your Reports:**
├ Total Sent: `{stats['user_reports']}`
├ Successful: `{stats['successful']}`
├ Failed: `{stats['failed']}`
└ Your Rate: `{stats['success_rate']:.1f}%`

📱 **Active Sessions:** `{len(sessions)}`

━━━━━━━━━━━━━━━━━━━━━━
🌍 **Global Statistics:**
├ Total Reports: `{stats['total']}`
├ Global Rate: `{stats['success_rate']:.1f}%`
└ Categories: `{len(self.data_manager.stats.get('reports_by_category', {}))}`

━━━━━━━━━━━━━━━━━━━━━━
👑 **Bot Owner:** @WORLDBANNER"""
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]]),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ============ HELP ============
        elif data == "help":
            help_text = """❓ **Report Bot Help**

**How to use:**

1️⃣ **Add a Session** (Required first!)
   - Go to Account/Session
   - Add via phone number or session string

2️⃣ **Send Reports**
   - Click "Send Report"
   - Select target type
   - Enter username/link
   - Choose category
   - Set number of reports
   - Confirm

**Target Types:**
• 👤 User - Report a user account
• 🤖 Bot - Report a bot  
• 👥 Group - Report group/channel
• 💬 Message - Report specific post

**Report Categories:**
Spam | Violence | Child Abuse | Pornography
Copyright | Fake | Drugs | Personal Details

**⚠️ Important Notes:**
• Reports go to Telegram moderation
• Real accounts = real reports
• Don't spam or abuse the system
• Your accounts may get limited

**Support:** @WORLDBANNER"""
            
            await query.edit_message_text(
                help_text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]]),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ============ ADMIN PANEL ============
        elif data == "admin_panel":
            if user.id != OWNER_ID:
                await query.answer("❌ Owner only!", show_alert=True)
                return
            await query.edit_message_text(
                "👑 **Admin Panel**\n\nSelect an option:",
                reply_markup=self.get_admin_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == "admin_grant":
            if user.id != OWNER_ID:
                return
            context.user_data["waiting_for"] = "grant_id"
            await query.edit_message_text(
                "➕ **Grant Access**\n\nSend the user ID to grant access:\n\nExample: `123456789`",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == "admin_revoke":
            if user.id != OWNER_ID:
                return
            context.user_data["waiting_for"] = "revoke_id"
            await query.edit_message_text(
                "➖ **Revoke Access**\n\nSend the user ID to revoke access:\n\nExample: `123456789`",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == "admin_stats":
            if user.id != OWNER_ID:
                return
            stats = self.data_manager.get_stats()
            users_count = len(self.data_manager.users)
            authorized_count = sum(1 for u in self.data_manager.users.values() if u.get('authorized', False))
            
            text = f"""👑 **Global Statistics**

━━━━━━━━━━━━━━━━━━━━━━
📊 **Reports:**
├ Total: `{stats['total']}`
├ Successful: `{stats['successful']}`
├ Failed: `{stats['failed']}`
└ Rate: `{stats['success_rate']:.1f}%`

👥 **Users:**
├ Total Users: `{users_count}`
├ Authorized: `{authorized_count}`
└ Unauthorized: `{users_count - authorized_count}`

📁 **Sessions File:** {os.path.exists(SESSIONS_FILE)}
📊 **Stats File:** {os.path.exists(STATS_FILE)}
👥 **Users File:** {os.path.exists(USERS_FILE)}

━━━━━━━━━━━━━━━━━━━━━━"""
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]),
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        text = update.message.text.strip()
        waiting_for = context.user_data.get("waiting_for")
        
        if not self.data_manager.is_authorized(user.id) and user.id != OWNER_ID:
            await update.message.reply_text("❌ Access Denied!")
            return
        
        # ============ PHONE NUMBER INPUT ============
        if waiting_for == "phone":
            if not text.startswith('+'):
                await update.message.reply_text(
                    "❌ Invalid phone number!\n\nSend with country code:\nExample: `+919876543210`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            context.user_data["phone"] = text
            context.user_data["waiting_for"] = "code"
            
            # Send code request
            status_msg = await update.message.reply_text(
                f"📲 **Sending OTP to** `{text}`...\n\nPlease wait...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Create temporary client for login
            try:
                temp_client = TelegramClient(f"temp_{user.id}_{int(time.time())}", API_ID, API_HASH)
                await temp_client.connect()
                await temp_client.send_code_request(text)
                context.user_data["temp_client"] = temp_client
                await status_msg.edit_text(
                    "✅ **Code sent!**\n\nEnter the verification code you received in Telegram:",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                await status_msg.edit_text(f"❌ Error: {str(e)[:100]}")
                context.user_data.pop("waiting_for", None)
        
        # ============ CODE INPUT ============
        elif waiting_for == "code":
            code = text
            phone = context.user_data.get("phone")
            temp_client = context.user_data.get("temp_client")
            
            if not temp_client:
                await update.message.reply_text("❌ Session expired. Please start over.")
                context.user_data.clear()
                return
            
            try:
                await temp_client.sign_in(phone, code)
                me = await temp_client.get_me()
                session_string = temp_client.session.save()
                await temp_client.disconnect()
                
                # Save session
                self.data_manager.add_session(user.id, me.phone or phone, session_string, "phone")
                
                await update.message.reply_text(
                    f"✅ **Account Added Successfully!**\n\n"
                    f"👤 **Name:** {me.first_name}\n"
                    f"📞 **Phone:** {me.phone or phone}\n"
                    f"🆔 **ID:** {me.id}\n\n"
                    f"You can now start sending reports!",
                    reply_markup=self.get_main_keyboard(user.id),
                    parse_mode=ParseMode.MARKDOWN
                )
                context.user_data.clear()
                
            except Exception as e:
                error_msg = str(e).lower()
                if "password" in error_msg or "2fa" in error_msg:
                    context.user_data["waiting_for"] = "password"
                    await update.message.reply_text(
                        "🔐 **2FA Required!**\n\nEnter your Two-Factor Authentication password:",
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await update.message.reply_text(f"❌ Error: {str(e)[:100]}")
                    context.user_data.clear()
        
        # ============ PASSWORD INPUT ============
        elif waiting_for == "password":
            password = text
            temp_client = context.user_data.get("temp_client")
            phone = context.user_data.get("phone")
            
            if not temp_client:
                await update.message.reply_text("❌ Session expired. Please start over.")
                context.user_data.clear()
                return
            
            try:
                await temp_client.sign_in(password=password)
                me = await temp_client.get_me()
                session_string = temp_client.session.save()
                await temp_client.disconnect()
                
                self.data_manager.add_session(user.id, me.phone or phone, session_string, "phone")
                
                await update.message.reply_text(
                    f"✅ **Account Added Successfully!**\n\n"
                    f"👤 **Name:** {me.first_name}\n"
                    f"📞 **Phone:** {me.phone or phone}\n"
                    f"🆔 **ID:** {me.id}\n\n"
                    f"You can now start sending reports!",
                    reply_markup=self.get_main_keyboard(user.id),
                    parse_mode=ParseMode.MARKDOWN
                )
                context.user_data.clear()
                
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {str(e)[:100]}")
                context.user_data.clear()
        
        # ============ SESSION STRING INPUT ============
        elif waiting_for == "session_string":
            session_string = text
            
            # Validate session
            status_msg = await update.message.reply_text("🔍 Validating session string...")
            
            try:
                client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
                await client.connect()
                
                if await client.is_user_authorized():
                    me = await client.get_me()
                    await client.disconnect()
                    
                    self.data_manager.add_session(user.id, me.phone or f"user_{me.id}", session_string, "string")
                    
                    await status_msg.edit_text(
                        f"✅ **Session Added Successfully!**\n\n"
                        f"👤 **User:** {me.first_name}\n"
                        f"📞 **Phone:** {me.phone or 'Hidden'}\n"
                        f"🆔 **ID:** {me.id}\n\n"
                        f"You can now start sending reports!",
                        reply_markup=self.get_main_keyboard(user.id),
                        parse_mode=ParseMode.MARKDOWN
                    )
                else:
                    await status_msg.edit_text("❌ Invalid session string! Session not authorized.")
            except Exception as e:
                await status_msg.edit_text(f"❌ Invalid session string: {str(e)[:100]}")
            
            context.user_data.clear()
        
        # ============ TARGET INPUT ============
        elif waiting_for == "target":
            report_type = context.user_data.get("report_type")
            target = text
            
            # Validate target based on type
            if report_type == "message":
                # Extract channel and message ID from link
                match = re.search(r't\.me/([^/]+)/(\d+)', target)
                if not match:
                    await update.message.reply_text(
                        "❌ Invalid message link!\n\n"
                        "Send a valid post link:\n"
                        "Example: `https://t.me/channelname/123`",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    return
                context.user_data["channel_username"] = match.group(1)
                context.user_data["message_id"] = int(match.group(2))
                context.user_data["target"] = match.group(1)
            
            elif report_type == "group":
                # Extract group username from link
                match = re.search(r't\.me/([^/]+)', target)
                if match:
                    context.user_data["target"] = match.group(1)
                else:
                    context.user_data["target"] = target.lstrip('@')
            
            else:
                context.user_data["target"] = target.lstrip('@')
            
            context.user_data["waiting_for"] = "category_selection"
            
            await update.message.reply_text(
                f"🎯 **Target:** `{target}`\n\n"
                f"**Select report category:**",
                reply_markup=self.get_category_keyboard(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        # ============ COUNT INPUT ============
        elif waiting_for == "count":
            try:
                count = int(text)
                if count < 1 or count > 100:
                    await update.message.reply_text("❌ Please enter a number between 1 and 100!")
                    return
            except ValueError:
                await update.message.reply_text("❌ Please enter a valid number!")
                return
            
            target = context.user_data.get("target")
            report_type = context.user_data.get("report_type")
            category = context.user_data.get("category")
            message_id = context.user_data.get("message_id")
            
            sessions_count = len(self.data_manager.get_sessions(user.id))
            
            # Confirm
            confirm_text = f"""📋 **Report Confirmation**

🎯 **Target:** `{target}`
📌 **Type:** {report_type.upper()}
📂 **Category:** {REPORT_CATEGORIES[category]['name']}
🔢 **Reports:** {count}
👥 **Sessions:** {sessions_count}

⚠️ **Important:**
• Reports sent via REAL Telegram API
• Each report uses one session
• May take 1-2 minutes to complete
• Don't close this chat

✅ **Start sending reports?** (Reply with 'yes' to confirm)"""
            
            context.user_data["confirmed_count"] = count
            context.user_data["waiting_for"] = "confirm"
            
            await update.message.reply_text(confirm_text, parse_mode=ParseMode.MARKDOWN)
        
        # ============ CONFIRMATION ============
        elif waiting_for == "confirm":
            if text.lower() != 'yes':
                await update.message.reply_text("❌ Report cancelled!")
                context.user_data.clear()
                return
            
            target = context.user_data.get("target")
            report_type = context.user_data.get("report_type")
            category = context.user_data.get("category")
            count = context.user_data.get("confirmed_count")
            message_id = context.user_data.get("message_id")
            
            status_msg = await update.message.reply_text(
                "🚀 **Sending Reports...**\n\n"
                "⏳ 0% complete\n"
                "📡 Sending to Telegram moderation...\n\n"
                "_Please wait, this may take a moment_",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Run reports
            results = await self.report_engine.run_reports(
                user.id, target, report_type, category, count, message_id
            )
            
            success_rate = (results['success'] / max(1, results['total'])) * 100
            
            if results.get('error'):
                result_text = f"""❌ **Report Failed!**

**Error:** {results['error']}

📋 **Please add sessions first!**
Go to Account/Session → Add Account"""
            else:
                result_text = f"""✅ **Report Batch Completed!**

━━━━━━━━━━━━━━━━━━━━━━
📊 **Results:**
├ ✅ Successful: `{results['success']}`
├ ❌ Failed: `{results['failed']}`
├ 📊 Total Sent: `{results['total']}`
└ 📈 Success Rate: `{success_rate:.1f}%`

🎯 **Target:** `{target}`
📂 **Category:** {REPORT_CATEGORIES[category]['name']}
━━━━━━━━━━━━━━━━━━━━━━

✅ Reports sent to Telegram moderation team!
📝 Results logged for tracking

_Note: Results depend on Telegram's moderation system_"""
            
            await status_msg.edit_text(result_text, parse_mode=ParseMode.MARKDOWN)
            context.user_data.clear()
        
        # ============ ADMIN GRANT ============
        elif waiting_for == "grant_id":
            if user.id != OWNER_ID:
                return
            try:
                target_id = int(text)
                self.data_manager.grant_access(target_id)
                await update.message.reply_text(f"✅ Access granted to `{target_id}`!\n\nThey can now use the bot.", parse_mode=ParseMode.MARKDOWN)
            except:
                await update.message.reply_text("❌ Invalid user ID! Send a number only.")
            context.user_data.clear()
        
        # ============ ADMIN REVOKE ============
        elif waiting_for == "revoke_id":
            if user.id != OWNER_ID:
                return
            try:
                target_id = int(text)
                self.data_manager.revoke_access(target_id)
                await update.message.reply_text(f"✅ Access revoked from `{target_id}`!", parse_mode=ParseMode.MARKDOWN)
            except:
                await update.message.reply_text("❌ Invalid user ID! Send a number only.")
            context.user_data.clear()
    
    async def grant_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id != OWNER_ID:
            await update.message.reply_text("❌ Owner only!")
            return
        
        args = context.args
        if not args:
            await update.message.reply_text("Usage: /grant <user_id>\n\nExample: `/grant 123456789`", parse_mode=ParseMode.MARKDOWN)
            return
        
        try:
            target_id = int(args[0])
            self.data_manager.grant_access(target_id)
            await update.message.reply_text(f"✅ Access granted to `{target_id}`!", parse_mode=ParseMode.MARKDOWN)
        except:
            await update.message.reply_text("❌ Invalid user ID!")
    
    async def revoke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if user.id != OWNER_ID:
            await update.message.reply_text("❌ Owner only!")
            return
        
        args = context.args
        if not args:
            await update.message.reply_text("Usage: /revoke <user_id>\n\nExample: `/revoke 123456789`", parse_mode=ParseMode.MARKDOWN)
            return
        
        try:
            target_id = int(args[0])
            self.data_manager.revoke_access(target_id)
            await update.message.reply_text(f"✅ Access revoked from `{target_id}`!", parse_mode=ParseMode.MARKDOWN)
        except:
            await update.message.reply_text("❌ Invalid user ID!")
    
    async def run(self):
        """Run the bot"""
        # Check configuration
        if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            print("\n" + "="*60)
            print("❌ ERROR: Please configure your BOT_TOKEN!")
            print("="*60)
            print("1. Go to @BotFather on Telegram")
            print("2. Create a new bot: /newbot")
            print("3. Copy the bot token")
            print("4. Replace 'YOUR_BOT_TOKEN_HERE' in the script")
            print("="*60)
            return
        
        if API_ID == 123456 or API_HASH == "your_api_hash_here":
            print("\n" + "="*60)
            print("❌ ERROR: Please configure API credentials!")
            print("="*60)
            print("1. Go to https://my.telegram.org/apps")
            print("2. Login with your Telegram account")
            print("3. Create an application")
            print("4. Copy API ID and API Hash")
            print("5. Replace values in the script")
            print("="*60)
            return
        
        # Create application
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("grant", self.grant_command))
        self.application.add_handler(CommandHandler("revoke", self.revoke_command))
        self.application.add_handler(CallbackQueryHandler(self.callback_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
        
        # Start bot
        print("\n" + "="*60)
        print("🤖 TELEGRAM ULTIMATE REPORT BOT v5.0")
        print("="*60)
        print(f"✅ Bot Token: {BOT_TOKEN[:15]}...")
        print(f"👑 Owner ID: {OWNER_ID}")
        print(f"🔑 API ID: {API_ID}")
        print("="*60)
        print("🚀 Bot is running...")
        print("📡 Using REAL Telegram API calls")
        print("📈 Reports sent directly to Telegram moderation")
        print("="*60 + "\n")
        
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
        finally:
            await self.application.updater.stop()
            await self.application.stop()

# ============ MAIN ============
if __name__ == "__main__":
    # Create necessary directories and files
    os.makedirs("sessions", exist_ok=True)
    
    # Create empty files if not exist
    for file in [SESSIONS_FILE, STATS_FILE, USERS_FILE]:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump({}, f)
    
    # Run bot
    bot = ReportBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
