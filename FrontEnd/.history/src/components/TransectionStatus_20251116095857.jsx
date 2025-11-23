// The exported code uses Tailwind CSS. Install Tailwind CSS in your dev environment to ensure all styles work.
import React, { useState, useEffect, useContext,  } from "react";
import { useParams } from "react-router";
import useExRequest from "../customHooks/ExternalRequestHook";
import { uiContext } from "../customContexts/UiContext";
import mtnLogo from "../assets/images/mtn.jpg";
import airtelLogo from "../assets/images/airtel.png";
import gloLogo from "../assets/images/glo.png";
import nineMobileLogo from "../assets/images/9mobile.png"; 

const Toast= ({ message, isVisible }) => { 
  if (!isVisible) return null;
  return (
    <div className="fixed bottom-4 right-4 bg-gray-800 text-white px-6 py-3 rounded-lg shadow-lg animate-fade-in-up">
      <div className="flex items-center">
        <i className="fas fa-check-circle mr-2"></i>
        {message}
      </div>
    </div>
  );
};

const ShareDialog = ({ isOpen, onClose }) => {
  const [message, setMessage] = useState("");
  if (!isOpen) return null;
  const shareOptions = [
    { icon: "fa-envelope", label: "Email", action: () => {} },
    {
      icon: "fa-whatsapp",
      label: "WhatsApp",
      action: () => {
        const baseText = "Transaction Receipt: TRX-20230921 for $1,250.00";
        const userMessage = message.trim();
        const fullText = userMessage
          ? `${baseText}\n\n${userMessage}`
          : baseText;
        const encodedText = encodeURIComponent(fullText);
        const whatsappUrl = `https://wa.me/?text=${encodedText}`;
        window.open(whatsappUrl, "_blank");
      },
    },
    { icon: "fa-link", label: "Copy Link", action: () => {} },
    { icon: "fa-telegram", label: "Telegram", action: () => {} },
    { icon: "fa-twitter", label: "Twitter", action: () => {} },
  ];

  const getNetworkLogo = (network) => {
    switch (network?.toLowerCase()) {
      case "mtn":
        return mtnLogo;
      case "airtel":
        return airtelLogo;
      case "glo":
        return gloLogo;
      case "9mobile":
        return nineMobileLogo;
      default:
        return "";
    }
  };

  return (
    <div className="fixed inset-0  bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white  rounded-xl shadow-xl w-full max-w-sm mx-4">
        <div className="p-4 ">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-xl font-semibold text-gray-800">
              Share Receipt
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors !rounded-button whitespace-nowrap"
            >
              <i className="fas fa-times"></i>
            </button>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 mb-2">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <i className="fas fa-receipt text-blue-600 text-xl"></i>
              </div>
              <div>
                <p className="font-medium text-gray-800">Transaction Receipt</p>
                <p className="text-sm text-gray-500">
                  TRX-20230921 • $1,250.00
                </p>
              </div>
            </div>
          </div>
          <div className="mb-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Add a message (optional)
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="w-full border border-gray-200 rounded-lg p-2 text-sm"
              placeholder="Type your message here..."
              rows={3}
            ></textarea>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {shareOptions.map((option) => (
              <button
                key={option.label}
                onClick={option.action}
                className="flex flex-col items-center p-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors !rounded-button whitespace-nowrap"
              >
                <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center mb-2">
                  <i className={`fas ${option.icon} text-gray-600`}></i>
                </div>
                <span className="text-sm font-medium text-gray-700">
                  {option.label}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};


const TransectionStatus = () => {
  const [trx,setTrx] = useState({});
  const {
    id:trx_id,amount,transaction_type,notes,
    status:statu,trx_ref,trx_date,updated_at,
    receiver,user,net_charges,data_plane,phone_number,network,
  } = trx
  const {sendExRequest} = useExRequest();
  const {id} = useParams();
  const {getFormattedDate,formatNaira,copyToClipboard} = useContext(uiContext);
  const [showConfetti, setShowConfetti] = useState(true);
  const [showToast, setShowToast] = useState(false);
  const [isShareDialogOpen, setIsShareDialogOpen] = useState(false);
  const [withDetails,setWithDetails] =useState({})
  const [depoDetails,setDepoDetails] =useState({
    })
  const generatePDF = () => {
    const doc = new jsPDF();
    // Set font styles
    doc.setFont("helvetica", "bold");
    doc.setFontSize(20);
    doc.text("Transaction Receipt", 20, 20);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(12);
    // Add transaction details
    const details = [
      ["Transaction ID:", "TRX-20230921"],
      ["Amount:", "$1,250.00"],
      ["Date & Time:", "November 20, 2023 • 3:30 PM"],
      ["Status:", "Completed"],
      ["Transaction Type:", "Bank Transfer"],
      ["Transaction Fee:", "$0.00"],
      [""],
      ["From:"],
      ["Account Holder:", "John Smith"],
      ["Bank:", "Chase Bank"],
      ["Account Number:", "****4588"],
      [""],
      ["To:"],
      ["Account Holder:", "Sarah Johnson"],
      ["Bank:", "Wells Fargo"],
      ["Account Number:", "****9523"],
      [""],
      ["Description:", "Monthly rent payment"],
      ["Reference Number:", "REF-20231120-ABCD"],
    ];
    let yPos = 40;
    details.forEach(([label, value]) => {
      if (value) {
        doc.setFont("helvetica", "bold");
        doc.text(label, 20, yPos);
        doc.setFont("helvetica", "normal");
        doc.text(value || "", 80, yPos);
      } else {
        doc.text(label, 20, yPos);
      }
      yPos += 10;
    });
    // Save the PDF
    doc.save("transaction-receipt.pdf");
    // Show toast notification
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };
  const getTheTrx = (data) => {
    setTrx(data.data)
    console.log('trx here : ', data);
  }
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowConfetti(false);
    }, 3000);
    return () => clearTimeout(timer);
  }, []);
  useEffect(() => {
    setDepoDetails ({
    'Amount':`${formatNaira(trx?.amount)}`,
    'Payment Type' :trx?.payment_type,
    "Deposite Account Number ":trx?.depositor_acc_num,
    "Deposite Bank":trx?.depositor_bank,
    'Deposite Account Name ':trx?.depositor_name,
      })
    setWithDetails({
    'Amount':`${formatNaira(trx?.amount)}`,
    "Account Number ":trx?.withdrawal_account_number,
    "Bank":trx?.withdrawal_bank_name,
    'Account Name ':trx?.withdrawal_account_name,
    'Note':`${trx?.notes || "No reason!"}`

  })

  },[trx])
  useEffect(() => {
    sendExRequest(`/account/trx/${id}`, "GET", null,getTheTrx)
  },[id])
  const status = statu === 'pending'?'pending':
                (statu === 'approved'|| statu === 'success')? 'completed': 'failed'
  return (
    <div className="min-h-max bg-gray-50  ">

      {Object.keys(trx).length > 0 && <div className="relative w-full max-w-3xl  bg-white rounded-xl shadow-lg overflow-hidden">
      <button className="z-20 absolute top-2 right-3 flex  gap-2 items-center cursor-pointer !rounded-button whitespace-nowrap">
            <div className=" rounded-full cursor-pointer flex gap-2   items-center justify-center ">
              <i className="fas fa-question-circle text-xl text-red-900 hover:text-red-600"></i>
            </div>

      </button>
        {/* Success Header with Animation */}
        <div className={`relative p-4 text-center ${
            status === "completed"
              ? "bg-gradient-to-r from-green-50 to-green-100"
              : status === "failed"
                ? "bg-gradient-to-r from-red-100 to-red-200"
                : "bg-gradient-to-r bg-yellow-100 to-yellow-200"
          }`}
        
        >
          {showConfetti && (
            <div className="absolute inset-0 overflow-hidden">
              {[...Array(50)].map((_, i) => (
                <div
                  key={i}
                  className="absolute animate-confetti"
                  style={{
                    left: `${Math.random() * 100}%`,
                    top: `-${Math.random() * 20}%`,
                    width: `${Math.random() * 10 + 5}px`,
                    height: `${Math.random() * 10 + 5}px`,
                    backgroundColor: [
                      "#FFC107",
                      "#4CAF50",
                      "#2196F3",
                      "#E91E63",
                      "#9C27B0",
                    ][Math.floor(Math.random() * 5)],
                    transform: `rotate(${Math.random() * 360}deg)`,
                    animation: `fall ${Math.random() * 3 + 2}s linear forwards`,
                  }}
                />
              ))}
            </div>
          )}
          <div
            className={`status-icon mb-4 inline-flex ${
              status === "pending" ? "animate-spin" : ""
            }`}
          >
            <div
              className={`rounded-full w-12 h-12 flex  items-center justify-center ${
                status === "completed"
                  ? "bg-green-500"
                  : status === "failed"
                    ? "bg-red-500"
                    : "bg-yellow-500"
              }`}>
              <i
                className={`fas ${
                  status === "completed"
                    ? "fa-check"
                    : status === "failed"
                      ? "fa-times"
                      : "fa-clock"
                } text-white text-3xl`}
              ></i>
            </div>
          </div>
          <div  className={`${status == "pending" ? "animate-pulse-gentle" : ""}`}>
            <p className="text-xl font-bold text-gray-900 mb-1">{formatNaira(amount)}</p>
          </div>
          <h1
            className={`text-xl font-semibold mb-1 ${
              status === "completed"
                ? "text-gray-800"
                : status === "failed"
                  ? "text-red-800"
                  : "text-yellow-800"
            }`}
          >
            {`Transection ${statu}`}
          </h1>
          <div className="text-sm font-medium text-gray-900 border rounded-full -mb-3">
            {transaction_type}
          </div>
        </div>

        {/* Transaction Details */} 
        <div className="px-3 border-b border-gray-100" >
          
          <div className="grid grid-cols-2 gap-2">
            {transaction_type === 'Withdraw' ? 
            (Object.entries(withDetails).map(([key,value]) => (
               <div>
              <p className="text-sm text-gray-500 mb-1">{key}</p>
              <div className="flex items-center">
                <p className="text-sm font-medium text-gray-800">
                  {value}
                </p>
              </div>
            </div>
            ))):(transaction_type === 'Deposite') ?
             (Object.entries(depoDetails).map(([key,value]) => (
              <div>
              <p className="text-sm text-gray-500 mb-1">{key}</p>
              <div className="flex items-center">
                <p className="text-sm font-medium text-gray-800">
                  {value}
                </p>
              </div>
            </div>
             ))):''}
            
            <div>
              <p className="text-sm text-gray-500 mb-1">Transaction ID</p>
              <div className="flex items-center">
                <p className="text-sm font-medium text-gray-800">
                  {`${trx_id?.slice(0, 5)}*****${trx_id?.slice(-4)}`}
                </p>
                <button onClick={() => {
                  copyToClipboard(trx_id,'Transection id copied!')
                }}
                className="ml-2 text-blue-500 cursor-pointer !rounded-button whitespace-nowrap">
                  <i className="fas fa-copy text-xs" ></i>
                </button>
              </div>
            </div>

            <div>
              <p className="text-sm text-gray-500 mb-1">Reference Number</p>
              <div className="flex items-center">
                <p className="text-sm font-medium text-gray-800">
                  {trx_ref || "REF-No"}
                </p>
                {trx_ref && <button 
                onClick={() => 
                  {copyToClipboard(trx_ref,'transectin Ref No copied!')}
                }
                className="ml-2 text-blue-500 cursor-pointer !rounded-button whitespace-nowrap">
                  <i className="fas fa-copy text-xs"></i>
                </button>}
              </div>
            </div>

            <div>
              <p className="text-sm text-gray-500 mb-1">Date & Time</p>
              <p className="text-sm font-medium text-gray-800">
                {getFormattedDate(trx_date)}
              </p>
            </div>
            
            {net_charges &&  <div>
              <p className="text-sm text-gray-500 mb-1">Transaction Fee</p>
              <p className="text-sm font-medium text-gray-800">{formatNaira(net_charges)}</p>
            </div>}

          </div>
        </div>

        {/* Transfer Details */}
        {(transaction_type === 'Transfer-In' || transaction_type === "Transfer-Out") &&
        <div className="border-b border-gray-100 ">
          
          <div className="max-w-lg mx-auto my-2" >
            <div className="flex items-center justify-between mb-">
              <div className="flex-1 pr-2 ">
                <div className="bg-gray-50 rounded-lg p-1">
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                      <i className="fas fa-arrow-up text-blue-600 text-sm"></i>
                    </div>
                    <div className="flex-1">
                      <p className="text-xs text-gray-500">From</p>
                      <p className="text-sm font-medium text-gray-800">
                        @{trx?.sender?.username}
                      </p>
                      <div className="flex items-center mt-1">
                        <i className="fas fa-university text-gray-400 text-xs mr-1"></i>
                        <p className="text-xs text-gray-600">
                          wallet balance
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="px-2">
                <i className="fas fa-arrow-right text-gray-400"></i>
              </div>
              <div className="flex-1 pl-4">
                <div className="bg-gray-50 rounded-lg p-1">
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3">
                      <i className="fas fa-arrow-down text-green-600 text-sm"></i>
                    </div>
                    <div className="flex-1">
                      <p className="text-xs text-gray-500">To</p>
                      <p className="text-sm font-medium text-gray-800">
                        @{receiver?.username || 'unknown user'}
                      </p>
                      <div className="flex items-center mt-1">
                        <i className="fas fa-university text-gray-400 text-xs mr-1"></i>
                        <p className="text-xs text-gray-600">
                          Funding Wallet
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>}
        {/* airirme or data details  */}
        {(transaction_type === 'Airtime' || transaction_type === "Data") &&
        <div className="px-3 border-b border-gray-100">
          <div>
              <p className="text-sm text-gray-500 mb-1">Phone Number</p>
              <div className="flex items-center">
                <p className="text-sm font-medium text-gray-800">
                  {phone_number || "No number"}
                </p>
                <button onClick={() => {
                  copyToClipboard(phone_number,'Phone Number Copied!')
                }}
                className="ml-2 text-blue-500 cursor-pointer !rounded-button whitespace-nowrap">
                  <i className="fas fa-copy text-xs" ></i>
                </button>
              </div>
            </div>
            
            <div>
              <p className="text-sm text-gray-500 mb-1">Network </p>
              <div className="flex items-center">
                <p className="text-sm font-medium text-gray-800 flex items-center">
                <img src={getNetworkLogo(network)} alt={`${network} logo`} className="inline-block w-6 h-6 mr-2" />
                  
                  <span> {network || "Net"} </span>
                </p>
                {trx_ref && <button 
                onClick={() => 
                  {copyToClipboard(trx_ref,'transectin Ref No copied!')}
                }
                className="ml-2 text-blue-500 cursor-pointer !rounded-button whitespace-nowrap">
                  <i className="fas fa-copy text-xs"></i>
                </button>}
              </div>
            </div>

            <div>
              <p className="text-sm text-gray-500 mb-1">Data Plane</p>
              <p className="text-sm font-medium text-gray-800">
                {data_plane || "No data"}
              </p>
            </div>
         
        </div>
        }
      
        {/* Action Buttons */}
        <div className="p-2 flex flex-wrap gap-2">
          <button
            id="downloadReceiptBtn"
            onClick={generatePDF}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-3 rounded-lg shadow-sm flex items-center justify-center transition-all cursor-pointer !rounded-button whitespace-nowrap"
          >
            <i className="fas fa-download mr-2"></i>
            Download Receipt
          </button>
          <button
            id="shareReceiptBtn"
            onClick={() => setIsShareDialogOpen(true)}
            className="flex-1 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 py-2 px-3 rounded-lg shadow-sm flex items-center justify-center transition-all cursor-pointer !rounded-button whitespace-nowrap"
          >
            <i className="fas fa-share-alt mr-2"></i>
            Share Receipt
          </button>
        </div>

      </div>}

      <Toast message="Receipt downloaded successfully" isVisible={showToast} />
      <ShareDialog
        isOpen={isShareDialogOpen}
        onClose={() => setIsShareDialogOpen(false)}
      />
      <style jsx>{`
@keyframes fall {
0% {
transform: translateY(0) rotate(0deg);
opacity: 1;
}
100% {
transform: translateY(100vh) rotate(360deg);
opacity: 0;
}
}
.animate-confetti {
position: absolute;
animation-timing-function: ease-in-out;
}
.animate-pulse-gentle {
animation: pulse 2s infinite;
}
@keyframes pulse {
0%, 100% {
transform: scale(1);
}
50% {
transform: scale(1.03);
}
}
.success-checkmark {
animation: scale-up 0.5s ease-out;
}
.animate-fade-in-up {
animation: fadeInUp 0.3s ease-out;
}
@keyframes fadeInUp {
from {
opacity: 0;
transform: translateY(20px);
}
to {
opacity: 1;
transform: translateY(0);
}
}
@keyframes scale-up {
0% {
transform: scale(0);
}
70% {
transform: scale(1.1);
}
100% {
transform: scale(1);
}
}
`}</style>
    </div>
  );
};
export default TransectionStatus;
