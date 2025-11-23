// The exported code uses Tailwind CSS. Install Tailwind CSS in your dev environment to ensure all styles work.
import { useState, useEffect, useRef, useContext } from "react";
import { Link, useNavigate } from "react-router";
import PinPasswordManger from "./PinPasswordManger";
import { authContext } from "../customContexts/AuthContext";
import config from "../customHooks/ConfigDetails";
import { ArrowBigRightDash, File } from "lucide-react";
import useRequest from "../customHooks/RequestHook";
import { uiContext } from "../customContexts/UiContext";
import def1 from '../assets/images/default1.jpg';
import def2 from '../assets/images/default2.png';
import def3 from '../assets/images/default3.png';
    


const Settings = () => {
  const navigate = useNavigate();
  const defaultImages = [def1,def2,def3];
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const {currentUser,setCurrentUser,logout} = useContext(authContext);
  const {setSuccess} = useContext(uiContext);
  const {sendArbitRequest} = useRequest();
  const [passMode,setPassmode] = useState('')
  const [showPassModal,setShowPassModal] = useState(false);;
  const [showFormModal,setShowFormModal] = useState(false);
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(true);
  const [biometricEnabled, setBiometricEnabled] = useState(true);
  const [pushNotificationsEnabled, setPushNotificationsEnabled] =useState(true);
  const [emailAlertsEnabled, setEmailAlertsEnabled] = useState(true);
  const [selectedLanguage, setSelectedLanguage] = useState("English");
  const [isLanguageDropdownOpen, setIsLanguageDropdownOpen] = useState(false);
  const languageDropdownRef = useRef(null);
  const languages = [
    "English",
    "Spanish",
    "French",
    "German",
    "Chinese",
    "Japanese",
    "Korean",
  ];
  const handleImageChange = (e) => {
    const file = e.target.files[0];
    setImage(file);
    if (file) {
        let file_link = URL.createObjectURL(file)
      setPreview(file_link);
    }
  };
  const grabDefaultImage = async  (image) => {
  const response = await  fetch(image);        // fetch the image URL
  const blob = await  response.blob();           // convert it to a Blob
  setImage(blob);
  setPreview(image)  
}
  const handleSaveProfileResp = (data) => {
    setShowFormModal(false);
    setSuccess(data.success);
    setPreview(setImage(null));
    setCurrentUser(data.user);
  }
  const handleSaveProfile = () => {
    if (!image) {return};
    let data = new FormData()
    data.append('file',image);
    let url = `/authuser/update-profile/`
    sendArbitRequest(url,"PUT",data,handleSaveProfileResp,true,true)
  };
  const UpdateImageForm= () => {
    return (
          <div className="fixed  inset-0 bg-black bg-opacity-50 flex items-center justify-center z-20">
        
                <div className="bg-white rounded-xl p-4 w-full max-w-sm mx-4 transform transition-all  overflow-y-auto">
                  <div className=" flex justify-between items-center mb-4">
                    <h3 className="text-md font-semibold text-gray-800">
                     Update profile Picture
                    </h3>
                    <button
                      onClick={() => {
                        setShowFormModal(false);
                      }}
                      className="text-gray-400 hover:text-gray-600 cursor-pointer"
                    >
                      <i className="fas fa-times"></i>
                    </button>
                  </div>
                  {/* images  */}
                  <div className="flex justify-between items-center border  p-2 rounded-lg">
                    <div className="flex flex-col gap-1">
                      <img className="w-20 h-20 object-cover rounded-full"
                      src={`${config.BASE_URL}${currentUser?.picture}`} alt="current" />
                      <div className="p-1 border rounded-md bg-indigo-600  text-center text-xs text-white">
                        Current Picture
                      </div>
                    </div>
                    <ArrowBigRightDash className="text-indigo-600"/>
                    <div className="flex flex-col gap-1">
                      {image && <>
                        <img className=" w-20 h-20 object-cover rounded-full"
                        src={preview} alt="new image" />
                        <div onClick={() => {setImage(null)}}
                        className="p-1  border rounded-md bg-green-800  hover:opacity-90 text-center text-xs text-white">
                          Remove
                        </div>
                      </>}
                      {!image && <label for='fileSelection' className="border-dashed border-w-2 border text-sm text-center text-gray-600 cursor-pointer hover:opacity-90 hover:bg-gray-50 p-5 rounded-lg">
                        <span className="flex text-gray-500 items-center">
                          <File className="w-4 h-4 mr-1"/>
                          Select New Picture
                        </span>
                        <input onChange={(e) => {handleImageChange(e)}} type="file"  className="hidden" name="" id="fileSelection" />
                      </label>}
                    </div>
                  </div>
                  {/* default images available  */}
                  <div className="flex gap-2 flex-start items-center border mt-2 ">
                    {defaultImages && defaultImages.map((image,index) => 
                      <div className="rounded-lg p-1 rounded-lg border  border-gray-300 ">
                        <img src={`${image}`} alt={`def${index}`} 
                        onClick={() => {
                          grabDefaultImage(image)
                        }}
                         className="object-cover w-10 h-10 hover:opacity-80"/>
                      </div>
                  )}
                  </div>
                  <div className="flex justify-center items-center">
                    <button 
                    onClick={handleSaveProfile}
                    className="border py-2 px-10 mt-5 rounded-md hover:bg-opacity-80 bg-blue-500 text-white"> 
                      Change Image 
                    </button>
                  </div>
                </div>
          </div>
    )
  }

  const LogoutPanel = () => {
    return
  }
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        languageDropdownRef.current &&
        !languageDropdownRef.current.contains(event.target)
      ) {
        setIsLanguageDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);
  const handleLanguageSelect = (language) => {
    setSelectedLanguage(language);
    setIsLanguageDropdownOpen(false);
  };
  return (
    <div className="min-h-screen bg-gray-50 flex justify-center">
      <div className="w-full bg-white shadow-sm transition-all duration-300 hover:shadow-md">
        <div className="p-4 ">
         
          {/* Profile Section */}
          <div className=" p-1 border-b rounded-md flex items-center mb-2 transform transition-all duration-300 hover:scale-[1.02]">
            <div className="w-16 h-16 rounded-full overflow-hidden mr-4 border-2 border-transparent hover:border-blue-400 transition-all duration-300">
              <img
                src={`${config.BASE_URL}${currentUser?.picture}`}
                alt="Profile"
                className="w-full h-full object-cover object-top transition-transform duration-500 hover:scale-110"
              />
            </div>
            <div className="flex-1">
              <h2 className="font-semibold text-gray-800">{`${currentUser?.first_name} ${currentUser?.last_name}`}</h2>
              <p className="text-gray-500 text-sm">Username: {`@${currentUser?.username}`}</p>
              <p className="text-gray-500 text-sm">Email: {`${currentUser?.email}`}</p>
            </div>
            <button 
            onClick={() => {setShowFormModal(true)}}
            className="text-blue-500 cursor-pointer transition-all duration-200 hover:text-blue-600 hover:scale-110">
              <i className="fas fa-user-edit"></i>
            </button>
          </div>
          {/* update picture form section  */}
          {showFormModal && <UpdateImageForm />}
          {/* Security Section */}
          <div className="mb-6 transform transition-all duration-300">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Security</h3>
            <div className="bg-white rounded-lg shadow-sm">

              <div
                className="flex items-center justify-between p-3 border-b border-gray-100 transition-colors duration-200 hover:bg-gray-50 cursor-pointer"
                onClick={() => {setPassmode('Change'),setShowPassModal(true)}}
              >
                <div className="flex items-center">
                  <i className="fas fa-lock text-gray-400 mr-3 transition-all duration-200 group-hover:text-blue-500"></i>
                  <span className="text-gray-700">Change Password</span>
                </div>
                <i className="fas fa-chevron-right text-gray-300 cursor-pointer transition-transform duration-200 hover:translate-x-1"></i>
              </div>
              <div
                className="flex items-center justify-between p-3 border-b border-gray-100 transition-colors duration-200 hover:bg-gray-50 cursor-pointer"
                onClick={() => {setPassmode("Reset"),setShowPassModal(true)}}
              >
                <div className="flex items-center">
                  <i className="fas fa-key text-gray-400 mr-3 transition-all duration-200 group-hover:text-blue-500"></i>
                  <span className="text-gray-700">Reset Password</span>
                </div>
                <i className="fas fa-chevron-right text-gray-300 cursor-pointer transition-transform duration-200 hover:translate-x-1"></i>
              </div>
              
              <div className="flex items-center justify-between p-3 border-b border-gray-100 transition-colors duration-200 hover:bg-gray-50">
                <div className="flex items-center">
                  <i className="fas fa-shield-alt text-gray-400 mr-3"></i>
                  <span className="text-gray-700">
                    Two-Factor Authentication
                  </span>
                </div>
                <div
                  className={`w-12 h-6 flex items-center rounded-full p-1 cursor-pointer transition-colors duration-300 ${twoFactorEnabled ? "bg-blue-500" : "bg-gray-300"}`}
                  onClick={() => setTwoFactorEnabled(!twoFactorEnabled)}
                >
                  <div
                    className={`bg-white w-5 h-5 rounded-full shadow-md transform transition-transform duration-300 ${twoFactorEnabled ? "translate-x-6" : "translate-x-0"}`}
                  ></div>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 transition-colors duration-200 hover:bg-gray-50">
                <div className="flex items-center">
                  <i className="fas fa-fingerprint text-gray-400 mr-3"></i>
                  <span className="text-gray-700">Biometric Login</span>
                </div>
                <div
                  className={`w-12 h-6 flex items-center rounded-full p-1 cursor-pointer transition-colors duration-300 ${biometricEnabled ? "bg-blue-500" : "bg-gray-300"}`}
                  onClick={() => setBiometricEnabled(!biometricEnabled)}
                >
                  <div
                    className={`bg-white w-5 h-5 rounded-full shadow-md transform transition-transform duration-300 ${biometricEnabled ? "translate-x-6" : "translate-x-0"}`}
                  ></div>
                </div>
              </div>
            </div>
          </div>
          {/* Wallet Section */}
          <div className="mb-6 transform transition-all duration-300">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Wallet</h3>
            <div className="bg-white rounded-lg shadow-sm">
              <div className="flex items-center justify-between p-3 border-b border-gray-100 cursor-pointer transition-colors duration-200 hover:bg-gray-50">
                <div className="flex items-center">
                  <i className="fas fa-university text-gray-400 mr-3 transition-all duration-200 hover:text-blue-500"></i>
                  <span className="text-gray-700">Linked Bank Accounts</span>
                </div>
                <i className="fas fa-chevron-right text-gray-300 transition-transform duration-200 hover:translate-x-1"></i>
              </div>
              <Link to='/payment-meth'
                data-readdy="true"
                className="flex items-center justify-between p-3 cursor-pointer transition-colors duration-200 hover:bg-gray-50 no-underline"
              >
                <div className="flex items-center">
                  <i className="fas fa-credit-card text-gray-400 mr-3 transition-all duration-200 hover:text-blue-500"></i>
                  <span className="text-gray-700">Default Payment Method</span>
                </div>
                <i className="fas fa-chevron-right text-gray-300 transition-transform duration-200 hover:translate-x-1"></i>
              </Link>
            </div>
          </div>
          {/* Notifications Section */}
          <div className="mb-6 transform transition-all duration-300">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Notifications
            </h3>
            <div className="bg-white rounded-lg shadow-sm">
              <div className="flex items-center justify-between p-3 border-b border-gray-100 transition-colors duration-200 hover:bg-gray-50">
                <div className="flex items-center">
                  <i className="fas fa-bell text-gray-400 mr-3"></i>
                  <span className="text-gray-700">Push Notifications</span>
                </div>
                <div
                  className={`w-12 h-6 flex items-center rounded-full p-1 cursor-pointer transition-colors duration-300 ${pushNotificationsEnabled ? "bg-blue-500" : "bg-gray-300"}`}
                  onClick={() =>
                    setPushNotificationsEnabled(!pushNotificationsEnabled)
                  }
                >
                  <div
                    className={`bg-white w-5 h-5 rounded-full shadow-md transform transition-transform duration-300 ${pushNotificationsEnabled ? "translate-x-6" : "translate-x-0"}`}
                  ></div>
                </div>
              </div>
              <div className="flex items-center justify-between p-3 transition-colors duration-200 hover:bg-gray-50">
                <div className="flex items-center">
                  <i className="fas fa-envelope text-gray-400 mr-3"></i>
                  <span className="text-gray-700">Email Alerts</span>
                </div>
                <div
                  className={`w-12 h-6 flex items-center rounded-full p-1 cursor-pointer transition-colors duration-300 ${emailAlertsEnabled ? "bg-blue-500" : "bg-gray-300"}`}
                  onClick={() => setEmailAlertsEnabled(!emailAlertsEnabled)}
                >
                  <div
                    className={`bg-white w-5 h-5 rounded-full shadow-md transform transition-transform duration-300 ${emailAlertsEnabled ? "translate-x-6" : "translate-x-0"}`}
                  ></div>
                </div>
              </div>
            </div>
          </div>
          {/* Preferences Section */}
          <div className="mb-6 transform transition-all duration-300">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Preferences
            </h3>
            <div className="bg-white rounded-lg shadow-sm">
              <div className="relative">
                <div
                  className="flex items-center justify-between p-3 border-b border-gray-100 cursor-pointer transition-colors duration-200 hover:bg-gray-50"
                  onClick={() =>
                    setIsLanguageDropdownOpen(!isLanguageDropdownOpen)
                  }
                  id="language-selector"
                >
                  <div className="flex items-center">
                    <i className="fas fa-globe text-gray-400 mr-3"></i>
                    <span className="text-gray-700">Language</span>
                  </div>
                  <div className="flex items-center">
                    <span className="text-gray-500 mr-2">
                      {selectedLanguage}
                    </span>
                    <i
                      className={`fas fa-chevron-${isLanguageDropdownOpen ? "up" : "down"} text-gray-300 transition-transform duration-200`}
                    ></i>
                  </div>
                </div>
                {isLanguageDropdownOpen && (
                  <div
                    ref={languageDropdownRef}
                    className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg py-1 z-10 animate-fadeIn"
                    id="language-dropdown"
                    style={{ animation: "fadeIn 0.2s ease-in-out" }}
                  >
                    {languages.map((language, index) => (
                      <div
                        key={language}
                        className={`px-4 py-2 cursor-pointer hover:bg-gray-50 transition-colors duration-150 ${
                          selectedLanguage === language
                            ? "text-blue-500 font-medium"
                            : "text-gray-700"
                        }`}
                        onClick={() => handleLanguageSelect(language)}
                        style={{
                          animation: `slideIn 0.2s ease-in-out ${index * 0.03}s both`,
                        }}
                      >
                        {language}
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <div className="flex items-center justify-between p-3 transition-colors duration-200 hover:bg-gray-50">
                <div className="flex items-center">
                  <i className="fas fa-code-branch text-gray-400 mr-3"></i>
                  <span className="text-gray-700">Settings Version</span>
                </div>
                <span className="text-gray-500">2.3.6</span>
              </div>
            </div>
          </div>
          {/* Referral & Rewards Section */}
          <div className="mb-6 transform transition-all duration-300">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Referral & Rewards
            </h3>
            <div className="bg-white rounded-lg shadow-sm">
              <div className="flex items-center justify-between p-3 border-b border-gray-100 cursor-pointer transition-colors duration-200 hover:bg-gray-50">
                <div className="flex items-center">
                  <i className="fas fa-user-plus text-gray-400 mr-3 transition-all duration-200 hover:text-blue-500"></i>
                  <span className="text-gray-700">Invite Friends</span>
                </div>
                <i className="fas fa-chevron-right text-gray-300 transition-transform duration-200 hover:translate-x-1"></i>
              </div>
              <div className="flex items-center justify-between p-3 cursor-pointer transition-colors duration-200 hover:bg-gray-50">
                <div className="flex items-center">
                  <i className="fas fa-gift text-gray-400 mr-3 transition-all duration-200 hover:text-blue-500"></i>
                  <span className="text-gray-700">View Rewards</span>
                </div>
                <i className="fas fa-chevron-right text-gray-300 transition-transform duration-200 hover:translate-x-1"></i>
              </div>
            </div>
          </div>
          {/* Help & Support Section */}
          <div className="mb-6 transform transition-all duration-300">
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              Help & Support
            </h3>
            <div className="bg-white rounded-lg shadow-sm">
              <a
                href="https://readdy.ai/home/0dcdf096-52d5-4665-acc2-bf17c64c3386/0ee2298f-1d41-4fee-be4e-b19e4835d0d9"
                data-readdy="true"
                className="flex items-center justify-between p-3 border-b border-gray-100 cursor-pointer transition-colors duration-200 hover:bg-gray-50 no-underline"
              >
                <div className="flex items-center">
                  <i className="fas fa-question-circle text-gray-400 mr-3 transition-all duration-200 hover:text-blue-500"></i>
                  <span className="text-gray-700">Help Center</span>
                </div>
                <i className="fas fa-chevron-right text-gray-300 transition-transform duration-200 hover:translate-x-1"></i>
              </a>
              <div className="flex items-center justify-between p-3 border-b border-gray-100 cursor-pointer transition-colors duration-200 hover:bg-gray-50">
                <div className="flex items-center">
                  <i className="fas fa-shield-alt text-gray-400 mr-3 transition-all duration-200 hover:text-blue-500"></i>
                  <span className="text-gray-700">Privacy Policy</span>
                </div>
                <i className="fas fa-chevron-right text-gray-300 transition-transform duration-200 hover:translate-x-1"></i>
              </div>
              <div className="flex items-center justify-between p-3 cursor-pointer transition-colors duration-200 hover:bg-gray-50">
                <div className="flex items-center">
                  <i className="fas fa-file-alt text-gray-400 mr-3 transition-all duration-200 hover:text-blue-500"></i>
                  <span className="text-gray-700">Terms & Conditions</span>
                </div>
                <i className="fas fa-chevron-right text-gray-300 transition-transform duration-200 hover:translate-x-1"></i>
              </div>
            </div>
          </div>
          {/* Logout Button */}
          <div className="mt-8 mb-4">
            <button className="w-full py-3 bg-red-50 text-red-600 font-medium rounded-lg !rounded-button whitespace-nowrap cursor-pointer hover:bg-red-100 transition-all duration-300 hover:shadow-md transform hover:-translate-y-1">
              <i className="fas fa-sign-out-alt mr-2"></i>
              Logout
            </button>
          </div>
        </div>

         {/* PIN Manage  Modal */}
        {showPassModal && (
        <PinPasswordManger name="Password" mode={passMode} closeModal={setShowPassModal} />)}
      </div>

      <style jsx>{`
                @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
                }
                @keyframes slideIn {
                from { opacity: 0; transform: translateX(10px); }
                to { opacity: 1; transform: translateX(0); }
                }
                @keyframes scaleIn {
                from { opacity: 0; transform: scale(0.95); }
                to { opacity: 1; transform: scale(1); }
                }
      `}</style>
    </div>
  );
};
export default Settings;
