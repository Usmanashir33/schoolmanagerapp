// The exported code uses Tailwind CSS. Install Tailwind CSS in your dev environment to ensure all styles work.
import { CopyIcon, Edit3, SidebarClose } from "lucide-react";
import { useState, useEffect, useContext } from "react";
import { authContext } from "../customContexts/AuthContext";
import { uiContext } from "../customContexts/UiContext";
import config from "../customHooks/ConfigDetails";
import useRequest from "../customHooks/RequestHook";
import profileBgImage from '../assets/images/profilebg.jpg'
import W from '../assets/images/walletbg2.jpg'

const Profile = () => {
  const {sendArbitRequest} = useRequest();
  const [isEditingBank, setIsEditingBank] = useState(false);
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const {currentUser,setCurrentUser}  = useContext(authContext);
  const {copyToClipboard,setSuccess}  = useContext(uiContext);
  const [bankName, setBankName] = useState("Chase Bank");
  const [accountNumber, setAccountNumber] = useState("****4567");
  const [userInfoForm,setUserInfoForm] = useState({});
  
  const [loading, setLoading] = useState(false);
  // Time-based greeting
  const [greeting, setGreeting] = useState("");
  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good morning");
    else if (hour < 18) setGreeting("Good afternoon");
    else setGreeting("Good evening");
  }, []);
  useEffect(() => {
    setUserInfoForm({
    first_name: currentUser?.first_name || "",
    last_name: currentUser?.last_name || "",
    username: currentUser?.username || "",
    email: currentUser?.email || "",
    phone: currentUser?.phone_number|| "",
    address: "123 Dandinshe Dala local Government kano state Nigeria",
  })
  },[currentUser])
  
  const handleSaveBank = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setIsEditingBank(false);
    }, 1000);
  };
  const handleSaveProfileResp = (data) => {
    console.log('data: ', data);
    setSuccess(data.success);
    setCurrentUser(data.user);
    setIsEditingProfile(false);
  }
  const handleSaveProfile = () => {
    let data = new FormData()
    Object.entries(userInfoForm).forEach(([key,value]) => {
      data.append(key,value)
    })
    let url = `/authuser/update-profile/`
    sendArbitRequest(url,"PUT",data,handleSaveProfileResp,true,true)
  };
  return (
    <div className="min-h-screen flex justify-center ">
      <div className="w-full max-w-m">

        {/* Header with profile */}
        <div className="relative bg-gradient-to-r from-purple-600 to-indigo-600  text-white shadow-lg transform transition-all duration-300 ease-in-out rounded-b-xl">
           <img
              src={profileBgImage}
              alt="Card Background"
              className="abosolute w-full h-32 object-cover rounded-b-xl"
            />
          <div className="absolute top-0 p-4">
            <div className="flex items-center">
            <div className="relative">
              <img
                src={`${config.BASE_URL}${currentUser?.picture}`}
                alt="Profile"
                className="w-16 h-16 rounded-full border-2 border-white object-cover object-top"
              />
              <div className="absolute bottom-0 right-0 w-4 h-4 bg-green-400 rounded-full border-2 border-white"></div>
            </div>
            <div className="ml-4">
              <h2 className="text-xl font-bold">{currentUser?.first_name} {currentUser?.last_name}</h2>
              <div className="flex">
                <p className="text-indigo-100 font-medium">{currentUser?.account?.account_id}</p>
                <CopyIcon
                      strokeWidth={1.3}
                      onClick={() => copyToClipboard(currentUser?.account?.account_id,'account number copied')}
                      className="text-white  p-1 text-sm hover:text-indigo-200 transition-all duration-200 cursor-pointer"
                    />

              </div>
              <p className="text-indigo-100">Premium Account</p>
            </div>
          </div>
          <p className="text-xl">{greeting}</p>
          </div>
          
        </div>
       
        {/* Bank Details */}
        <div className=" mt-2 bg-white rounded-2xl shadow-md px-6 pt-2 pb-4 transform transition-all duration-300 ease-in-out hover:shadow-lg">
          {isEditingBank ? (
            <div className="space-y-3">
              <h3 className="text-lg font-medium text-gray-800 mb-4">
                Edit Bank Details
              </h3>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">
                  Bank Name
                </label>
                <input
                  type="text"
                  value={bankName}
                  onChange={(e) => setBankName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">
                  Account Number
                </label>
                <input
                  type="text"
                  value={accountNumber}
                  onChange={(e) => setAccountNumber(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                />
              </div>
              <div className="flex space-x-3 pt-2">
                <button
                  onClick={() => setIsEditingBank(false)}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 px-4 rounded-lg transition-all duration-200 !rounded-button whitespace-nowrap cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveBank}
                  className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-lg transition-all duration-200 !rounded-button whitespace-nowrap cursor-pointer"
                >
                  {loading ? (
                    <i className="fas fa-spinner fa-spin"></i>
                  ) : (
                    "Save Changes"
                  )}
                </button>
              </div>
            </div>
          ) : (
            <>
            <div className=" text-md font-medium text-gray-800 mb-2 flex justify-between">
               <span>Deposite Bank Details</span>
               <CopyIcon 
               onClick={() => copyToClipboard(
                ` Acc Number :  ${currentUser?.account?.accountnumbers[0]?.account_number || 'null'}
                Bank Name : ${currentUser?.account?.accountnumbers[0]?.bank_name || 'null'}`
                
                ,'Account Details  Copied')}
               className="hover:bg-gray-100 hover:py-2 p-1 rounded-sm"/>
               </div>
              <div className="flex justify-between items-center mb-1">
                
                <div>
                  <label className="text-sm text-gray-500">Bank Name</label>
                  <p className="text-gray-800 font-medium">{currentUser?.account?.accountnumbers[0]?.bank_name}</p>
                </div>
              </div>
              <div className="flex justify-between items-center mb-4 ">
                <div>
                  <label className="text-sm text-gray-500">
                    Account Number
                  </label>
                  <p className="text-gray-800 font-medium"> {currentUser?.account?.accountnumbers[0]?.account_number} </p>
                </div>
                <CopyIcon
                    onClick={() => copyToClipboard(currentUser?.account?.accountnumbers[0]?.account_number || 'null','account number copied')}
                    className="text-indigo-500  p-1 text-sm hover:text-indigo-400 transition-all duration-200 cursor-pointer"
                  />
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <label className="text-sm text-gray-500 mr-2">
                    KYC Status
                  </label>
                  <span className="flex items-center text-green-600">
                    <i className="fas fa-check-circle mr-1"></i>
                    <span className="text-sm">Verified</span>
                  </span>
                </div>
                <button className="text-indigo-600 hover:text-indigo-800 transition-all duration-200 flex items-center cursor-pointer">
                  <i className="fas fa-file-alt mr-1"></i>
                  <span className="text-sm">Update KYC</span>
                </button>
              </div>
            </>
          )}
        </div>

        {/* User Profile Form */}
        <div className=" my-3 bg-white rounded-2xl shadow-md overflow-hidden transform transition-all duration-300 ease-in-out">
          <div
            className="p-4 bg-gray-50  flex justify-between items-center cursor-pointer"
            
          >
            <h3 className="text-lg font-medium text-indigo-800 ">
                  {isEditingProfile ? 
                ("Edit Personal Information")
                : 
                ("Personal Information")}
            </h3>
                {isEditingProfile ? 
                (<SidebarClose className="text-indigo-700 w-5" onClick={() => setIsEditingProfile(!isEditingProfile)} />)
                : 
                (<Edit3 className="text-indigo-700 w-5" onClick={() => setIsEditingProfile(!isEditingProfile)} />)}
          </div>

             {/* Account Details */}
          {!isEditingProfile && <div className="p-4 border-t">
            
            <div className="space-y-3">
              <div className="flex justify-between">
                <p className="text-sm text-gray-600">Full Name</p>
                <p className="text-sm font-medium text-gray-800">{currentUser?.first_name} {currentUser?.last_name}</p>
              </div>
              <div className="flex justify-between">
                <p className="text-sm text-gray-600">Username</p>
                <p className="text-sm font-medium text-gray-800">@{currentUser?.username}</p>
              </div>
              <div className="flex justify-between">
                <p className="text-sm text-gray-600">Email</p>
                <p className="text-sm font-medium text-gray-800">
                  {currentUser?.email}
                </p>
              </div>
              <div className="flex justify-between">
                <p className="text-sm text-gray-600">Phone</p>
                <p className="text-sm font-medium text-gray-800">
                  {currentUser?.phone_number || "Not provided"}
                </p>
              </div>
              <div className="flex justify-between">
                <p className="text-sm text-gray-600">KYC Status</p>
                <div className="flex items-center">
                  <span className="text-sm font-medium text-gray-800 mr-1">
                    Verified
                  </span>
                  <span className="text-green-500">
                    <i className="fas fa-check-circle"></i>
                  </span>
                </div>
              </div>
            </div>
            
          </div>}

          {isEditingProfile && (
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">
                  First Name
                </label>
                <input
                  type="text"
                  name="first_name"
                  value={userInfoForm.first_name}
                  onChange={(e) => setUserInfoForm({ ...userInfoForm, first_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">
                  Last Name
                </label>
                <input
                  type="text"
                  name="last_name"
                  value={userInfoForm.last_name}
                  onChange={(e) => setUserInfoForm({ ...userInfoForm, last_name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  disabled
                  value={userInfoForm.email}
                  onChange={(e) => setUserInfoForm({ ...userInfoForm, email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">
                  Phone Number
                </label>
                <input
                  type="tel"
                  name="phone"
                  disabled
                  value={userInfoForm.phone}
                  onChange={(e) => setUserInfoForm({ ...userInfoForm, phone: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">
                  Address
                </label>
                <textarea
                  name="address"
                  value={userInfoForm.address}
                  onChange={(e) => setUserInfoForm({ ...userInfoForm, address: e.target.value })}
                  rows={2}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                ></textarea>
              </div>
              <div className="flex space-x-3 pt-2">
                <button
                  onClick={() => setIsEditingProfile(false)}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 px-4 rounded-lg transition-all duration-200 !rounded-button whitespace-nowrap cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveProfile}
                  className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-lg transition-all duration-200 !rounded-button whitespace-nowrap cursor-pointer"
                >
                  {loading ? (
                    <i className="fas fa-spinner fa-spin"></i>
                  ) : (
                    "Save Changes"
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
export default Profile;
