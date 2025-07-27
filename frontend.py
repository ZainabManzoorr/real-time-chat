import streamlit as st
import requests
import json
import websocket
import threading
import time
import queue
from datetime import datetime
import uuid

# Global message queue for WebSocket communication
message_queue = queue.Queue()

# Backend URL
BACKEND_URL = "http://localhost:8000"

def main():
    st.set_page_config(page_title="Real-time Chat Tester", layout="wide")
    
    # Add custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    .error-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 0.5rem 0;
    }
    .message-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header"><h1>🚀 Real-time Chat Application</h1><p>Complete Workflow Tester</p></div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'user1_data' not in st.session_state:
        st.session_state.user1_data = None
    if 'user2_data' not in st.session_state:
        st.session_state.user2_data = None
    if 'current_room' not in st.session_state:
        st.session_state.current_room = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'ws_connections' not in st.session_state:
        st.session_state.ws_connections = {}
    
    # Sidebar for workflow control
    with st.sidebar:
        st.header("🔄 Workflow Control")
        
        if st.button("🔄 Reset All Data"):
            st.session_state.user1_data = None
            st.session_state.user2_data = None
            st.session_state.current_room = None
            st.session_state.messages = []
            st.session_state.ws_connections = {}
            # Clear the global message queue
            global message_queue
            while not message_queue.empty():
                message_queue.get()
            st.rerun()
        
        st.markdown("---")
        st.header("📋 Current Status")
        
        if st.session_state.user1_data:
            st.success("✅ User 1: Authenticated")
        else:
            st.error("❌ User 1: Not authenticated")
            
        if st.session_state.user2_data:
            st.success("✅ User 2: Authenticated")
        else:
            st.error("❌ User 2: Not authenticated")
            
        if st.session_state.current_room:
            st.success(f"✅ Room: {st.session_state.current_room}")
        else:
            st.error("❌ Room: Not created")
    
    # Main content area
    col1, col2 = st.columns(2)
    
    # User 1 Panel
    with col1:
        st.header("👤 User 1 Panel")
        
        if st.session_state.user1_data is None:
            # User 1 Authentication
            with st.expander("🔐 User 1 Authentication", expanded=True):
                tab1, tab2 = st.tabs(["Signup", "Login"])
                
                with tab1:
                    st.subheader("Signup User 1")
                    user1_email = st.text_input("Email", value="atif@test.com", key="user1_signup_email")
                    user1_password = st.text_input("Password", value="password123", type="password", key="user1_signup_password")
                    
                    if st.button("Signup User 1"):
                        if user1_email and user1_password:
                            try:
                                response = requests.post(
                                    f"{BACKEND_URL}/auth/signup",
                                    json={"email": user1_email, "password": user1_password}
                                )
                                if response.status_code == 200:
                                    st.success("✅ User 1 signup successful!")
                                else:
                                    st.error(f"❌ Signup failed: {response.text}")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                        else:
                            st.error("❌ Please enter email and password")
                
                with tab2:
                    st.subheader("Login User 1")
                    user1_login_email = st.text_input("Email", value="atif@test.com", key="user1_login_email")
                    user1_login_password = st.text_input("Password", value="password123", type="password", key="user1_login_password")
                    
                    if st.button("Login User 1"):
                        if user1_login_email and user1_login_password:
                            try:
                                response = requests.post(
                                    f"{BACKEND_URL}/auth/login",
                                    json={"email": user1_login_email, "password": user1_login_password}
                                )
                                if response.status_code == 200:
                                    # Extract token from cookies
                                    cookies = response.cookies
                                    access_token = cookies.get("access_token")
                                    if access_token:
                                        response_data = response.json()
                                        st.session_state.user1_data = {
                                            "email": user1_login_email,
                                            "user_id": response_data.get("user_id"),
                                            "access_token": access_token
                                        }
                                        st.success("✅ User 1 login successful!")
                                        st.rerun()
                                    else:
                                        st.error("❌ No access token received")
                                else:
                                    st.error(f"❌ Login failed: {response.text}")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                        else:
                            st.error("❌ Please enter email and password")
        else:
            # User 1 is authenticated
            st.success(f"✅ Authenticated as: {st.session_state.user1_data['email']}")
            st.info(f"User ID: `{st.session_state.user1_data['user_id']}`")
            
            with st.expander("🔑 User 1 Token"):
                st.code(st.session_state.user1_data['access_token'], language="text")
    
    # User 2 Panel
    with col2:
        st.header("👤 User 2 Panel")
        
        if st.session_state.user2_data is None:
            # User 2 Authentication
            with st.expander("🔐 User 2 Authentication", expanded=True):
                tab1, tab2 = st.tabs(["Signup", "Login"])
                
                with tab1:
                    st.subheader("Signup User 2")
                    user2_email = st.text_input("Email", value="duda@test.com", key="user2_signup_email")
                    user2_password = st.text_input("Password", value="password123", type="password", key="user2_signup_password")
                    
                    if st.button("Signup User 2"):
                        if user2_email and user2_password:
                            try:
                                response = requests.post(
                                    f"{BACKEND_URL}/auth/signup",
                                    json={"email": user2_email, "password": user2_password}
                                )
                                if response.status_code == 200:
                                    st.success("✅ User 2 signup successful!")
                                else:
                                    st.error(f"❌ Signup failed: {response.text}")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                        else:
                            st.error("❌ Please enter email and password")
                
                with tab2:
                    st.subheader("Login User 2")
                    user2_login_email = st.text_input("Email", value="duda@test.com", key="user2_login_email")
                    user2_login_password = st.text_input("Password", value="password123", type="password", key="user2_login_password")
                    
                    if st.button("Login User 2"):
                        if user2_login_email and user2_login_password:
                            try:
                                response = requests.post(
                                    f"{BACKEND_URL}/auth/login",
                                    json={"email": user2_login_email, "password": user2_login_password}
                                )
                                if response.status_code == 200:
                                    # Extract token from cookies
                                    cookies = response.cookies
                                    access_token = cookies.get("access_token")
                                    if access_token:
                                        response_data = response.json()
                                        st.session_state.user2_data = {
                                            "email": user2_login_email,
                                            "user_id": response_data.get("user_id"),
                                            "access_token": access_token
                                        }
                                        st.success("✅ User 2 login successful!")
                                        st.rerun()
                                    else:
                                        st.error("❌ No access token received")
                                else:
                                    st.error(f"❌ Login failed: {response.text}")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                        else:
                            st.error("❌ Please enter email and password")
        else:
            # User 2 is authenticated
            st.success(f"✅ Authenticated as: {st.session_state.user2_data['email']}")
            st.info(f"User ID: `{st.session_state.user2_data['user_id']}`")
            
            with st.expander("🔑 User 2 Token"):
                st.code(st.session_state.user2_data['access_token'], language="text")
    
    # Room Creation Section
    st.markdown("---")
    st.header("🏠 Chat Room Management")
    
    if st.session_state.user1_data and st.session_state.user2_data:
        if st.session_state.current_room is None:
            if st.button("🏠 Create Chat Room"):
                try:
                    headers = {
                        "Authorization": f"Bearer {st.session_state.user1_data['access_token']}",
                        "Content-Type": "application/json"
                    }
                    response = requests.post(
                        f"{BACKEND_URL}/room/get_or_create",
                        json={"other_user_id": st.session_state.user2_data['user_id']},
                        headers=headers
                    )
                    if response.status_code == 200:
                        room_data = response.json()
                        st.session_state.current_room = room_data.get("room_id")
                        st.success(f"✅ Room created: `{st.session_state.current_room}`")
                        st.rerun()
                    else:
                        st.error(f"❌ Room creation failed: {response.text}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.success(f"✅ Room ID: `{st.session_state.current_room}`")
            
            # WebSocket Connection Section
            st.markdown("---")
            st.header("💬 Real-time Chat")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔌 WebSocket Connections")
                
                if st.button("🔌 Connect Both Users"):
                    # Check if already connected
                    if "user1" in st.session_state.ws_connections and "user2" in st.session_state.ws_connections:
                        st.warning("⚠️ Both users are already connected!")
                    else:
                        # Connect User 1 if not already connected
                        if "user1" not in st.session_state.ws_connections:
                            connect_user_to_websocket("user1", st.session_state.user1_data, st.session_state.current_room)
                        # Connect User 2 if not already connected
                        if "user2" not in st.session_state.ws_connections:
                            connect_user_to_websocket("user2", st.session_state.user2_data, st.session_state.current_room)
                        st.success("✅ Both users connected to WebSocket!")
                
                if st.button("🔌 Connect User 1 Only"):
                    if "user1" in st.session_state.ws_connections:
                        st.warning("⚠️ User 1 is already connected!")
                    else:
                        connect_user_to_websocket("user1", st.session_state.user1_data, st.session_state.current_room)
                        st.success("✅ User 1 connected to WebSocket!")
                
                if st.button("🔌 Connect User 2 Only"):
                    if "user2" in st.session_state.ws_connections:
                        st.warning("⚠️ User 2 is already connected!")
                    else:
                        connect_user_to_websocket("user2", st.session_state.user2_data, st.session_state.current_room)
                        st.success("✅ User 2 connected to WebSocket!")
                
                # Disconnect buttons
                st.markdown("---")
                st.subheader("🔌 Disconnect")
                
                if st.button("🔌 Disconnect Both Users"):
                    if "user1" in st.session_state.ws_connections:
                        try:
                            st.session_state.ws_connections["user1"]["ws"].close()
                        except:
                            pass
                        del st.session_state.ws_connections["user1"]
                    if "user2" in st.session_state.ws_connections:
                        try:
                            st.session_state.ws_connections["user2"]["ws"].close()
                        except:
                            pass
                        del st.session_state.ws_connections["user2"]
                    st.success("✅ Both users disconnected!")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔌 Disconnect User 1"):
                        if "user1" in st.session_state.ws_connections:
                            try:
                                st.session_state.ws_connections["user1"]["ws"].close()
                            except:
                                pass
                            del st.session_state.ws_connections["user1"]
                            st.success("✅ User 1 disconnected!")
                        else:
                            st.warning("⚠️ User 1 is not connected!")
                
                with col2:
                    if st.button("🔌 Disconnect User 2"):
                        if "user2" in st.session_state.ws_connections:
                            try:
                                st.session_state.ws_connections["user2"]["ws"].close()
                            except:
                                pass
                            del st.session_state.ws_connections["user2"]
                            st.success("✅ User 2 disconnected!")
                        else:
                            st.warning("⚠️ User 2 is not connected!")
            
            with col2:
                st.subheader("📤 Send Messages")
                
                # User 1 Message Section
                st.markdown("**👤 User 1 Message**")
                user1_message = st.text_area(
                    "Type your message here...",
                    key="user1_message",
                    height=80,
                    placeholder="Enter your message..."
                )
                
                # User 1 Send Button and Status
                if st.button("📤 Send as User 1", key="send_user1", use_container_width=True):
                    if user1_message and "user1" in st.session_state.ws_connections:
                        send_message("user1", user1_message)
                        st.success("✅ Sent!")
                        st.rerun()
                    else:
                        st.error("❌ Not connected or no message")
                
                # User 1 Connection Status
                if "user1" in st.session_state.ws_connections:
                    st.success("🟢 User 1 Connected")
                else:
                    st.error("🔴 User 1 Disconnected")
                
                st.markdown("---")
                
                # User 2 Message Section
                st.markdown("**👤 User 2 Message**")
                user2_message = st.text_area(
                    "Type your message here...",
                    key="user2_message",
                    height=80,
                    placeholder="Enter your message..."
                )
                
                # User 2 Send Button and Status
                if st.button("📤 Send as User 2", key="send_user2", use_container_width=True):
                    if user2_message and "user2" in st.session_state.ws_connections:
                        send_message("user2", user2_message)
                        st.success("✅ Sent!")
                        st.rerun()
                    else:
                        st.error("❌ Not connected or no message")
                
                # User 2 Connection Status
                if "user2" in st.session_state.ws_connections:
                    st.success("🟢 User 2 Connected")
                else:
                    st.error("🔴 User 2 Disconnected")
            
            # Display Messages
            st.markdown("---")
            st.subheader("💬 Chat Messages")
            
            # Add a container for messages with better styling
            with st.container():
                if st.session_state.messages:
                    # Create a scrollable area for messages
                    message_container = st.container()
                    
                    with message_container:
                        for i, msg in enumerate(st.session_state.messages):
                            timestamp = msg.get('timestamp', '')
                            sender = msg.get('sender', '')
                            content = msg.get('content', '')
                            
                            # Create different styling for different message types
                            if sender == "user1":
                                with st.chat_message("user", avatar="👤"):
                                    st.write(f"**{content}**")
                                    st.caption(f"User 1 • {timestamp}")
                            elif sender == "user2":
                                with st.chat_message("user", avatar="👤"):
                                    st.write(f"**{content}**")
                                    st.caption(f"User 2 • {timestamp}")
                            else:
                                with st.chat_message("assistant", avatar="🤖"):
                                    st.write(f"*{content}*")
                                    st.caption(f"System • {timestamp}")
                else:
                    st.info("💬 No messages yet. Connect users and start chatting!")
                    
                # Add a clear messages button
                if st.session_state.messages:
                    if st.button("🗑️ Clear All Messages", key="clear_messages"):
                        st.session_state.messages = []
                        st.rerun()
            
            # Connection Status
            st.markdown("---")
            st.subheader("🔌 Connection Status")
            
            # Create a more visual connection status
            col1_status, col2_status = st.columns(2)
            
            with col1_status:
                if "user1" in st.session_state.ws_connections:
                    st.success("🟢 **User 1 Connected**")
                    st.caption("WebSocket: Active")
                else:
                    st.error("🔴 **User 1 Disconnected**")
                    st.caption("WebSocket: Inactive")
                
            with col2_status:
                if "user2" in st.session_state.ws_connections:
                    st.success("🟢 **User 2 Connected**")
                    st.caption("WebSocket: Active")
                else:
                    st.error("🔴 **User 2 Disconnected**")
                    st.caption("WebSocket: Inactive")
    
    else:
        st.warning("⚠️ Please authenticate both users first to create a room and start chatting.")
    
    # Process message queue from WebSocket threads
    process_message_queue()
    
    # Debug Information
    with st.expander("🔍 Debug Information"):
        st.json({
            "user1_data": st.session_state.user1_data,
            "user2_data": st.session_state.user2_data,
            "current_room": st.session_state.current_room,
            "ws_connections": list(st.session_state.ws_connections.keys()),
            "message_count": len(st.session_state.messages)
        })

def connect_user_to_websocket(user_key, user_data, room_id):
    """Connect a user to WebSocket"""
    ws_url = f"ws://localhost:8000/chat/ws/chat/{room_id}?token={user_data['access_token']}"
    
    def on_message(ws, message):
        # Use global queue to safely communicate with main thread
        try:
            msg_data = json.loads(message)
            message_queue.put({
                'type': 'message',
                'sender': 'system',
                'content': f"Received: {msg_data.get('content', message)}",
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
        except:
            message_queue.put({
                'type': 'message',
                'sender': 'system',
                'content': f"Received: {message}",
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
    
    def on_error(ws, error):
        message_queue.put({
            'type': 'message',
            'sender': 'system',
            'content': f"WebSocket error: {error}",
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
    
    def on_close(ws, close_status_code, close_msg):
        message_queue.put({
            'type': 'message',
            'sender': 'system',
            'content': f"WebSocket connection closed (code: {close_status_code}, msg: {close_msg})",
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        # Mark connection as closed
        message_queue.put({
            'type': 'close_connection',
            'user_key': user_key
        })
    
    def on_open(ws):
        message_queue.put({
            'type': 'message',
            'sender': 'system',
            'content': f"{user_key.title()} connected to WebSocket successfully!",
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        # Send a ping message to keep connection alive
        try:
            ws.send("ping")
        except:
            pass
    
    # Create WebSocket connection
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # Start WebSocket in a separate thread with keep-alive
    def run_websocket():
        try:
            # Use a more robust connection method
            ws.run_forever(
                ping_interval=30, 
                ping_timeout=10,
                skip_utf8_validation=True
            )
        except Exception as e:
            message_queue.put({
                'type': 'message',
                'sender': 'system',
                'content': f"WebSocket thread error: {str(e)}",
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
    
    wst = threading.Thread(target=run_websocket, name=f"WebSocket-{user_key}")
    wst.daemon = False  # Make it non-daemon so it doesn't get killed
    wst.start()
    
    # Store both WebSocket and thread
    st.session_state.ws_connections[user_key] = {
        'ws': ws,
        'thread': wst
    }

def process_message_queue():
    """Process messages from WebSocket threads safely in main thread"""
    global message_queue
    try:
        while not message_queue.empty():
            msg = message_queue.get_nowait()
            
            if msg['type'] == 'message':
                st.session_state.messages.append({
                    'sender': msg['sender'],
                    'content': msg['content'],
                    'timestamp': msg['timestamp']
                })
            elif msg['type'] == 'close_connection':
                user_key = msg['user_key']
                if user_key in st.session_state.ws_connections:
                    del st.session_state.ws_connections[user_key]
    except Exception as e:
        # Silently handle any queue errors
        pass

def send_message(user_key, message):
    """Send message through WebSocket"""
    if user_key in st.session_state.ws_connections:
        try:
            st.session_state.ws_connections[user_key]['ws'].send(message)
            # Add message to local state
            st.session_state.messages.append({
                'sender': user_key,
                'content': message,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })
        except Exception as e:
            st.session_state.messages.append({
                'sender': 'system',
                'content': f"Failed to send message: {str(e)}",
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })

if __name__ == "__main__":
    main()
