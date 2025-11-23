// The exported code uses Tailwind CSS. Install Tailwind CSS in your dev environment to ensure all styles work.
import { faMultiply } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { ArrowLeft } from "lucide-react";
import { useContext, useState } from "react";

const TrxStatus= ({close, trxDetails}) => { 
  const [showToast, setShowToast] = useState(false);
  const [showShareDialog, setShowShareDialog] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
         
  const SuccessStatus = () => {
    return(
      <>
          <div className="  w-16 h-16 rounded-full bg-green-500 flex items-center justify-center mb-3"
          >
            <i className=" animate-pulse fas fa-check text-white text-2xl"></i>
          </div>
          <h2 className="text-xl font-semibold text-green-500">
            Transaction Successful
           </h2>
          <p className="text-sm text-gray-500 mt-1">
            Your transaction has been completed
          </p>
      </>
    )
  }
  const PendingStatus = () => {
    return(
      <>
         <div className="w-16 h-16 rounded-full bg-yellow-500 flex items-center justify-center mb-3">
                <i className="fas fa-clock text-white text-2xl animate-pulse "></i>
              </div>
              <h2 className="text-xl font-semibold text-yellow-600">
                Transaction Pending
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                Your transaction is in progress.... 
              </p>
              <p className="text-sm text-yellow-600 mt-2">
                This may take a few minutes to complete (Avg 5-10 minutes)
              </p>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-1 m-1">
              <p className="text-sm text-yellow-700">
                We'll notify you once the transaction is completed.
              </p>
            </div>
      </>
    )
  }
  const FailedStatus = () => {
    return(
      <>
        <div className="w-16 h-16 rounded-full bg-red-500 flex items-center justify-center mb-3">
                <i className="fas fa-xmark text-white text-2xl animate-pulse">
                  <FontAwesomeIcon icon={faMultiply}/>
                  </i> 
              </div>
              <h2 className="text-xl font-semibold text-red-500">
                Transaction Failed
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                Your transaction could not be completed
              </p>
             
            <div className="bg-red-50 border border-red-200 rounded-lg p-2 ">
              <p className="text-sm text-red-600">
                Please try again or contact our support team if the issue
                persists.
              </p>
              <p className="text-sm text-red-600 mt-1">
                Support: support@example.com 
              </p>
        </div>
      </>
    )
  }
  const handleShare = (type) => {
    switch (type) {
      case "email":
        setToastMessage("Opening email client...");
        break;
      case "message":
        setToastMessage("Opening messaging app...");
        break;
      case "copyLink":
        navigator.clipboard.writeText(
          "https://example.com/transaction/TRX-15456789",
        );
        setToastMessage("Link copied to clipboard");
        break;
      case "social":
        setToastMessage("Opening social media options...");
        break;
    }

    setShowToast(true);
    setTimeout(() => {
      setShowToast(false);
      setShowShareDialog(false);
    }, 2000);
  };

  return (
    <div 
    className="flex bbd justify-center items-center  bg-gray-50 absolute w-full top-0 min-h-full z-30">
      <div className="w-full bg-white rounded-lg shadow-md px- relative py-2">
        <span 
        onClick={() => {close(false)}}
        className=" sticky bbd  top-0 text-blue-600  items-center  text-sm flex bg-white gap-2 items-center mx-auto cursor-pointer !rounded-button whitespace-nowrap pb-1">
            {/* <i className="fas fa-arrow-left mr-2"></i> */}
            <ArrowLeft  className="p-1 font-medium "/>
            Back
        </span>
        {
          <div className="mb-1 bbd ">
            <div className="flex flex-col items-center mb-4 ">
              {trxDetails &&  
                  trxDetails['Status'] == 'success'?  <SuccessStatus/> :
                  trxDetails['Status'] == 'pending'?  <PendingStatus/> : <FailedStatus/>
               }
              

            </div>
            <div className="space-y-1 mb-3 border rounded-md p-1">
              {trxDetails && Object.entries(trxDetails).map(([key,value],index) =>  
                <div className="flex justify-between" key={`trx-det-${index}`}>
                  <span className="text-gray-500">{key}</span>
                  <span className={
                        key == "Amount"? 'font-medium':'text-gray-500'
                    }>
                    {key == "Amount"?`₦ ${value}`:value}</span>
              </div>
              )}
            </div>
            <div className="space-y-3">
              <div className="relative">
                {showToast && (
                  <div className="absolute -top-12 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white px-4 py-2 rounded-md text-sm transition-opacity duration-300">
                    Receipt downloaded successfully
                  </div>
                )}
                <button
                  id="downloadReceiptBtn"
                  onClick={() => {
                    const receiptContent = `
                        Transaction Receipt
                        ------------------
                        Amount: $1,234.56
                        Date & Time: Dec 15, 2023 • 14:30
                        Reference ID: TRX-15456789
                        Recipient: John Doe
                        `;
                    const blob = new Blob([receiptContent], {
                      type: "text/plain",
                    });
                    const url = window.URL.createObjectURL(blob);
                    const link = document.createElement("a");
                    link.href = url;
                    link.setAttribute("download", "transaction-receipt.txt");
                    document.body.appendChild(link);
                    link.click();
                    link.parentNode?.removeChild(link);
                    setShowToast(true);
                    setTimeout(() => {
                      setShowToast(false);
                    }, 3000);
                  }}
                  className="w-full py-2 border border-gray-200 rounded-md flex items-center justify-center cursor-pointer !rounded-button whitespace-nowrap hover:bg-gray-50"
                >
                  <i className="fas fa-download mr-2"></i>
                  Download Receipt
                </button>
              </div>
                  {/* check if its success or failed transection  */}
                    {trxDetails &&  
                    trxDetails['Status'] == 'success'?  (
                     <button
                      id="shareButton"
                      onClick={() => setShowShareDialog(true)}
                      className="w-full py-2 border border-gray-200 rounded-md flex items-center justify-center cursor-pointer !rounded-button whitespace-nowrap hover:bg-gray-50"
                    >
                      <i className="fas fa-share-alt mr-2"></i>
                      Share
                    </button>
                    ) :
                    trxDetails['Status'] == 'pending'?  (
                       <button
                          onClick={() => {
                            setShowToast(true);
                            setTimeout(() => setShowToast(false), 3000);
                          }}
                          className="w-full py-2 mb-2 bg-yellow-500 text-white rounded-md flex items-center justify-center cursor-pointer !rounded-button whitespace-nowrap hover:bg-yellow-600"
                        >
                          <i className="fas fa-rotate mr-2"></i>
                          Check Status
                      </button>
                    ) : ( 
                      <button
                          onClick={() => {''}}
                          className="w-full py-2 bg-red-500 text-white rounded-md flex items-center justify-center cursor-pointer !rounded-button whitespace-nowrap hover:bg-red-600"
                        >
                          <i className="fas fa-redo mr-2"></i>
                          Try Again
                      </button>
                    )
                    }
              {showShareDialog && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                  <div className="bg-white rounded-lg w-full max-w-md p-6 relative">
                    <button
                      id="closeShareDialog"
                      onClick={() => setShowShareDialog(false)}
                      className="absolute right-4 top-4 text-gray-400 hover:text-gray-600"
                    >
                      <i className="fas fa-times"></i>
                    </button>

                    <h3 className="text-xl font-semibold mb-4">
                      Share Transaction Details
                    </h3>

                    <div className="grid grid-cols-2 gap-4">
                      <button
                        id="shareEmail"
                        onClick={() => handleShare("email")}
                        className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 !rounded-button whitespace-nowrap"
                      >
                        <i className="fas fa-envelope text-xl text-blue-500 mr-3"></i>
                        <span>Email</span>
                      </button>

                      <button
                        id="shareMessage"
                        onClick={() => handleShare("message")}
                        className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 !rounded-button whitespace-nowrap"
                      >
                        <i className="fas fa-comment text-xl text-green-500 mr-3"></i>
                        <span>Message</span>
                      </button>

                      <button
                        id="shareCopyLink"
                        onClick={() => handleShare("copyLink")}
                        className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 !rounded-button whitespace-nowrap"
                      >
                        <i className="fas fa-link text-xl text-purple-500 mr-3"></i>
                        <span>Copy Link</span>
                      </button>

                      <button
                        id="shareSocial"
                        onClick={() => handleShare("social")}
                        className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 !rounded-button whitespace-nowrap"
                      >
                        <i className="fas fa-share-nodes text-xl text-orange-500 mr-3"></i>
                        <span>Social Media</span>
                      </button>
                    </div>

                    {showToast && (
                      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white px-4 py-2 rounded text-sm">
                        {toastMessage}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        }
      </div>
    </div>
  );
};
export default TrxStatus;
