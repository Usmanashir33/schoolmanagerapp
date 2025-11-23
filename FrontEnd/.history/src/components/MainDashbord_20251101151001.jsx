// The exported code uses Tailwind CSS. Install Tailwind CSS in your dev environment to ensure all styles work.
import { BrowserRouter as Router, Route, Routes,  useNavigate, Link } from 'react-router-dom';
import { useContext, useState } from 'react';
import Home from './Home';
import Sidebar from './Sidebar';
import Dashboard from './Dashbord';
import Rightbar from './RightBar';
import Profile from './Profile';
import SendingMoney from './SendingMoney';
import Withdrawal from './Withdrawal';
import Transections from './Transections';
import Wallet from './Wallet';
import Settings from './Settings';
import PaymentMethods from './PaymentMethods';
import { BanknoteArrowUp, Bell,  ChevronDownIcon,  ChevronLast,  MessageSquare, StarIcon } from 'lucide-react';
import HelpCenterPage from './HelpCenter';
import WithdrawalRequests from './AAStaff/WithdrawalRequets';
import { uiContext } from '../customContexts/UiContext';
import { authContext } from '../customContexts/AuthContext';
import config from '../customHooks/ConfigDetails';
import { liveContext } from '../customContexts/LiveContext';
import TransectionStatus from './TransectionStatus';
import Refarrels from './Refarrels';

const MainDashbord = () => {
  const navigate = useNavigate()
  const {currentUser} = useContext(authContext);
  const {unreadNotif,withdrawalRequests} = useContext(liveContext);
  const [showAccounts,setShowAccounts] = useState(false);
  const dropdownRef =  ReactuseRef();
  
  const {isSidebarOpen, setIsSidebarOpen,greetUser,readNotifi} = useContext(uiContext);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen); 
  };
  
  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden w-full">
      {/* Sidebar */}
      <Sidebar/>

      {/* Main Content */}
      {<div className="flex-1 flex ">
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Top Navbar */}
          { <header className="bg-white shadow-sm z-10 items-center border-b ">
            <div className="flex items-center justify-between h-16 px-6">

              <div className="flex items-center">
                <button onClick={toggleSidebar} className="text-gray-500 focus:outline-none md:hidden cursor-pointer !rounded-button whitespace-nowrap">
                  <i className="fas fa-bars text-lg"></i>
                </button>
                <h2 className="ml-4 text-lg font-medium text-green-900 md:ml-0">{greetUser()}</h2>
              </div>
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-4">
                  <button 
                  onClick={() => {navigate('/notif')}}
                  className=" lg:hidden relative text-gray-600 hover:text-gray-900 cursor-pointer !rounded-button whitespace-nowrap">
                    {/* <i className="fas fa-bell text-xl"></i> */}
                    <Bell strokeWidth={1.2} />
                    {unreadNotif > 0  && <span className="absolute -top-1  -right-1 w-max text-xs px-1 rounded-lg font-medium bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                      {readNotifi(unreadNotif)}

                    </span>} 
                  </button>
                  <button className="relative text-gray-600 hover:text-gray-900 cursor-pointer !rounded-button whitespace-nowrap">
                    <MessageSquare strokeWidth={1.2} className="w-6 h-6 text-gray-600 text-xl " />
                    <span className="absolute -top-1 -right-1 w-max text-xs px-1 rounded-lg font-mediumanimate-pulse bg-blue-500 text-white text-xs rounded-full flex items-center justify-center">2</span>
                  </button>
                </div>
                <div className="relative ">
                  
                  <button className="flex items-center text-gray-700 focus:outline-none cursor-pointer !rounded-button whitespace-nowrap">
                    <span className="mr-2 text-md font-medium">@{currentUser?.username}</span>
                    <div className="w-8 h-8 overflow-hidden rounded-full bg-gray-200">
                      <img
                      src={`${config.BASE_URL}${currentUser?.picture}`}
                        alt="User Avatar"
                        className="object-cover w-full h-full"
                      />
                    </div>
                    <ChevronDownIcon  onClick={() => {setShowAccounts(!showAccounts)}}
                    strokeWidth={3} className=' ml-2 w-4 text-gray-600 cursor-pointer h-4 text-gray-600 cursor-pointer hover:text-gray-900 bg-gray-100 rounded-lg'/>
                  </button>

                  {/* dropdown here  */}
                  {showAccounts && 
                  <div  ref={dropdownRef} className="absolute top-7 w-fullright-0  mt-2  bg-white border border-gray-200 rounded-md shadow-lg">
                    <ul className="">
                      <li>
                       {currentUser?.is_staff && 
                        <Link to={`/staffusers`}className="flex items-center px-3 py-2 text-gray-600 rounded-lg hover:bg-gray-50 border ">
                          <StarIcon strokeWidth={1} className="mr-2 w-3  text-green-900"/>
                          <span className="text-sm ">Staff Account </span>
                        </Link>}
                      </li>
                    </ul>
                  </div>}

                </div>
              </div>
            </div>
          </header>}

           <Routes>
              <Route 
                  path='/home' 
                  element={
                    <main className="flex-1 overflow-y-auto p-2 bg-gray-50">
                      <Home/>
                    </main>
                  } 
              />
              <Route 
                  path='/trx-status/:id' 
                  element={
                    <main className="flex-1 overflow-y-auto p-2 bg-gray-50">
                      <TransectionStatus/>
                    </main>
                  } 
              />
              <Route 
                  path='Wallet' 
                  element={
                    <main className="flex-1 overflow-y-auto p-2 bg-gray-50">
                      <Wallet/>
                    </main>
                  } 
              />

              <Route 
                  path='profile' 
                  element={
                    <main className="flex-1 overflow-y-auto px-2 bg-gray-50 ">
                      <Profile/>
                    </main>
                  } 
              />

              <Route 
                  path='refarrels' 
                  element={
                    <main className="flex-1 overflow-y-auto px-2 bg-gray-50 ">
                      <Refarrels/>
                    </main>
                  } 
              />
              <Route 
                  path='notif' 
                  element={
                    <main className="flex-1 overflow-y-auto px-2 bg-gray-50 ">
                      <Rightbar/>
                    </main>
                  } 
              />
              <Route 
                  path='internal-trns' 
                  element={
                    <main className="flex-1 overflow-y-auto px-2 bg-gray-50 ">
                      <SendingMoney/>
                    </main>
                  } 
              />
              <Route 
                  path='transections' 
                  element={
                    <main className="flex-1 overflow-y-auto px-2 bg-gray-50 ">
                      <Transections/>
                    </main>
                  } 
              />
              <Route 
                  path='withdraw' 
                  element={
                    <main className="flex-1 overflow-y-auto px-2 bg-gray-50 ">
                      <Withdrawal/>
                    </main>
                  } 
              />
              <Route 
                  path='settings' 
                  element={
                    <main className="flex-1 overflow-y-auto px-2 bg-gray-50  ">
                      <Settings/>
                    </main>
                  } 
              />
              <Route 
                  path='payment-meth' 
                  element={
                    <main className="flex-1 overflow-y-auto px-2 bg-gray-50 ">
                      <PaymentMethods/>
                    </main>
                  } 
              />
              <Route 
                  path='help-center' 
                  element={
                    <main className="flex-1 overflow-y-auto px-2 bg-gray-50 ">
                      <HelpCenterPage/>
                    </main>
                  } 
              />
          </Routes>
        </div>


        {/* Notifications Panel */}
        <div className="hidden lg:block 0 bg-white border-l overflow-y-auto w-1/3  ">
           <Rightbar/>
        </div>
      </div>}

    </div>
  );
};

export default MainDashbord;
