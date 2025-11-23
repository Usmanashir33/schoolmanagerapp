// The exported code uses Tailwind CSS. Install Tailwind CSS in your dev environment to ensure all styles work.
import React, { useContext, useEffect, useState } from "react";
import { staffContext } from "../../customContexts/StaffContext";

import { uiContext } from "../../customContexts/UiContext";
import config from "../../customHooks/ConfigDetails";
import { useNavigate, useParams } from "react-router";

const AAUsers= () => {
  const navigate = useNavigate();
  const [currentPage, setCurrentPage] = useState(1);

  const {formatNaira,getFormattedDate} = useContext(uiContext);
  const {usersData,setUsersData,sendArbitRequest} = useContext(staffContext);
  const [search,setSearch] = useState('');
  const [searchedUsers,setSearchedUsers] = useState([]);
  const [pageContent,setPageContent] = useState({});
  const [filterdUsers,setFilteredUsers] = useState([]);

  const [isFilterOpen,setIsFilterOpen] = useState(false);

  const {
      active_users:activeUsers,
      inactive_users:inActiveUsers,
      new_users:newUsers,
      total_users:totalUsers,
      users:Users,
  } = pageContent;
  const {next:nextPage,previous:previousPage,results:usersdata}=(Users || {});
  
  
  const toggleIsFilterOpen = () => {setIsFilterOpen(!isFilterOpen)};
  const [userType,setUserType] = useState('')
  const resetFilters = () => {
        setUserType('')
    };
 
  // Status badge color mapping
  const getStatusBadgeClass = (status) => {
    switch (status) {
      case true:
        return "bg-green-100 text-green-800";
      case 'pending':
        return "bg-yellow-100 text-yellow-800";
      case false:
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };
  const getUsers = (data) => {
    setUsersData(data);
  }

  //set filtered user 
  useEffect(() => {
    switch (userType) {
      case "Staffs":
        setFilteredUsers(usersdata?.filter((user) => user?.is_staff == true))
        break;

      case "Users":
        setFilteredUsers(usersdata?.filter((user) => user?.is_staff != true))
        break;

      case "Active Users":
        setFilteredUsers(usersdata?.filter((user) => user?.is_active == true))
        break;

      case "Inactive Users":
        setFilteredUsers(usersdata?.filter((user) => user?.is_active != true))
        break;

      default:
        setFilteredUsers(usersdata)
        break;
    };
    setIsFilterOpen(false);
  },[userType,usersdata])
  
  useEffect(() => {
    if (usersData){
      setPageContent(usersData);
    }
  },[usersData])

  const getSearchedUser = (data) => {
    setSearchedUsers([data]);
  }

  useEffect(() => {
      setSearchedUsers([]);
      if (search.length >= 5){
        let waiting = 500 ;// seconds
        setTimeout(() => {
          const url = "/authuser/search-user/" ;
          sendArbitRequest(url, "POST", {search}, getSearchedUser )
        }, waiting );
      }
    },[search])

  useEffect(() => {
    if (!usersData?.users?.results?.length){
      let url = `/staff/users/` ;
      sendArbitRequest(url,"GET",null,getUsers,true,) ;
    }
  },[]);

  return (
    <main className="flex-1 overflow-y-auto p-2 hide-scrollbar">
          {/* Stats Cards */}
          <div className="grid grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-3">
              <div className="flex justify-between items-center mb-2">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <i className="fas fa-users text-blue-500"></i>
                </div>
                <span className="text-green-500 text-sm font-medium">+12%</span>
              </div>
              <div className="text-gray-500 text-sm">Total Users</div>
              <div className="text-2xl font-bold mt-1">{totalUsers}</div>
            </div>
            

            <div className="bg-white rounded-lg shadow p-3">
              <div className="flex justify-between items-center mb-2">
                <div className="bg-yellow-100 p-3 rounded-lg">
                  <i className="fas fa-user-clock text-yellow-500"></i>
                </div>
                <span className="text-green-500 text-sm font-medium">+4%</span>
              </div>
              <div className="text-gray-500 text-sm">New Users</div>
              <div className="text-2xl font-bold mt-1">{newUsers}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-3">
              <div className="flex justify-between items-center mb-2">
                <div className="bg-green-100 p-3 rounded-lg">
                  <i className="fas fa-user-check text-green-500"></i>
                </div>
                <span className="text-green-500 text-sm font-medium">+8%</span>
              </div>
              <div className="text-gray-500 text-sm">Active Users</div>
              <div className="text-2xl font-bold mt-1">{activeUsers}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-3">
              <div className="flex justify-between items-center mb-2">
                <div className="bg-red-100 p-3 rounded-lg">
                  <i className="fas fa-user-times text-red-500"></i>
                </div>
                <span className="text-red-500 text-sm font-medium">-2%</span>
              </div>
              <div className="text-gray-500 text-sm">In-Active Users</div>
              <div className="text-2xl font-bold mt-1">{inActiveUsers}</div>
            </div>
          </div>

          {/* User Management Section */}
          <div className="bg-white rounded-lg shadow mb-8">
            <div className="flex justify-between items-center p-3 border-b border-gray-200">
              <h2 className="text-lg font-medium">User Management</h2>
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-2 py-2 rounded-lg flex items-center space-x-2 cursor-pointer !rounded-button whitespace-nowrap">
                <i className="fas fa-plus text-sm"></i>
                <span>Add New User</span>
              </button>
            </div>
            <div className="p-3">
              <div className="flex justify-between items-center mb-6">
                <div className="relative w-64">
                  <input
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    type="search"
                    placeholder="Search users..."
                    className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  />
                  <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
                </div>
                <div className="flex space-x-3 relative ">
                  {(userType) <span className="flex p-1 font-medium text-gray-900 items-center">
                    {filterdUsers.length}
                  </span>}
                  <button onClick={toggleIsFilterOpen}  className="flex items-center space-x-2 px-2 py-2 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50 cursor-pointer !rounded-button whitespace-nowrap">
                    <i className="fas fa-filter text-sm"></i>
                    <span> {userType?userType:'Filters'} </span>
                  </button>
                  <button className="flex items-center space-x-2 px-2 py-2 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50 cursor-pointer !rounded-button whitespace-nowrap">
                    <i className="fas fa-download text-sm"></i>
                    <span>Export</span>
                  </button>

                  {isFilterOpen && (
                        <div className="absolute -top-5 right-10 mt-2 w-72 bg-white rounded-lg shadow-lg z-50 border overflow-y-auto max-h-96">
                          <div className="p-4">
                            <div className="flex justify-between items-center ">
                                <h4 className="text-sm font-medium text-gray-900 mb-3">Filter Users</h4>
                                <i onClick={toggleIsFilterOpen}  className=" fas fa-times hover:bg-gray-200 p-1 hover:p-1 rounded-md text-red-900"></i>
                            </div>
                            
                            {/* Transaction Type */}
                            <div className="mb-4">
                              <label className="block text-xs font-medium text-gray-700 mb-1">User Type</label>
                              <div className="relative">
                                <select 
                                  className="w-full text-xs border rounded p-2 pr-8 appearance-none bg-white"
                                  value={userType}
                                  onChange={(e) => setUserType(e.target.value)}
                                >
                                  <option value="All Types">All Types</option>
                                  <option value="Staffs">Staffs</option>
                                  <option value="Users">Users</option>
                                  <option value="Active Users">Active Users</option>
                                  <option value="Inactive Users">Inactive Users</option>
                                </select>
                                <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                                  <i className="fas fa-chevron-down text-gray-400 text-xs"></i>
                                </div>
                              </div>
                            </div>
                            
                            {/* Action Buttons */}
                            <div className="flex justify-between pt-2 border-t">
                              <button 
                                onClick={ () => {toggleIsFilterOpen(); resetFilters()}}
                                className="px-3 py-1.5 text-xs text-gray-600 border rounded hover:bg-gray-50 !rounded-button whitespace-nowrap">
                                Reset
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                  
                </div>
              </div>
              
              {/* Users Table */}
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="text-left text-gray-500 text-sm border-b border-gray-200">
                      <th className="px-2 py-3 font-medium w-10">
                        <input
                          type="checkbox"
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                      </th>
                      <th className="px-2 py-3 font-medium ">User</th>
                      <th className="px-2 py-3 font-medium">Email</th>
                      <th className="px-2 py-3 font-medium">Balance</th>
                      <th className="px-2 py-3 font-medium">Role</th>
                      <th className="px-2 py-3 font-medium text-center">Trxs</th>
                      <th className="px-2 py-3 font-medium">Status</th>
                      <th className="px-2 py-3 font-medium">Created</th>
                      <th className="px-2 py-3 font-medium">Actions</th>
                    </tr>
                  </thead> 
                  <tbody>
                    {(search? searchedUsers : filterdUsers )?.map((user) => (
                      <>
                      <tr
                        onClick={() => {navigate(`/staffusers/user/${user.id}`)}}
                        key={user.id}
                        className="border-b border-gray-200 hover:bg-gray-50"
                      >
                        <td className="px-2 py-2">
                          <input
                            type="checkbox"
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                        </td>
                        <td className="px-2 py-2 overflow-x-hidden ">
                          <div className="flex items-center">
                            <img
                              src={`${config.BASE_URL}${user?.picture}`}
                              alt={user.username}
                              className="h-10 w-10 rounded-full object-cover mr-3 border border-3 border-gray-200"
                            />
                            <span className="font-medium">@{user.username}</span>
                          </div>
                        </td>
                        <td className="px-2 py-2 text-gray-600">
                          {`${user.email?.slice(0,5)}....${user.email?.slice(-10)}`}
                        </td>
                        <td className="px-2 py-2 font-medium">{formatNaira(user?.account?.account_balance)}</td>
                        <td className="px-2 py-2">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadgeClass(user?.is_staff?true:'user')}`}
                          >
                            {user?.is_staff? "Staff":"user"}
                          </span>
                        </td>
                        <td className="px-2 py-2 text-center">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-medium   ${getStatusBadgeClass(user?.can_transect)}`}
                          >
                            {user?.can_transect? "Normal":"Suspended"}
                          </span>
                        </td>
                        <td className="px-2 py-2">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadgeClass(user?.is_active)}`}
                          >
                            {user?.is_active? "Active":"inactive"}
                          </span>
                        </td>
                        <td className="px-2 py-2 text-gray-600 text-xs  w-20">
                          {getFormattedDate(user.date_joined)}
                        </td>
                        <td className="px-2 py-2">
                          <div className="flex space-x-3 text-gray-600">
                            <button className="cursor-pointer hover:text-blue-600">
                              <i className="fas fa-eye"></i>
                            </button>
                            <button className="cursor-pointer hover:text-blue-600">
                              <i className="fas fa-edit"></i>
                            </button>
                            <button className="cursor-pointer hover:text-red-600">
                              <i className="fas fa-trash"></i>
                            </button>
                          </div>
                        </td>
                      </tr>
                      </>
                    ))}
                  </tbody>
                    {(search && !Object.keys(searchedUsers)?.length) && <tr className=" w-full   text-gray-500 text-md">
                      No record
                    </tr> }
                </table>
              </div>

              {/* Pagination */}
              <div className="flex justify-between items-center mt-6 text-sm">
                <div className="text-gray-500">
                  Showing 1 to 5 of 100 entries
                </div>
                <div className="flex space-x-1">
                  <button className="px-3 py-1 border border-gray-300 rounded text-gray-600 hover:bg-gray-50 cursor-pointer !rounded-button whitespace-nowrap">
                    Previous
                  </button>
                  <button className="px-3 py-1 bg-blue-600 text-white rounded border border-blue-600 cursor-pointer !rounded-button whitespace-nowrap">
                    1
                  </button>
                  <button className="px-3 py-1 border border-gray-300 rounded text-gray-600 hover:bg-gray-50 cursor-pointer !rounded-button whitespace-nowrap">
                    2
                  </button>
                  <button className="px-3 py-1 border border-gray-300 rounded text-gray-600 hover:bg-gray-50 cursor-pointer !rounded-button whitespace-nowrap">
                    3
                  </button>
                  <button className="px-3 py-1 border border-gray-300 rounded text-gray-600 hover:bg-gray-50 cursor-pointer !rounded-button whitespace-nowrap">
                    Next
                  </button>
                </div>
              </div>
            </div>
          </div>
        </main>
  );
};
export default AAUsers;
