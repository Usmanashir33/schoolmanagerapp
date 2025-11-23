import  { useContext, useState } from "react";
import { EyeClosed, EyeIcon, EyeOff, } from 'lucide-react';
import { Link, useNavigate } from "react-router";
import AddMoneyModal from "./AddMoneyModal";
import { authContext } from "../customContexts/AuthContext";
import Transections from "./Transections";
import { uiContext } from "../customContexts/UiContext";
const Home = () => {
  const navigate = useNavigate();
  const {currentUser} = useContext(authContext);
  const {formatNaira} = useContext(uiContext);
  const [showBalance, setShowBalance] = useState(false);
  const [showAddMoneyModal, setShowAddMoneyModal] = useState(false);
  const toggleBalance = () => {
    setShowBalance(!showBalance);
  };
  const toggleAddMoneyModal = () => {
    setShowAddMoneyModal(!showAddMoneyModal);
  };

  return (
    <>
      <div className="min-h-screen bg-gray-50 font-san ">
        {/* Header */}
        {/* Main Content */}
        <div className="px-4 py-0 ">
          {/* Balance Card */}
          <div className="bg-blue-600 rounded-xl p-4 text-white mb-5">
            <div className="flex justify-between items-center">
              <p className="text-sm mb-1">Available Balance</p>
              {showBalance
                ?<EyeClosed strokeWidth={1.2} className="w-5 cursor-pointer" onClick={toggleBalance} />
                : 
                <EyeIcon strokeWidth={1.2}  className="w-5 cursor-pointer" onClick={toggleBalance}/>
              }
            </div>
            <h2 className="text-2xl font-bold mb-3">
              {showBalance
                ? `${formatNaira(currentUser?.account?.account_balance)}`
                : 
                " ******* "}
            </h2>
            <div className="flex gap-3">
              <button
                onClick={toggleAddMoneyModal}
                className="flex-1 bg-blue-500 py-2 rounded-lg flex items-center justify-center gap-1 hover:bg-blue-400 transition-colors !rounded-button whitespace-nowrap cursor-pointer"
              >
                <i className="fas fa-plus text-xs"></i>
                <span className="text-sm">Add Money</span>
              </button>
              <Link
                to={`/internal-trns`}
                className="flex-1 bg-blue-500 py-2 rounded-lg flex items-center justify-center gap-1 hover:bg-blue-400 transition-colors !rounded-button whitespace-nowrap cursor-pointer text-white no-underline"
              >
                <i className="fas fa-paper-plane text-xs"></i>
                <span className="text-sm">Send Money</span>
              </Link>
            </div>
          </div>
          {/* Quick Services */}
          <div className="grid grid-cols-3 gap-3 mb-6">
            <div className="bg-white rounded-xl p-4 flex flex-col items-center shadow-sm cursor-pointer hover:shadow-md transition-shadow">
              < className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                <i className="fas fa-wifi text-blue-600"></i>
              </>
              <p className="text-sm">Buy Data</p>
            </div>
            <div className="bg-white rounded-xl p-4 flex flex-col items-center shadow-sm cursor-pointer hover:shadow-md transition-shadow">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                <i className="fas fa-phone text-blue-600"></i>
              </div>
              <p className="text-sm">Buy Airtime</p>
            </div>
            <div className="bg-white rounded-xl p-4 flex flex-col items-center shadow-sm cursor-pointer hover:shadow-md transition-shadow">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                <i className="fas fa-bolt text-blue-600"></i>
              </div>
              <p className="text-sm">Pay Electricity</p>
            </div>
            <div className="bg-white rounded-xl p-4 flex flex-col items-center shadow-sm cursor-pointer hover:shadow-md transition-shadow">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                <i className="fas fa-tv text-blue-600"></i>
              </div>
              <p className="text-sm">TV Subscription</p>
            </div>
            <div className="bg-white rounded-xl p-4 flex flex-col items-center shadow-sm cursor-pointer hover:shadow-md transition-shadow">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mb-2">
                <i className="fas fa-gamepad text-blue-600"></i>
              </div>
              <p className="text-sm">Gaming</p>
            </div>
            <div className="bg-white rounded-xl p-4 flex flex-col items-center shadow-sm cursor-pointer hover:shadow-md transition-shadow">
              <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center mb-2">
                <i className="fas fa-ellipsis-h text-purple-600"></i>
              </div>
              <p className="text-sm">More</p>
            </div>
          </div>
          {/* Recent Transactions */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-3">
              <h2 className="font-medium">Recent Transactions</h2>
              <button className="text-blue-600 text-sm cursor-pointer" 
                onClick={() => {navigate("/transections")}}
              >
                See All
              </button>
            </div>
            <div className="space-y-3">
                <Transections isRecent={true}/>
            </div>
            <div className="space-y-3 bbd hidden  ">
              <div className="bg-white rounded-xl p-3 flex items-center shadow-sm">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                  <i className="fas fa-wifi text-blue-600"></i>
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-medium">Data Bundle</h3>
                  <p className="text-xs text-gray-500">9Mobile - 10GB</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-red-600">-$24.99</p>
                  <p className="text-xs text-gray-500">2:30 PM</p>
                </div>
              </div>
              <div className="bg-white rounded-xl p-3 flex items-center shadow-sm">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                  <i className="fas fa-tv text-blue-600"></i>
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-medium">DSTV Premium</h3>
                  <p className="text-xs text-gray-500">Monthly Subscription</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-red-600">-$45.00</p>
                  <p className="text-xs text-gray-500">Yesterday</p>
                </div>
              </div>
              <div className="bg-white rounded-xl p-3 flex items-center shadow-sm">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                  <i className="fas fa-bolt text-blue-600"></i>
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-medium">Electricity Bill</h3>
                  <p className="text-xs text-gray-500">IKEDC - Prepaid</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-red-600">-$100.00</p>
                  <p className="text-xs text-gray-500">Yesterday</p>
                </div>
              </div>
              <div className="bg-white rounded-xl p-3 flex items-center shadow-sm">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                  <i className="fas fa-phone text-blue-600"></i>
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-medium">Airtime</h3>
                  <p className="text-xs text-gray-500">MTN - Recharge</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-red-600">-$10.00</p>
                  <p className="text-xs text-gray-500">2 days ago</p>
                </div>
              </div>
            </div>
          </div>
          {/* Special Offers */}
          <div>
            <h2 className="font-medium mb-3">Special Offers</h2>
            <div className="relative">
              <div className="overflow-x-auto hide-scrollbar">
                <div className="flex gap-4 pb-6">
                  <div className="min-w-[280px] bg-gradient-to-r from-blue-600 to-blue-500 rounded-xl p-4 text-white cursor-pointer">
                    <div className="font-bold text-xl mb-1">50% Off</div>
                    <div className="text-sm mb-2">On Data Bundles</div>
                    <div className="flex items-center text-xs">
                      <span>Learn More</span>
                      <i className="fas fa-chevron-right ml-1"></i>
                    </div>
                  </div>
                  <div className="min-w-[280px] bg-gradient-to-r from-green-600 to-green-500 rounded-xl p-4 text-white cursor-pointer">
                    <div className="font-bold text-xl mb-1">Free TV</div>
                    <div className="text-sm mb-2">First Month Sub</div>
                    <div className="flex items-center text-xs">
                      <span>Learn More</span>
                      <i className="fas fa-chevron-right ml-1"></i>
                    </div>
                  </div>
                  <div className="min-w-[280px] bg-gradient-to-r from-purple-600 to-purple-500 rounded-xl p-4 text-white cursor-pointer">
                    <div className="font-bold text-xl mb-1">Cashback</div>
                    <div className="text-sm mb-2">On Bill Payments</div>
                    <div className="flex items-center text-xs">
                      <span>Learn More</span>
                      <i className="fas fa-chevron-right ml-1"></i>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex justify-center gap-1 mt-2">
                <div className="w-2 h-2 rounded-full bg-blue-600"></div>
                <div className="w-2 h-2 rounded-full bg-gray-300"></div>
                <div className="w-2 h-2 rounded-full bg-gray-300"></div>
              </div>
            </div>
          </div>
        </div>
        {showAddMoneyModal && <AddMoneyModal  toggleModal={toggleAddMoneyModal}/>}
      </div>
    </>
  );
};
export default Home;
