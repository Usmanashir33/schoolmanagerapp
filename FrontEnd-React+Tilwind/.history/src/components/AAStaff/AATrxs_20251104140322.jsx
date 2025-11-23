import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { staffContext } from "../../customContexts/StaffContext";
import { uiContext } from "../../customContexts/UiContext";
import config from "../../customHooks/ConfigDetails";

const AATrxs = () => {
  const navigate = useNavigate();
  const {formatNaira,getFormattedDate} = useContext(uiContext);
  const {sendArbitRequest,trxsData,setTrxsData} = useContext(staffContext);
  const [pageContent,setPageContent] = useState({});
  const [search,setSearch] = useState('');
  const [searchedTrx,setSearchedTrx] = useState([]); 

  const [filteredTrxs,setFilteredTrxs] = useState([]);
  
  const [isFilterOpen,setIsFilterOpen] = useState(!false);
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [transactionType, setTransactionType] = useState('');
  const [amountRange, setAmountRange] = useState({ min: '', max: '' });
  const [statusFilters, setStatusFilters] = useState({
          success: false,
          pending: false,
          failed: false
        });
  const resetFilters = () => {
          setDateRange({ start: '', end: '' });
          setTransactionType('');
          setAmountRange({ min: '', max: '' });
          setStatusFilters({
          success: false,
          pending: false,
          failed: false
          });
      };
  const applyFilters = () => {
        let filtered = pageContent?.trxs?.results || [];
        if (dateRange.start) {
            filtered = filtered.filter(trx => new Date(trx.trx_date) >= new Date(dateRange.start));
        }
        if (dateRange.end) {
            filtered = filtered.filter(trx => new Date(trx.trx_date) <= new Date(dateRange.end));
        }
        if (transactionType) {
            filtered = filtered.filter(trx => trx.transaction_type === transactionType);
        }
        if (amountRange.min) {
            filtered = filtered.filter(trx => trx.amount >= amountRange.min);
        }
        if (amountRange.max) {
            filtered = filtered.filter(trx => trx.amount <= amountRange.max);
        }
        if (statusFilters.success) {
            filtered = filtered.filter(trx => trx.status === 'success');
        }
        if (statusFilters.pending) {
            filtered = filtered.filter(trx => trx.status === 'pending');
        }
        if (statusFilters.failed) {
            filtered = filtered.filter(trx => trx.status === 'failed');
        }
        if (statusFilters.failed) {
            filtered = filtered.filter(trx => trx.status === 'cancelled');
        }
        setFilteredTrxs(filtered);
    };

      // Status badge color mapping
      const getStatusBadgeClass = (status) => {
        switch (status) {
          case "success":
            return "bg-green-100 text-green-800";
          case "approved":
            return "bg-green-100 text-green-800";
          case "pending":
            return "bg-yellow-100 text-yellow-800";
          case "failed":
            return "bg-red-100 text-red-800";
          case "cancelled":
            return "bg-red-100 text-red-800";
          default:
            return "bg-gray-100 text-gray-800";
        }
      };
    
      // Type badge color mapping
      const getTypeBadgeClass = (type) => {
        switch (type) {
          case "Deposite":
            return "bg-blue-100 text-blue-800";
          case "Transfer-In":
            return "bg-blue-100 text-blue-800";
          case "Refund":
            return "bg-blue-100 text-blue-800";

          case "Transfer-Out":
            return "bg-red-100 text-red-800";
          case "Withdraw":
            return "bg-red-100 text-red-800";
          default:
            return "bg-gray-100 text-gray-800";
        }
      };
    const getTrxs = (data) => {
        setTrxsData(data);
      };

    const getSearchedTrx = (data) => {
      setSearchedTrx(data);
    };

    useEffect(() => {
      setSearchedTrx([]);
      if (search.length >= 5){
        let waiting = 500 ;// seconds
        setTimeout(() => {
          const url = "/account/search-trx/";
          sendArbitRequest(url, "POST", {search}, getSearchedTrx)
        }, waiting );
      }
    },[search]);

    useEffect(() => {
        if (trxsData){
          setPageContent(trxsData);
          setFilteredTrxs(trxsData?.trxs?.results || []);
        }
      },[trxsData])
    
      useEffect(() => {
        if (!trxsData?.trxs?.results?.length){
          let url = `/staff/trxs/` ;
          sendArbitRequest(url,"GET",null,getTrxs,true,) ;
        }
      },[])
    return ( 
        <main className="flex-1 overflow-y-auto p-2 overflow-hidden hide-scrollbar">
          {/* Stats Cards */}
          <div className="grid grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-3">
              <div className="flex justify-between items-center mb-2">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <i className="fas fa-exchange-alt text-blue-500"></i>
                </div>
                <span className="text-green-500 text-sm font-medium">+15%</span>
              </div>
              <div className="text-gray-500 text-sm">Recent Transactions</div>
              <div className="text-xl font-bold mt-1">{pageContent?.recent_trx}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-3">
              <div className="flex justify-between items-center mb-2">
                <div className="bg-green-100 p-3 rounded-lg">
                  <i className="fas fa-arrow-trend-up text-green-500"></i>
                </div>
                <span className="text-green-500 text-sm font-medium">+12%</span>
              </div>
              <div className="text-gray-500 text-sm">Total Credits</div>
              <div className="text-xl font-bold mt-1">{formatNaira(pageContent?.recent_credit_sum)}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-3">
              <div className="flex justify-between items-center mb-2">
                <div className="bg-purple-100 p-3 rounded-lg">
                  <i className="fas fa-arrow-trend-down text-purple-500"></i>
                </div>
                <span className="text-red-500 text-sm font-medium">+8%</span>
              </div>
              <div className="text-gray-500 text-sm">Total Expenses</div>
              <div className="text-xl font-bold mt-1">{formatNaira(pageContent?.recent_debit_sum)}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-3">
              <div className="flex justify-between items-center mb-2">
                <div className="bg-yellow-100 p-3 rounded-lg">
                  <i className="fas fa-clock text-yellow-500"></i>
                </div>
                <span className="text-red-500 text-sm font-medium">-5%</span>
              </div>
              <div className="text-gray-500 text-sm">Pending Transactions</div>
              <div className="text-xl font-bold mt-1">237</div>
            </div>
          </div>

          {/* Transaction Management Section */}
          <div className="bg-white rounded-lg shadow mb-8">
            <div className="flex justify-between items-center p-4 border-b border-gray-200">
              <h2 className="text-lg font-medium">Transaction Management</h2>
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-2 py-2 rounded-lg flex items-center space-x-2 cursor-pointer !rounded-button whitespace-nowrap">
                <i className="fas fa-plus text-sm"></i>
                <span>Add New Transaction</span>
              </button>
            </div>

            <div className="p-4">
              <div className="flex justify-between items-center mb-6">
                <div className="relative w-64">
                  <input

                    type="search"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search transactions..."
                    className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  />
                  <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
                </div>
                <div className="flex space-x-3 relative ">
                  <div className="relative">
                    <button className="flex items-center space-x-2 px-2 py-2 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50 cursor-pointer !rounded-button whitespace-nowrap">
                      <i className="fas fa-filter text-sm"></i>
                      <span onClick={() => setIsFilterOpen(!isFilterOpen)}  className="text-xs">{transactionType? transactionType :'All Types'}</span>
                      <i className="fas fa-chevron-down ml-2 text-xs"></i>
                    </button>
                  </div>
                  <button className="flex items-center space-x-2 px-2 py-2 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50 cursor-pointer !rounded-button whitespace-nowrap">
                    <i className="fas fa-download text-sm"></i>
                    <span className="text-xs" >Export</span>
                  </button>
                  

                  {isFilterOpen && (
                        <div className="absolute right-10 top-10 mt-2 w-72 bg-white rounded-lg shadow-lg z-50 border overflow-y-auto max-h-96">
                          <div className="p-4">
                            <div className="flex justify-between items-center ">
                                <h4 className="text-sm font-medium text-gray-900 mb-3">Filter Transactions</h4>
                                <i onClick={() => setIsFilterOpen(!isFilterOpen)}  className=" fas fa-times hover:bg-gray-200 p-1 hover:p-1 rounded-md text-red-900"></i>
                            </div>
                            
                            {/* Date Range */}
                            <div className="mb-4">
                              <label className="block text-xs font-medium text-gray-700 mb-1">Date Range</label>
                              <div className="grid grid-cols-2 gap-2">
                                <div>
                                  <label className="block text-xs text-gray-500 mb-1">From</label>
                                  <input 
                                    type="date" 
                                    className="w-full text-xs border rounded p-2"
                                    value={dateRange.start}
                                    onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
                                  />
                                </div>
                                <div>
                                  <label className="block text-xs text-gray-500 mb-1">To</label>
                                  <input 
                                    type="date" 
                                    className="w-full text-xs border rounded p-2"
                                    value={dateRange.end}
                                    onChange={(e) => setDateRange({...dateRange, end: e.target.value})}
                                  />
                                </div>
                              </div>
                            </div>
                            
                            {/* Transaction Type */}
                            <div className="mb-4">
                              <label className="block text-xs font-medium text-gray-700 mb-1">Transaction Type</label>
                              <div className="relative">
                                <select 
                                  className="w-full text-xs border rounded p-2 pr-8 appearance-none bg-white"
                                  value={transactionType}
                                  onChange={(e) => setTransactionType(e.target.value)}
                                >
                                  <option value="">All Types</option>
                                  <option value="Deposit">Deposit</option>
                                  <option value="Withdraw">Withdrawal</option>
                                  <option value="Transfer-In">Transfer In</option>
                                  <option value="Transfer-Out">Payment</option>
                                  <option value="Refund">Refund</option>
                                  <option value="purchase">Purchase</option>
                                </select>
                                <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
                                  <i className="fas fa-chevron-down text-gray-400 text-xs"></i>
                                </div>
                              </div>
                            </div>
                            
                            {/* Action Buttons */}
                            <div className="flex justify-between pt-2 border-t">
                              <button 
                                onClick={() => {resetFilters(),setIsFilterOpen(false)}}
                                className="px-3 py-1.5 text-xs text-gray-600 border rounded hover:bg-gray-50 !rounded-button whitespace-nowrap"
                              >
                                Reset
                              </button>
                              <button 
                                onClick={() => {applyFilters(),setIsFilterOpen(false)}}
                                className="px-3 py-1.5 text-xs text-white bg-blue-600 rounded hover:bg-blue-700 !rounded-button whitespace-nowrap"
                              >
                                Apply
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                </div>
              </div>

              {/* Transactions Table */}
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="text-left text-gray-500 text-sm border-b border-gray-200">
                      <th className="px-2 py-2 font-medium w-10">
                        <input
                          type="checkbox"
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                      </th>
                      <th className="px-2 py-2 font-medium">Transaction ID</th>
                      <th className="px-2 py-2 font-medium">User</th>
                      <th className="px-2 py-2 font-medium">Amount</th>
                      <th className="px-2 py-2 font-medium">Type</th>
                      <th className="px-2 py-2 font-medium">Status</th>
                      <th className="px-2 py-2 font-medium">Date</th>
                      {/* <th className="px-2 py-2 font-medium">Actions</th> */}
                    </tr>
                  </thead>
                  <tbody>
                    {(search? searchedTrx : filteredTrxs)?.map((transaction) => (
                      <tr
                        key={transaction.id}
                        className="border-b border-gray-200 hover:bg-gray-50 "
                        onClick={() => {navigate(`/staffusers/trx/${transaction.id}`)}}
                      >
                        <td className="px-2 py-2">
                          <input
                            type="checkbox"
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                        </td>
                        <td className="px-2 py-2 font-medium text-blue-600">
                          {transaction?.id?.slice(0,8)}...
                        </td>
                        <td className="px-2 py-2">
                          <div className="flex items-center">
                            <img
                              src={`${config.BASE_URL}${transaction.user.picture}`}
                              alt={transaction.user.username}
                              className="h-8 w-8 rounded-full object-cover mr-3"
                            />
                            <span className="font-medium">
                              @{transaction.user.username}
                            </span>
                          </div>
                        </td>
                        <td className="px-2 py-2 font-medium">
                          {formatNaira(transaction?.amount)}
                        </td>
                        <td className="px-2 py-2">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-medium ${getTypeBadgeClass(transaction?.transaction_type)}`}
                          >
                            {transaction?.transaction_type}
                          </span>
                        </td>
                        <td className="px-2 py-2">
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadgeClass(transaction.status)}`}
                          >
                            {transaction.status}
                          </span>
                        </td>
                        <td className="px-2 py-2 text-gray-600 text-normal text-sm  ">
                          {getFormattedDate(transaction?.trx_date)}
                        </td>
                        
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="flex justify-between items-center mt-6 text-sm">
                <div className="text-gray-500">
                  Showing 1 to 5 of 120 entries
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
}
 
export default AATrxs;