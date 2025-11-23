import { useState } from "react";

const LiveChatModal = ({closeModal}) => {
  const [messages, setMessages] = useState([{ text:'', isUser:{} }]);
    const sendMessage = () => {
    const messageInput = document.getElementById(
      "messageInput",
    );
    const message = messageInput.value.trim();
    if (message) {
      setMessages((prev) => [...prev, { text: message, isUser: true }]);
      messageInput.value = "";
      // Simulate agent response
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            text: "Thank you for your message. I'll help you with that right away.",
            isUser: false,
          },
        ]);
        const chatHistory = document.getElementById("chatHistory");
        if (chatHistory) {
          chatHistory.scrollTop = chatHistory.scrollHeight;
        }
      }, 1000);
    }
  };
    return ( 
         <div
        className="fixed bottom-4 right-4 w-80 bg-white rounded-xl shadow-2xl overflow-hidden z-50 animate-fade-in"
      >
        <div className="bg-indigo-600 p-4 flex items-center justify-between text-white">
          <div className="flex items-center">
            <div className="w-8 h-8 rounded-full overflow-hidden border-2 border-white">
              <img
                src="https://readdy.ai/api/search-image?query=professional%20customer%20service%20agent%20portrait%2C%20friendly%20smile%2C%20headset%2C%20office%20environment%2C%20high%20quality&width=100&height=100&seq=4&orientation=squarish"
                alt="Support Agent"
                className="w-full h-full object-cover"
              />
            </div>
            <div className="ml-3">
              <p className="font-medium text-sm">Sarah Johnson</p>
              <p className="text-xs text-indigo-200">Support Agent</p>
            </div>
          </div>
          <button
            id="closeChatButton"
            className="text-white hover:text-indigo-200 transition-colors"
            onClick={() =>
              closeModal(false)
            }
          >
            <i className="fas fa-times"></i>
          </button>
        </div>
        <div id="chatHistory" className="h-80 p-4 overflow-y-auto bg-gray-50">
          {messages.length === 0 ? (
            <div className="flex items-start mb-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full overflow-hidden mr-3">
                <img
                  src="https://readdy.ai/api/search-image?query=professional%20customer%20service%20agent%20portrait%2C%20friendly%20smile%2C%20headset%2C%20office%20environment%2C%20high%20quality&width=100&height=100&seq=4&orientation=squarish"
                  alt="Agent"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="bg-white p-3 rounded-lg shadow-sm max-w-[80%]">
                <p className="text-sm text-gray-700">
                  Hi there! 👋 How can I assist you today?
                </p>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex items-start mb-4 ${message.isUser ? "justify-end" : ""}`}
              >
                {!message.isUser && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full overflow-hidden mr-3">
                    <img
                      src="https://readdy.ai/api/search-image?query=professional%20customer%20service%20agent%20portrait%2C%20friendly%20smile%2C%20headset%2C%20office%20environment%2C%20high%20quality&width=100&height=100&seq=4&orientation=squarish"
                      alt="Agent"
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
                <div
                  className={`p-3 rounded-lg shadow-sm max-w-[80%] ${
                    message.isUser
                      ? "bg-indigo-600 text-white"
                      : "bg-white text-gray-700"
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                </div>
                {message.isUser && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full overflow-hidden ml-3">
                    <div className="w-full h-full bg-gray-300 flex items-center justify-center">
                      <i className="fas fa-user text-gray-600"></i>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
        <div className="p-4 border-t">
          <div className="flex items-center">
            <input
              type="text"
              id="messageInput"
              placeholder="Type your message..."
              className="flex-1 px-4 py-2 bg-gray-100 rounded-l-full focus:outline-none focus:ring-2 focus:ring-indigo-400 text-sm"
            />
            <button
              id="sendMessageButton"
              className="px-4 py-2 bg-indigo-600 text-white rounded-r-full hover:bg-indigo-700 transition-colors !rounded-button whitespace-nowrap"
            >
              <i className="fas fa-paper-plane"></i>
            </button>
          </div>
        </div>
      </div>
    );
}
 
export default LiveChatModal;