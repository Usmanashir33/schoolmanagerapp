import  { useState, useEffect, useContext } from "react";
import PinPasswordManger from "./PinPasswordManger";
import {Copy, Eye, EyeClosed, EyeClosedIcon, EyeIcon } from 'lucide-react';
import walletBg from "../assets/images/walletbg.jpg";

import { useNavigate } from "react-router";
import AddMoneyModal from "./AddMoneyModal";
import { authContext } from "../customContexts/AuthContext";
import { uiContext } from "../customContexts/UiContext";
const Wallet = () => {
  const  {currentUser} =useContext(authContext);
  const {formatNaira,copyToClipboard}  = useContext(uiContext)
  const [addMoney,setAddmoney] = useState(false);
  const navigate = useNavigate();
  const [isVisible, setIsVisible] = useState(false);
  const [pinMode, setPinMode] = useState("");
  const [showPinModal, setShowPinModal] = useState(false);
  const [showBalance, setShowBalance] = useState(true);

  const toggleAddmoney = () => {
    setAddmoney(!addMoney)
  }
 

  const toggleBalanceVisibility = () => {
    setShowBalance(!showBalance);
  };
  useEffect(() => {
    setIsVisible(true);
  }, []);
  return (
    <div className="min-h-screen bg-gray-50 flex justify-center">
      <div
        className={` w-full bg-white shadow-sm transform transition-all duration-1000 ${isVisible ? "translate-y-0 opacity-100" : "translate-y-10 opacity-0"}`}
      >
        {/* Wallet Card */}
        <div className="px-3">
          <div
            className="rounded-xl  p-4 text-white shadow-md transform transition-all duration-500 hover:scale-[1.02] hover:shadow-lg overflow-hidden relative"
            style={{
              // backgroundImage: `url('')`,
              backgroundImage: `url(${walletBg})`,
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600/80 to-indigo-600/80"></div>
            <div className="relative z-10">
              <div className="mb-2">
                <p className="text-sm text-purple-100">Total Balance</p>
                <div className="flex items-center">
                  <h2 className="text-2xl font-bold">
                    {showBalance
                      ? `${formatNaira(currentUser?.account?.account_balance)}`
                      : "******"}
                  </h2>
                    {showBalance && <EyeClosed className="ml-3 w-5 cursor-pointer" onClick={() => {toggleBalanceVisibility()}} />}
                    {!showBalance &&  <EyeIcon   className="ml-3 w-5 cursor-pointer" onClick={() => {toggleBalanceVisibility()}}/>}

                </div>
              </div>
              <div className="flex gap-3 mt-4">
                <button onClick={toggleAddmoney}
                className="bg-gray-900 bg-opacity-30 hover:bg-opacity-50 transition-all duration-300 py-2 px-4 rounded-lg flex-1 text-sm font-medium flex items-center justify-center cursor-pointer hover:transform hover:scale-105 !rounded-button whitespace-nowrap">
                  <i className="fas fa-plus mr-2"></i> Fund Wallet
                </button>
                <button  onClick={() => {navigate("/withdraw")}}
                className="bg-gray-900 bg-opacity-30 hover:bg-opacity-50 transition-all duration-300 py-2 px-4 rounded-lg flex-1 text-sm font-medium flex items-center justify-center cursor-pointer hover:transform hover:scale-105 !rounded-button whitespace-nowrap">
                  <i className="fas fa-arrow-down mr-2"></i>
                  {/* <ArrowDown className="p-1 font-medium text-s"/> */}
                   Withdraw
                </button>
              </div>
              <div className="mt-4 pt-3 border-t border-purple-400 border-opacity-30">
                <p className="text-xs ">Account Number</p>
                <p className="text-sm font-medium flex items-center gap-5">
                  {currentUser?.account?.accountnumbers[0]?.account_number}
                  <Copy onClick={() => copyToClipboard(currentUser?.account?.accountnumbers[0]?.account_number || 'null','account number copied')}
                   className="w-4 h-4 text-gray-200 hover:text-white" />
                </p>
                <p className="text-xs text-white mt-1">
                  {currentUser?.account?.accountnumbers[0]?.bank_name} • Savings Account
                </p>
              </div>
            </div>
          </div>
          {/* Quick Actions */}
          <div className="grid grid-cols-4 gap-2 mt-4">
            <div className="flex flex-col items-center p-3 cursor-pointer transform transition-all duration-300 hover:scale-110">
              <div  onClick={() => {navigate("/internal-trns")}}
              className="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center text-blue-500 mb-1">
                <i className="fas fa-paper-plane"></i>
              </div>
              <span className="text-xs text-gray-600 whitespace-nowrap">
                Send Money
              </span>
            </div>
            <div className="flex flex-col items-center p-3 cursor-pointer transform transition-all duration-300 hover:scale-110">
              <div onClick={() => {navigate("/internal-trns")}}
               className="w-10 h-10 bg-purple-50 rounded-full flex items-center justify-center text-purple-500 mb-1">
                <i className="fas fa-hand-holding-usd"></i>
              </div>
              <span className="text-xs text-gray-600 whitespace-nowrap">
                Request
              </span>
            </div>
            <div className="flex flex-col items-center p-3 cursor-pointer transform transition-all duration-300 hover:scale-110">
              <div className="w-10 h-10 bg-green-50 rounded-full flex items-center justify-center text-green-500 mb-1">
                <i className="fas fa-file-invoice"></i>
              </div>
              <span className="text-xs text-gray-600 whitespace-nowrap">
                Pay Bills
              </span>
            </div>
            <div className="flex flex-col items-center p-3 cursor-pointer transform transition-all duration-300 hover:scale-110">
              <div className="w-10 h-10 bg-amber-50 rounded-full flex items-center justify-center text-amber-500 mb-1">
                <i className="fas fa-chart-line"></i>
              </div>
              <span className="text-xs text-gray-600 whitespace-nowrap">
                Investments
              </span>
            </div>
          </div>
        </div>


        {/* Account Management */}
        <div className=" border-t">
          <div className="">
            <div
              id="changePinButton"
              onClick={() => {setPinMode("Change"),setShowPinModal(true)}}
              className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg cursor-pointer transition-all duration-300 hover:shadow-sm transform hover:translate-x-1"
            >
              <div className="flex items-center">
                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center text-gray-600 mr-3">
                  <i className="fas fa-shield-alt"></i>
                </div>
                <span className="text-sm font-medium text-gray-800">
                  Change PIN
                </span>
              </div>
              <i className="fas fa-chevron-right text-gray-400"></i>
            </div>

            <div onClick={() => {setPinMode("Reset"),setShowPinModal(true)}}
             className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg cursor-pointer transition-all duration-300 hover:shadow-sm transform hover:translate-x-1">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center text-gray-600 mr-3">
                  <i className="fas fa-key"></i>
                </div>
                <span className="text-sm font-medium text-gray-800">
                  Reset PIN
                </span>
              </div>
              <i className="fas fa-chevron-right text-gray-400"></i>
            </div>
             <div
             className="flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg cursor-pointer transition-all duration-300 hover:shadow-sm transform hover:translate-x-1">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center text-gray-600 mr-3">
                  <i className="fas fa-credit-card"></i>
                </div>
                <span className="text-sm font-medium text-gray-800">
                  Manage Cards
                </span>
              </div>
              <i className="fas fa-chevron-right text-gray-400"></i>
            </div>
          </div>
        </div>
      </div>
        {/* PIN Manage  Modal */}
        {showPinModal && (<PinPasswordManger mode={pinMode} closeModal={setShowPinModal} />)}
        { addMoney &&  < AddMoneyModal toggleModal={toggleAddmoney}/>}
    </div>
  );
};
export default Wallet;
