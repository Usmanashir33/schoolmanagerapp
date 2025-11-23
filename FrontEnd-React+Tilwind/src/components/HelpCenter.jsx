// The exported code uses Tailwind CSS. Install Tailwind CSS in your dev environment to ensure all styles work.
import { useState, useEffect, useRef } from "react";
import LiveChatModal from "./LiveChatModal";
import { Link } from "react-router";
const HelpCenterPage = () => {
    const [showContactModal,setShowContactModal] = useState(false);
    const [showLiveChatModal,setShowLiveChatModal] = useState(false);
  const [searchFocus, setSearchFocus] = useState(false);
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    issueType: "",
    description: "",
    file: null,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [typedText, setTypedText] = useState("");
  const fullGreeting = "How can we help you today?";
  const [copied, setCopied] = useState(null);
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
  useEffect(() => {
    const messageInput = document.getElementById("messageInput");
    const sendButton = document.getElementById("sendMessageButton");
    const handleKeyPress = (e) => {
      if (e.key === "Enter") {
        sendMessage();
      }
    };
    messageInput?.addEventListener("keypress", handleKeyPress);
    sendButton?.addEventListener("click", sendMessage);
    return () => {
      messageInput?.removeEventListener("keypress", handleKeyPress);
      sendButton?.removeEventListener("click", sendMessage);
    };
  }, []);
  // Typing animation effect
  useEffect(() => {
    if (typedText.length < fullGreeting.length) {
      const timeout = setTimeout(() => {
        setTypedText(fullGreeting.slice(0, typedText.length + 1));
      }, 100);
      return () => clearTimeout(timeout);
    }
  }, [typedText]);
  useEffect(() => {
    setTypedText("H");
  }, []);
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFormData((prev) => ({ ...prev, file: e.target.files?.[0] || null }));
    }
  };
  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
      setIsSubmitted(true);
      // Reset form after showing success message
      setTimeout(() => {
        setFormData({
          fullName: "",
          email: "",
          issueType: "",
          description: "",
          file: null,
        });
        setIsSubmitted(false);
      }, 3000);
    }, 1500);
  };
  const copyToClipboard = (text, type) => {
    navigator.clipboard.writeText(text);
    setCopied(type);
    setTimeout(() => setCopied(null), 2000);
  };
  return (
    <div className=" bg-gray-50 font-sans">
      <div className=" mx-auto bg-white shadow-lg rounded-xl overflow-hidden">
        {/* Header Section with Animation */}
        <div className="bg-indigo-600 p-6 text-white relative overflow-hidden">
          <div className="flex items-center mb-4">
            <div className="relative">
              <div className="w-12 h-12 rounded-full overflow-hidden border-2 border-white shadow-md animate-pulse">
                <img
                  src="https://readdy.ai/api/search-image?query=professional%20support%20agent%20with%20headset%2C%20smiling%2C%20friendly%20face%2C%20high%20quality%20portrait%2C%20soft%20lighting%2C%20blue%20background%2C%20professional%20appearance&width=200&height=200&seq=1&orientation=squarish"
                  alt="Support Agent"
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-400 rounded-full border border-white"></div>
            </div>
            <div className="ml-4">
              <h1 className="text-xl font-bold">{typedText}</h1>
              <p className="text-sm text-indigo-100 opacity-90">
                We're here to assist you
              </p>
            </div>
          </div>
          <div className="relative mt-4 transition-all duration-300">
            <div
              className={`absolute inset-y-0 left-3 flex items-center pointer-events-none transition-all duration-300 ${searchFocus ? "text-indigo-800" : "text-gray-400"}`}
            >
              <i className="fas fa-search"></i>
            </div>
            <input
              type="text"
              placeholder="Search for help topics..."
              className="w-full py-3 pl-10 pr-4 text-gray-700 bg-white rounded-lg border-none focus:ring-2 focus:ring-indigo-400 transition-all duration-300"
              onFocus={() => setSearchFocus(true)}
              onBlur={() => setSearchFocus(false)}
            />
          </div>
        </div>

        {/* Quick Access Grid with Animations */}
        <div className="grid grid-cols-2 gap-2 p-4">
          <div className="bg-indigo-50 p-4 rounded-lg text-center cursor-pointer hover:bg-indigo-100 transition-all duration-300 transform hover:-translate-y-1">
            <div className="text-indigo-600 text-2xl mb-2">
              <i className="fas fa-question-circle"></i>
            </div>
            <h3 className="font-medium text-indigo-800">FAQs</h3>
            <p className="text-xs text-gray-500">Quick answers</p>
          </div>
          <Link
          to={`/site-guides`}
            data-readdy="true"
            className="block bg-blue-50 p-4 rounded-lg text-center cursor-pointer hover:bg-blue-100 transition-all duration-300 transform hover:-translate-y-1"
          >
            <div className="text-blue-600 text-2xl mb-2">
              <i className="fas fa-book"></i>
            </div>
            <h3 className="font-medium text-blue-800">Guides</h3>
            <p className="text-xs text-gray-500">Detailed instructions</p>
          </Link>
          <div
            id="contactButton"
            className="bg-purple-50 p-4 rounded-lg text-center cursor-pointer hover:bg-purple-100 transition-all duration-300 transform hover:-translate-y-1"
            onClick={() => {setShowContactModal(true)}}
          >
            <div className="text-purple-600 text-2xl mb-2">
              <i className="fas fa-phone-alt"></i>
            </div>
            <h3 className="font-medium text-purple-800">Contact</h3>
            <p className="text-xs text-gray-500">Talk to us</p>
          </div>
          <div
            id="liveChatButton"
            className="bg-green-50 p-4 rounded-lg text-center cursor-pointer hover:bg-green-100 transition-all duration-300 transform hover:-translate-y-1"
            onClick={() =>
              setShowLiveChatModal(true)
            }
          >
            <div className="text-green-600 text-2xl mb-2">
              <i className="fas fa-comment-dots"></i>
            </div>
            <h3 className="font-medium text-green-800">Live Chat</h3>
            <p className="text-xs text-gray-500">Immediate support</p>
          </div>
        </div>

        {/* Support Team Status with Animation */}
        <div className="px-6 py-3 border-t border-b border-gray-100">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse mr-2"></div>
            <span className="text-sm font-medium text-gray-700">
              Support Team Available
            </span>
            <div className="ml-auto text-xs text-gray-500">
              <i className="far fa-clock mr-1"></i>
              <span>Available until 8PM EST</span>
            </div>
          </div>
        </div>

        {/* Contact Information Block with Animations */}
        <div className="p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            Contact Information
          </h2>
          <div className="space-y-3">
            <div
              className="flex items-center cursor-pointer group"
              onClick={() => copyToClipboard("support@company.com", "email")}
            >
              <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 mr-3 group-hover:bg-indigo-200 transition-colors duration-300">
                <i className="fas fa-envelope"></i>
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-600">support@company.com</p>
                <div className="h-0.5 w-0 group-hover:w-full bg-indigo-400 transition-all duration-300"></div>
              </div>
              {copied === "email" && (
                <span className="text-xs text-green-600 ml-2 animate-fade-in">
                  Copied!
                </span>
              )}
            </div>
            <div
              className="flex items-center cursor-pointer group"
              onClick={() => copyToClipboard("(800) 123-4567", "phone")}
            >
              <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 mr-3 group-hover:bg-indigo-200 transition-colors duration-300">
                <i className="fas fa-phone-alt"></i>
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-600">(800) 123-4567</p>
                <div className="h-0.5 w-0 group-hover:w-full bg-indigo-400 transition-all duration-300"></div>
              </div>
              {copied === "phone" && (
                <span className="text-xs text-green-600 ml-2 animate-fade-in">
                  Copied!
                </span>
              )}
            </div>
            <div
              className="flex items-center cursor-pointer group"
              onClick={() => copyToClipboard("+1 (555) 987-6543", "whatsapp")}
            >
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center text-green-600 mr-3 group-hover:bg-green-200 transition-colors duration-300">
                <i className="fab fa-whatsapp"></i>
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-600">
                  WhatsApp: +1 (555) 987-6543
                </p>
                <div className="h-0.5 w-0 group-hover:w-full bg-green-400 transition-all duration-300"></div>
              </div>
              {copied === "whatsapp" && (
                <span className="text-xs text-green-600 ml-2 animate-fade-in">
                  Copied!
                </span>
              )}
            </div>
            <div
              className="flex items-center cursor-pointer group"
              onClick={() => copyToClipboard("@companysupport", "telegram")}
            >
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 mr-3 group-hover:bg-blue-200 transition-colors duration-300">
                <i className="fab fa-telegram"></i>
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-600">
                  Telegram: @companysupport
                </p>
                <div className="h-0.5 w-0 group-hover:w-full bg-blue-400 transition-all duration-300"></div>
              </div>
              {copied === "telegram" && (
                <span className="text-xs text-green-600 ml-2 animate-fade-in">
                  Copied!
                </span>
              )}
            </div>
            <div
              className="flex items-center cursor-pointer group"
              onClick={() => copyToClipboard("@company_support", "twitter")}
            >
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 mr-3 group-hover:bg-blue-200 transition-colors duration-300">
                <i className="fab fa-twitter"></i>
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-600">
                  Twitter: @company_support
                </p>
                <div className="h-0.5 w-0 group-hover:w-full bg-blue-400 transition-all duration-300"></div>
              </div>
              {copied === "twitter" && (
                <span className="text-xs text-green-600 ml-2 animate-fade-in">
                  Copied!
                </span>
              )}
            </div>
            <div className="flex items-center">
              <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 mr-3">
                <i className="fas fa-clock"></i>
              </div>
              <p className="text-sm text-gray-600">Mon-Fri: 9AM-6PM EST</p>
            </div>
          </div>
        </div>

        {/* Support Ticket Form with Animations */}
        <form onSubmit={handleSubmit} className="p-6 border-t border-gray-100">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            Submit a Ticket
          </h2>
          <div className="space-y-4">
            <div className="relative">
              <input
                type="text"
                id="fullName"
                name="fullName"
                value={formData.fullName}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400 focus:border-transparent transition-all duration-300 peer"
                placeholder=" "
                required
              />
              <label
                htmlFor="fullName"
                className="absolute text-sm text-gray-500 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white px-2 peer-focus:px-2 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:-translate-y-4 peer-focus:scale-75 peer-focus:text-indigo-600 left-1"
              >
                Full Name
              </label>
            </div>
            <div className="relative">
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400 focus:border-transparent transition-all duration-300 peer"
                placeholder=" "
                required
              />
              <label
                htmlFor="email"
                className="absolute text-sm text-gray-500 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white px-2 peer-focus:px-2 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:-translate-y-4 peer-focus:scale-75 peer-focus:text-indigo-600 left-1"
              >
                Email Address
              </label>
            </div>
            <div className="relative">
              <select
                id="issueType"
                name="issueType"
                value={formData.issueType}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400 focus:border-transparent transition-all duration-300 appearance-none cursor-pointer"
                required
              >
                <option value="" disabled>
                  Select Issue Type
                </option>
                <option value="technical">Technical Support</option>
                <option value="billing">Billing Question</option>
                <option value="feature">Feature Request</option>
                <option value="other">Other</option>
              </select>
              <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none text-gray-500">
                <i className="fas fa-chevron-down"></i>
              </div>
            </div>
            <div className="relative">
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-400 focus:border-transparent transition-all duration-300 peer"
                placeholder=" "
                required
              ></textarea>
              <label
                htmlFor="description"
                className="absolute text-sm text-gray-500 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white px-2 peer-focus:px-2 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-[5.5rem] peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:-translate-y-4 peer-focus:scale-75 peer-focus:text-indigo-600 left-1"
              >
                Describe your issue...
              </label>
              <div className="text-xs text-right text-gray-500 mt-1">
                {formData.description.length}/500 characters
              </div>
            </div>
            <div className="relative">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center cursor-pointer hover:border-indigo-400 transition-colors duration-300">
                <input
                  type="file"
                  id="file"
                  name="file"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <label htmlFor="file" className="cursor-pointer">
                  <i className="fas fa-paperclip text-gray-400 mr-2"></i>
                  <span className="text-sm text-gray-600">
                    {formData.file
                      ? formData.file.name
                      : "Attach Files (optional)"}
                  </span>
                </label>
              </div>
            </div>
          </div>
          <button
            type="submit"
            disabled={isLoading || isSubmitted}
            className={`mt-6 w-full py-3 px-4 bg-indigo-600 text-white rounded-lg !rounded-button whitespace-nowrap cursor-pointer transition-all duration-300 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ${isLoading ? "opacity-70" : ""}`}
          >
            {isLoading ? (
              <span className="flex items-center justify-center">
                <i className="fas fa-circle-notch fa-spin mr-2"></i>
                Processing...
              </span>
            ) : isSubmitted ? (
              <span className="flex items-center justify-center">
                <i className="fas fa-check-circle mr-2"></i>
                Ticket Submitted!
              </span>
            ) : (
              "Submit Ticket"
            )}
          </button>
        </form>

        {/* Recent Articles Section with Animations */}
        <div className="p-6 border-t border-gray-100">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">
            Recent Articles
          </h2>
          <div className="space-y-4">
            <div className="flex border border-gray-200 rounded-lg overflow-hidden cursor-pointer hover:shadow-md transition-all duration-300 transform hover:-translate-y-1">
              <div className="w-1/3 h-24 overflow-hidden">
                <img
                  src="https://readdy.ai/api/search-image?query=person%20getting%20started%20with%20software%2C%20tutorial%20concept%2C%20digital%20learning%2C%20computer%20screen%20showing%20tutorial%2C%20modern%20office%20setting%2C%20professional%20environment%2C%20high%20quality&width=300&height=200&seq=2&orientation=landscape"
                  alt="Getting Started Guide"
                  className="w-full h-full object-cover object-top transition-transform duration-300 hover:scale-110"
                />
              </div>
              <div className="w-2/3 p-3">
                <h3 className="font-medium text-gray-800 text-sm">
                  Getting Started Guide
                </h3>
                <p className="text-xs text-gray-500 mt-1">
                  Learn the basics of our platform
                </p>
                <div className="flex items-center mt-2">
                  <span className="text-xs text-indigo-600">
                    <i className="far fa-clock mr-1"></i>5 min read
                  </span>
                </div>
              </div>
            </div>
            <div className="flex border border-gray-200 rounded-lg overflow-hidden cursor-pointer hover:shadow-md transition-all duration-300 transform hover:-translate-y-1">
              <div className="w-1/3 h-24 overflow-hidden">
                <img
                  src="https://readdy.ai/api/search-image?query=security%20concept%2C%20digital%20protection%2C%20cybersecurity%2C%20shield%20icon%2C%20secure%20data%2C%20professional%20environment%2C%20modern%20office%20setting%2C%20high%20quality&width=300&height=200&seq=3&orientation=landscape"
                  alt="Security Best Practices"
                  className="w-full h-full object-cover object-top transition-transform duration-300 hover:scale-110"
                />
              </div>
              <div className="w-2/3 p-3">
                <h3 className="font-medium text-gray-800 text-sm">
                  Security Best Practices
                </h3>
                <p className="text-xs text-gray-500 mt-1">
                  Protect your account
                </p>
                <div className="flex items-center mt-2">
                  <span className="text-xs text-indigo-600">
                    <i className="far fa-clock mr-1"></i>8 min read
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
      {/* Custom CSS for animations */}
      {showLiveChatModal &&
        <LiveChatModal closeModal={setShowLiveChatModal}/>
      }

      {/* Contact Modal */}
      { showContactModal && <div
        id="contactModal"
        className="hidden h-full  fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fade-in"
      >
        <div className="bg-white  h-5/6 overflow-y-auto  rounded-xl w-full max-w-md mx-4 overflow-hidden shadow-2xl">
          <div className="bg-purple-600 p-4 text-white flex justify-between items-center">
            <h3 className="text-lg font-semibold">Contact Us</h3>
            <button
              onClick={() =>
                setShowContactModal(false)
              }
              className="text-white hover:text-purple-200 transition-colors"
            >
              <i className="fas fa-times"></i>
            </button>
          </div>
          <div className="p-6">
            <div className="mb-6">
              <p className="text-sm text-gray-600 mb-2">Support Hours:</p>
              <p className="text-sm font-medium text-gray-800">
                <i className="far fa-clock mr-2"></i>
                Monday - Friday: 9AM-6PM EST
              </p>
            </div>
            <div className="space-y-4">
              <a
                href="tel:8001234567"
                className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 mr-3">
                  <i className="fas fa-phone-alt"></i>
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-800">Call Us</p>
                  <p className="text-sm text-gray-600">(800) 123-4567</p>
                </div>
                <i className="fas fa-chevron-right text-gray-400"></i>
              </a>

              <a
                href="mailto:support@company.com"
                className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center text-red-600 mr-3">
                  <i className="fas fa-envelope"></i>
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-800">Email Us</p>
                  <p className="text-sm text-gray-600">support@company.com</p>
                </div>
                <i className="fas fa-chevron-right text-gray-400"></i>
              </a>

              <a
                href="https://wa.me/15559876543"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center text-green-600 mr-3">
                  <i className="fab fa-whatsapp"></i>
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-800">WhatsApp</p>
                  <p className="text-sm text-gray-600">+1 (555) 987-6543</p>
                </div>
                <i className="fas fa-chevron-right text-gray-400"></i>
              </a>

              <a
                href="https://t.me/companysupport"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 mr-3">
                  <i className="fab fa-telegram"></i>
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-800">Telegram</p>
                  <p className="text-sm text-gray-600">@companysupport</p>
                </div>
                <i className="fas fa-chevron-right text-gray-400"></i>
              </a>

              <a
                href="https://twitter.com/company_support"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 mr-3">
                  <i className="fab fa-twitter"></i>
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-800">Twitter</p>
                  <p className="text-sm text-gray-600">@company_support</p>
                </div>
                <i className="fas fa-chevron-right text-gray-400"></i>
              </a>
            </div>
          </div>
        </div>
      </div>}

      <style jsx>{`
@keyframes fade-in {
0% { opacity: 0; }
100% { opacity: 1; }
}
.animate-fade-in {
animation: fade-in 0.3s ease-in-out;
}
`}</style>
    </div>
  );
};
export default HelpCenterPage;
