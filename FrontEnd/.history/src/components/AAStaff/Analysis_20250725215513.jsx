import React, { useState, useEffect } from "react";
import * as echarts from "echarts";
const Analysis = () => {
  const [selectedPeriod, setSelectedPeriod] = useState("Daily");
  const [selectedFilter, setSelectedFilter] = useState("All");
  const [selectedTimeRange, setSelectedTimeRange] = useState("Month");

  const getTransactionStats = (period) => {
    const data = transactionData[period];
    return {
      inflow: {
        total: data.airtime.reduce((a, b) => a + b, 0),
        change: period === "Weekly" ? "+18.2%" : "+15.4%",
      },
      outflow: {
        total: data.withdrawals.reduce((a, b) => a + b, 0),
        change: period === "Weekly" ? "-12.4%" : "-10.2%",
      },
      transactions: {
        total: data.airtime.length,
        change: period === "Weekly" ? "+24" : "+18",
      },
      average: {
        total: Math.round(
          data.airtime.reduce((a, b) => a + b, 0) / data.airtime.length,
        ),
        change: period === "Weekly" ? "+5.8%" : "+4.2%",
      },
    };
  };

  const transactionData = {
    Daily: {
      labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
      airtime: [800, 1200, 900, 1500, 1100, 800, 1400],
      data: [500, 700, 600, 1000, 800, 600, 800],
      withdrawals: [600, 800, 800, 1200, 700, 800, 900],
      deposits: [400, 500, 500, 800, 500, 500, 500],
    },
    Weekly: {
      labels: ["Week 1", "Week 2", "Week 3", "Week 4"],
      airtime: [3200, 3800, 3500, 4200],
      data: [2100, 2400, 2300, 2800],
      withdrawals: [2800, 3200, 3000, 3600],
      deposits: [1800, 2200, 2000, 2400],
    },
    Monthly: {
      labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
      airtime: [12000, 14000, 13000, 15000, 14500, 15500],
      data: [8000, 9000, 8500, 9500, 9200, 9800],
      withdrawals: [10000, 11000, 10500, 12000, 11500, 12500],
      deposits: [7000, 8000, 7500, 8500, 8200, 8800],
    },
  };
  useEffect(() => {
    const chartDom = document.getElementById("transactionChart");
    if (!chartDom) return;
    const myChart = echarts.init(chartDom);
    const currentData = transactionData[selectedPeriod];
    const option = {
      animation: false,
      tooltip: {
        trigger: "item",
        formatter: "{b}: {c} ({d}%)",
      },
      legend: {
        orient: "vertical",
        right: "5%",
        top: "center",
        textStyle: {
          color: "#6B7280",
        },
      },
      series: [
        {
          name: "Transaction Distribution",
          type: "pie",
          radius: ["60%", "80%"],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: "#fff",
            borderWidth: 2,
          },
          label: {
            show: false,
          },
          emphasis: {
            label: {
              show: true,
              fontSize: "14",
              fontWeight: "bold",
            },
          },
          labelLine: {
            show: false,
          },
          data: [
            { value: 35, name: "Airtime", itemStyle: { color: "#3B82F6" } },
            { value: 25, name: "Data", itemStyle: { color: "#10B981" } },
            { value: 20, name: "Withdrawals", itemStyle: { color: "#F59E0B" } },
            { value: 20, name: "Deposits", itemStyle: { color: "#EC4899" } },
          ],
        },
      ],
    };
    myChart.setOption(option);
    return () => {
      myChart.dispose();
    };
  }, [selectedPeriod]);
  const performanceData = [
    { date: "Jan", value: 3000 },
    { date: "Feb", value: 3800 },
    { date: "Mar", value: 3200 },
    { date: "Apr", value: 4200 },
    { date: "May", value: 4800 },
    { date: "Jun", value: 4500 },
  ];
  const transactions = [
    {
      date: "2024-01-15",
      type: "Airtime Purchase",
      amount: "-$50.00",
      status: "Completed",
      carrier: "AT&T",
    },
    {
      date: "2024-01-14",
      type: "Data Bundle",
      amount: "-$25.00",
      status: "Completed",
      carrier: "Verizon",
    },
    {
      date: "2024-01-13",
      type: "Bank Withdrawal",
      amount: "-$200.00",
      status: "Pending",
    },
    {
      date: "2024-01-12",
      type: "Wallet Deposit",
      amount: "+$500.00",
      status: "Completed",
    },
    {
      date: "2024-01-11",
      type: "Airtime Purchase",
      amount: "-$100.00",
      status: "Failed",
      carrier: "T-Mobile",
    },
  ];
  return (
    <div className=" bg-gray-50 p-4 md:p-6 w-full max-w-[1440px] mx-auto overflow-auto hide-scrollbar">
      
      
      {/* Header Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6 mb-8">
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Transaction Analysis
            </h3>
            <div className="flex gap-2">
              {["Daily", "Weekly", "Monthly"].map((period) => {
                const stats = getTransactionStats(selectedPeriod);
                return (
                  <button
                    key={period}
                    onClick={() => {
                      setSelectedPeriod(period);
                      const stats = getTransactionStats(period);

                      // Update the stats display
                      const inflowElement =
                        document.getElementById("inflow-value");
                      const outflowElement =
                        document.getElementById("outflow-value");
                      const transactionsElement =
                        document.getElementById("transactions-value");
                      const averageElement =
                        document.getElementById("average-value");

                      if (inflowElement)
                        inflowElement.textContent = `$${stats.inflow.total.toLocaleString()}`;
                      if (outflowElement)
                        outflowElement.textContent = `$${stats.outflow.total.toLocaleString()}`;
                      if (transactionsElement)
                        transactionsElement.textContent =
                          stats.transactions.total;
                      if (averageElement)
                        averageElement.textContent = `$${stats.average.total.toLocaleString()}`;
                    }}
                    className={`px-3 py-1 text-sm rounded-md cursor-pointer whitespace-nowrap !rounded-button ${
                      selectedPeriod === period
                        ? "bg-blue-100 text-blue-600"
                        : "text-gray-600 hover:bg-gray-100"
                    }`}
                  >
                    {period}
                  </button>
                );
              })}
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <i className="fas fa-arrow-up text-blue-600"></i>
                </div>
                <span
                  className="text-green-500 text-sm font-medium"
                  id="inflow-change"
                >
                  +18.2%
                </span>
              </div>
              <p className="text-gray-600 text-sm">Inflow</p>
              <p className="text-xl font-bold text-gray-900" id="inflow-value">
                $12,845.00
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                  <i className="fas fa-arrow-down text-red-600"></i>
                </div>
                <span
                  className="text-red-500 text-sm font-medium"
                  id="outflow-change"
                >
                  -12.4%
                </span>
              </div>
              <p className="text-gray-600 text-sm">Outflow</p>
              <p className="text-xl font-bold text-gray-900" id="outflow-value">
                $8,234.00
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                  <i className="fas fa-exchange-alt text-green-600"></i>
                </div>
                <span
                  className="text-blue-500 text-sm font-medium"
                  id="transactions-change"
                >
                  +24
                </span>
              </div>
              <p className="text-gray-600 text-sm">Total Transactions</p>
              <p
                className="text-xl font-bold text-gray-900"
                id="transactions-value"
              >
                156
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                  <i className="fas fa-chart-pie text-purple-600"></i>
                </div>
                <span
                  className="text-green-500 text-sm font-medium"
                  id="average-change"
                >
                  +5.8%
                </span>
              </div>
              <p className="text-gray-600 text-sm">Average Value</p>
              <p className="text-xl font-bold text-gray-900" id="average-value">
                $1,245.00
              </p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Transaction Distribution
            </h3>
            <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
              <i className="fas fa-chart-bar text-gray-600"></i>
            </div>
          </div>
          <div id="transactionChart" className="h-[200px] w-full"></div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6 mb-8">
        {/* Portfolio Performance Chart */}
        <div className="col-span-2 bg-white rounded-lg p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">
              Portfolio Performance
            </h3>
            <div className="flex flex-wrap gap-2">
              {["Day", "Week", "Month", "Year"].map((period) => (
                <button
                  key={period}
                  onClick={() => setSelectedPeriod(period)}
                  className={`px-3 py-1 text-sm rounded-md cursor-pointer whitespace-nowrap !rounded-button ${
                    selectedPeriod === period
                      ? "bg-blue-100 text-blue-600"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  {period}
                </button>
              ))}
            </div>
          </div>
          {/* Chart Area */}
          <div className="h-64 relative">
            <svg width="100%" height="100%" viewBox="0 0 600 200">
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop
                    offset="0%"
                    style={{ stopColor: "#3B82F6", stopOpacity: 0.3 }}
                  />
                  <stop
                    offset="100%"
                    style={{ stopColor: "#3B82F6", stopOpacity: 0 }}
                  />
                </linearGradient>
              </defs>
              <path
                d="M 50 150 Q 150 120 200 130 T 350 100 T 500 80 T 550 70"
                stroke="#3B82F6"
                strokeWidth="3"
                fill="none"
              />
              <path
                d="M 50 150 Q 150 120 200 130 T 350 100 T 500 80 T 550 70 L 550 200 L 50 200 Z"
                fill="url(#gradient)"
              />
              {performanceData.map((point, index) => (
                <circle
                  key={index}
                  cx={50 + index * 100}
                  cy={150 - (point.value - 3000) / 20}
                  r="4"
                  fill="#3B82F6"
                />
              ))}
            </svg>
            <div className="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-gray-500 px-12">
              {performanceData.map((point) => (
                <span key={point.date}>{point.date}</span>
              ))}
            </div>
          </div>
        </div>
        {/* Asset Allocation */}
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">
            Asset Allocation
          </h3>
          <div className="flex justify-center mb-6">
            <div className="relative w-32 h-32">
              <svg width="128" height="128" viewBox="0 0 128 128">
                <circle
                  cx="64"
                  cy="64"
                  r="50"
                  fill="none"
                  stroke="#E5E7EB"
                  strokeWidth="12"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="50"
                  fill="none"
                  stroke="#3B82F6"
                  strokeWidth="12"
                  strokeDasharray="125.6"
                  strokeDashoffset="25.12"
                  transform="rotate(-90 64 64)"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="50"
                  fill="none"
                  stroke="#10B981"
                  strokeWidth="12"
                  strokeDasharray="31.4"
                  strokeDashoffset="0"
                  transform="rotate(72 64 64)"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="50"
                  fill="none"
                  stroke="#F59E0B"
                  strokeWidth="12"
                  strokeDasharray="31.4"
                  strokeDashoffset="0"
                  transform="rotate(144 64 64)"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="50"
                  fill="none"
                  stroke="#6B7280"
                  strokeWidth="12"
                  strokeDasharray="18.84"
                  strokeDashoffset="0"
                  transform="rotate(216 64 64)"
                />
              </svg>
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                <span className="text-sm text-gray-600">Stocks</span>
              </div>
              <span className="text-sm font-medium">40%</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                <span className="text-sm text-gray-600">Crypto</span>
              </div>
              <span className="text-sm font-medium">25%</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
                <span className="text-sm text-gray-600">Bonds</span>
              </div>
              <span className="text-sm font-medium">20%</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-gray-500 rounded-full mr-2"></div>
                <span className="text-sm text-gray-600">Cash</span>
              </div>
              <span className="text-sm font-medium">15%</span>
            </div>
          </div>
        </div>
      </div>
      {/* Enhanced Analysis Features */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 mb-8">
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
              <i className="fas fa-chart-line text-blue-600"></i>
            </div>
            <h4 className="font-semibold text-gray-900">ROI Performance</h4>
          </div>
          <p className="text-2xl font-bold text-green-600">12.4%</p>
          <p className="text-sm text-gray-500">Growth</p>
        </div>
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
              <i className="fas fa-shield-alt text-green-600"></i>
            </div>
            <h4 className="font-semibold text-gray-900">Risk Assessment</h4>
          </div>
          <p className="text-2xl font-bold text-green-600">Low</p>
          <p className="text-sm text-gray-500">Stable</p>
        </div>
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center mr-3">
              <i className="fas fa-trending-up text-orange-600"></i>
            </div>
            <h4 className="font-semibold text-gray-900">Market Analysis</h4>
          </div>
          <p className="text-2xl font-bold text-orange-600">Bullish</p>
          <p className="text-sm text-gray-500">Strong</p>
        </div>
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center mr-3">
              <i className="fas fa-balance-scale text-gray-600"></i>
            </div>
            <h4 className="font-semibold text-gray-900">
              Investment Distribution
            </h4>
          </div>
          <p className="text-2xl font-bold text-gray-900">Balanced</p>
          <p className="text-sm text-gray-500">Optimal</p>
        </div>
      </div>
      {/* Advanced Analysis Tools */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6 mb-8">
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Quick Actions
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <button className="flex items-center justify-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors !rounded-button">
              <div className="text-center">
                <i className="fas fa-mobile-alt text-blue-600 text-2xl mb-2"></i>
                <p className="text-sm text-gray-900">Buy Airtime</p>
              </div>
            </button>
            <button className="flex items-center justify-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors !rounded-button">
              <div className="text-center">
                <i className="fas fa-wifi text-green-600 text-2xl mb-2"></i>
                <p className="text-sm text-gray-900">Buy Data</p>
              </div>
            </button>
            <button className="flex items-center justify-center p-4 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors !rounded-button">
              <div className="text-center">
                <i className="fas fa-wallet text-yellow-600 text-2xl mb-2"></i>
                <p className="text-sm text-gray-900">Withdraw</p>
              </div>
            </button>
            <button className="flex items-center justify-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors !rounded-button">
              <div className="text-center">
                <i className="fas fa-piggy-bank text-purple-600 text-2xl mb-2"></i>
                <p className="text-sm text-gray-900">Deposit</p>
              </div>
            </button>
          </div>
        </div>
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Usage Statistics
          </h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-600">Airtime Balance</span>
                <span className="text-sm font-medium">$35.50</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: "65%" }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-600">Data Usage</span>
                <span className="text-sm font-medium">4.2GB/5GB</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full"
                  style={{ width: "84%" }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-600">Wallet Balance</span>
                <span className="text-sm font-medium">$250.00</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-purple-600 h-2 rounded-full"
                  style={{ width: "100%" }}
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* Recent Transactions */}
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            Recent Transactions
          </h3>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedFilter("All")}
              className={`px-4 py-2 text-sm rounded-md cursor-pointer whitespace-nowrap !rounded-button ${
                selectedFilter === "All"
                  ? "bg-blue-100 text-blue-600"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              All
            </button>
            <button
              onClick={() => setSelectedFilter("Airtime")}
              className={`px-4 py-2 text-sm rounded-md cursor-pointer whitespace-nowrap !rounded-button ${
                selectedFilter === "Airtime"
                  ? "bg-blue-100 text-blue-600"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              Airtime
            </button>
            <button
              onClick={() => setSelectedFilter("Data")}
              className={`px-4 py-2 text-sm rounded-md cursor-pointer whitespace-nowrap !rounded-button ${
                selectedFilter === "Data"
                  ? "bg-blue-100 text-blue-600"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              Data
            </button>
            <button
              onClick={() => setSelectedFilter("Transfers")}
              className={`px-4 py-2 text-sm rounded-md cursor-pointer whitespace-nowrap !rounded-button ${
                selectedFilter === "Transfers"
                  ? "bg-blue-100 text-blue-600"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              Transfers
            </button>
          </div>
        </div>
        <div className="overflow-x-auto -mx-6">
          <table className="w-full min-w-[800px]">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">
                  Date
                </th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">
                  Transaction
                </th>
                <th className="text-right py-3 px-4 text-sm font-medium text-gray-600">
                  Amount
                </th>
                <th className="text-center py-3 px-4 text-sm font-medium text-gray-600">
                  Status
                </th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((transaction, index) => (
                <tr key={index} className="border-b border-gray-100">
                  <td className="py-4 px-4 text-sm text-gray-900">
                    {transaction.date}
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center mr-3">
                        <i
                          className={`fas ${
                            transaction.type.includes("Stock")
                              ? "fa-chart-line"
                              : transaction.type.includes("Crypto")
                                ? "fa-bitcoin"
                                : transaction.type.includes("Dividend")
                                  ? "fa-coins"
                                  : "fa-exchange-alt"
                          } text-gray-600 text-xs`}
                        ></i>
                      </div>
                      <span className="text-sm text-gray-900">
                        {transaction.type}
                      </span>
                    </div>
                  </td>
                  <td
                    className={`py-4 px-4 text-sm text-right font-medium ${
                      transaction.amount.startsWith("+")
                        ? "text-green-600"
                        : "text-red-600"
                    }`}
                  >
                    {transaction.amount}
                  </td>
                  <td className="py-4 px-4 text-center">
                    <span
                      className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                        transaction.status === "Completed"
                          ? "bg-green-100 text-green-800"
                          : transaction.status === "Pending"
                            ? "bg-yellow-100 text-yellow-800"
                            : "bg-red-100 text-red-800"
                      }`}
                    >
                      {transaction.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
export default Analysis;
