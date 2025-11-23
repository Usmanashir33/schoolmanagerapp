import { BrowserRouter as Router, Route, Routes, Navigate, Link, useNavigate } from 'react-router-dom';
import { useContext, useState } from "react";
import AAUsers from "./AAUsers";
import AATrxs from "./AATrxs";
import Analysis from "./Analysis";

import { BanknoteArrowUp, Gauge, LineChart, Lock, LucideBanknoteArrowDown, Settings, User, Users, X } from 'lucide-react';
import UserDetails from './AAUserDetails';
import { authContext } from '../../customContexts/AuthContext';
import config from '../../customHooks/ConfigDetails';
import TransactionDetailsModal from './TrxDetails';
import { liveContext } from '../../customContexts/LiveContext';
import { uiContext } from '../../customContexts/UiContext';
import WithdrawalRequests from './WithdrawalRequets';

const StaffPage  = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [isSidebarOpen,setIsSidebarOpen] = useState(true);
  const {currentUser} = useContext(authContext);
  const {withdrawalRequests,} = useContext(liveContext);
  const {readNotifi} = useContext(uiContext);
  const navigate = useNavigate();

  const checkActiveNav = (navPath) => {
    let current_location = document.location.pathname ;
        // console.log('navPath: ', navPath);
        // console.log('current_location: ', current_location);
        return navPath == current_location ?  
        `bg-blue-800 text-white p-1 rounded-md hover:bg-opacity-50 border-right-0`
        // `bbd`
          :
        ''
    }

  // Mock data for transactions 
  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div
      //  className=" w-56 bg-gray-800 text-white flex flex-col px-2"
      className={`fixed  inset-y-0 left-0 z-20  w-56 bg-blue-600 text-white flex flex-col  px-2 mr-2 shadow-lg
         transform transition-transform duration-300 ease-in-out 
         ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full '} 
         md:translate-x-0 md:static  md:h-screen `}
      >
        <div className="p-2  font-semibold text-lg flex items-center justify-between ">
          AdminPanel
          <X 
          onClick={() => {setIsSidebarOpen(false)}}
          // className='rounded-lg  bg-opacity-10 text-red-100 hover:text-red-500 hidden md:block'/>
          className="md:hidden absolute right-0 text-xl mr-4 hover:bg-blue-600 p-1 rounded-md  hover:text-yellow-600 transition-colors duration-200"/>
        </div>

        <div className="flex-1 flex-col flex justify-between">
          <nav className="mt-4">
            <Link 
              to={`${"/staffusers"}`}
              className={`${checkActiveNav("/staffusers")} flex items-center px-2 py-2 text-white    hover:bg-blue-800 hover:bg-opacity-50 shadow-md hover:bg-opacity-50 shadow-md rounded-md  transition-colors cursor-pointer`}
            >
              <Gauge  strokeWidth={1.5} className='w-6 mr-2 '/>
              <span>Analysis</span>
            </Link >
            <Link
              to={'/staffusers/manageusers'}
              data-readdy="true"
              className={`${checkActiveNav("/staffusers/manageusers")} flex items-center px-2 py-2 text-white    hover:bg-blue-800 hover:bg-opacity-50 shadow-md  rounded-md transition-colors cursor-pointer`}
            >
              <Users  strokeWidth={1.5} className='w-6 mr-2 '/>
              <span>Users</span>
            </Link>
            <Link
              to={`${""}`}
              className={`${checkActiveNav("/staffusers/perm")} flex items-center px-2 py-2 text-white    hover:bg-blue-800 hover:bg-opacity-50 shadow-md  rounded-md  transition-colors cursor-pointer`}
            >
              <Lock  strokeWidth={1.5} className='w-6 mr-2 '/>
              <span>Roles & Permissions</span>
            </Link>
            <Link
              to={`${""}`}
              className={`${checkActiveNav("/staffusers/logs")}  flex items-center px-2 py-2 text-white    hover:bg-blue-800 hover:bg-opacity-50 shadow-md transition-colors cursor-pointer`}
            >
              <LineChart  strokeWidth={1.5} className='w-6 mr-2 '/>
              <span>Activity Logs</span>
            </Link>
            <Link
              to={`${"/staffusers/managetrxs"}`}
              className={`${checkActiveNav("/staffusers/managetrxs")} flex items-center p-2 py-2    hover:bg-blue-800 hover:bg-opacity-50 shadow-md  rounded-md  cursor-pointer `}
            >
              {/* <i className="fas fa-money-bill-transfer w-6"></i> */}
              <LucideBanknoteArrowDown className='w-6 mr-2 ' strokeWidth={1.5}/>
              <span>Transactions</span>
            </Link>
            <Link
              to={`${"/staffusers/settings"}`}
              className={`flex items-center px-2 py-2 text-white    hover:bg-blue-800 hover:bg-opacity-50 shadow-md  rounded-md transition-colors cursor-pointer}`}
            >
              <Settings  strokeWidth={1.5} className='w-6 mr-2 '/>
              <span>Settings</span>
            </Link>
          </nav>
          <Link to={`/hom`}className="mb-2 flex items-center px-3 py-2  rounded-lg hover:bg-blue-700 border ">
              <User strokeWidth={1.5} className="mr-2 w-4  text-white"/>
              <span className="font-semibold text-xs ">User Account</span>
            </Link>
            
        </div> 

        
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Top Header */}
        <header className=" bg-white border-b border-gray-200 flex items-center justify-between px-6 py-2">
          <button onClick={(prev) => {setIsSidebarOpen(!isSidebarOpen)}} className="text-gray-500 focus:outline-none md:hidden cursor-pointer !rounded-button whitespace-nowrap">
                  <i className="fas fa-bars text-lg"></i>
                </button>
          <div className="relative w-64">
            <input
              type="text"
              placeholder="Search..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
            <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          </div>
          <div className="flex items-center space-x-4  relative">
            <button className="relative p-2 text-gray-600 hover:text-gray-900 cursor-pointer">
              <i className="fas fa-bell text-xl"></i>
              <span className="absolute top-0 right-0 h-2 w-2 rounded-full bg-red-500"></span>
            </button>
            {currentUser?.is_staff &&  <button 
                  onClick={() => {navigate('/staffusers/with-requests')}}
                  className="relative text-gray-600 hover:text-gray-900 cursor-pointer !rounded-button whitespace-nowrap">
                    <BanknoteArrowUp className="text-gray-600 text-xl " strokeWidth={1.2}  />
                    
                    <span className="absolute -top-1  -right-1  bg-green-500 text-white w-max text-xs px-1 rounded-lg font-medium  flex items-center justify-center ">
                      {/* {readNotifi(200)} */}
                      {withdrawalRequests.filter((trx) => trx.status == 'pending').length > 0  && 
                      readNotifi(withdrawalRequests.filter((trx) => trx.status == 'pending').length)
                      }

                    </span>
                  </button>
              }
            <div className="flex items-center cursor-pointer">
              <img
                src={`${config.BASE_URL}${currentUser?.picture}`}
                alt="Profile"
                className="h-8 w-8 rounded-full object-cover border border-blue-200 border-2 p-1 "
              />
              <span className="ml-2 text-sm font-medium">@{currentUser?.username?.toUpperCase()}</span>
              <i className="fas fa-chevron-down ml-2 text-xs text-gray-500"></i>
            </div>
            <div className="absolute -bottom-1 right-0 shadow-md rounded-sm ">
              <div className="flex justify-between text-sm px-4">
                {/* <div>user account</div> */}
              </div>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <Routes>
          <Route 
              path='' 
              element={
                <Analysis/>
              } 
          />
          <Route 
              path='manageusers' 
              element={
                <AAUsers/>
              } 
          />
          <Route 
              path='with-requests' 
              element={
                <WithdrawalRequests />
              } 
          />
          <Route 
              path='user/:id' 
              element={
                <UserDetails/>
              } 
          />
          <Route 
              path='trx/:id' 
              element={
                <TransactionDetailsModal/>
              } 
          />
          <Route 
              path='managetrxs' 
              element={
                <AATrxs/>
              } 
          />
        </Routes>
        
      </div>
    </div>
  );
};

export default StaffPage;
