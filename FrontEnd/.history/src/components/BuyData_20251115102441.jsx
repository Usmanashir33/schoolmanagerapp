import React, { useContext, useEffect, useState } from "react";
import { ShoppingBag, Wifi, ChevronDown, CreditCard, CheckCircle, History, XCircle, Smartphone } from "lucide-react";
import mtnLogo from "../assets/images/mtn.jpg";
import airtelLogo from "../assets/images/airtel.png";
import gloLogo from "../assets/images/glo.png";
import nineMobileLogo from "../assets/images/9mobile.png";
import { uiContext } from "../customContexts/UiContext";
import Pins from "./PinsPage";
import useSendTransection from "../customHooks/SendTransection";
// // import smileLogo from "../assets/smile-logo.png";

const networkOptions = [
  { name: "MTN", logo: mtnLogo, plans: [ { size: "500MB", price: 150 }, { size: "1GB", price: 300 }, { size: "2GB", price: 500 }, { size: "5GB", price: 1000 } ] },
  { name: "Airtel", logo: airtelLogo, plans: [ { size: "500MB", price: 140 }, { size: "1GB", price: 280 }, { size: "2GB", price: 480 }, { size: "5GB", price: 950 } ] },
  { name: "Glo", logo: gloLogo, plans: [ { size: "500MB", price: 130 }, { size: "1GB", price: 270 }, { size: "2GB", price: 450 }, { size: "5GB", price: 900 } ] },
  { name: "9mobile", logo: nineMobileLogo, plans: [ { size: "500MB", price: 160 }, { size: "1GB", price: 320 }, { size: "2GB", price: 520 }, { size: "5GB", price: 1000 } ] },
//   { name: "Smile", logo: "https://upload.wikimedia.org/wikipedia/en/4/48/Smile_logo.png", plans: [ { size: "1GB", price: 350 }, { size: "2GB", price: 600 }, { size: "5GB", price: 1200 } ] }
];

const mockHistory = [
  { number: "08123456789", network: "MTN", date: "2025-10-28" },
  { number: "09012345678", network: "Airtel", date: "2025-10-29" },
  { number: "08055555555", network: "Glo", date: "2025-11-01" },
];

export default function DataSellingPage() {
    const {setError} = useContext(uiContext);
  const [selectedNetwork, setSelectedNetwork] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [confirmation, setConfirmation] = useState(null);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [showPins, setShowPins] = useState(false);
  const {sendTransectionRequest} = useSendTransection();

   const serverRespo = (resp) => {
    console.log('resp: ', resp);

  }

  const verifyPins = (pins) => {
    const url = `/account/airtimeOrData/`
    let formdata={
      payment_pin : pins,
      amount :confirmation?.price,
      data_size :confirmation?.size,
      phone_number :confirmation?.number,
      transaction_type:'Data',
      network: confirmation?.network,
    }
    sendTransectionRequest(url,'POST',formdata,serverRespo,true)
    setShowPins(false);
  };
  const handleBuy = (plan) => {
    if (selectedNetwork && phoneNumber) {
      setConfirmation({
        network: selectedNetwork.name,
        size: plan.size,
        price: plan.price,
        number: phoneNumber,
        logo: selectedNetwork.logo,
        date: new Date().toLocaleDateString(),
      });
    } else {
      setError("Please select a network and enter a valid phone number.");
    }
  };

    const closeConfirmation = () => setConfirmation(null);
   
    // Function to determine the telecom provider
    function identifyTelecomProvider(phoneNumber){
        let number = phoneNumber;
        // Extract the first 4 digits
        const prefix = phoneNumber.substring(0, 4);
        const prefix2 = phoneNumber.substring(0, 3);
        const possibleInuts = ['+234','234',] ;

        let foundNumbers = possibleInuts.find((num) => num === prefix)?? possibleInuts.find((num) => num === prefix2)
        foundNumbers? number = number.replace(foundNumbers,"") : null
        if (number.substring(0,1) !== "0"){
            number = '0' + number
        }
        // to make sure it looks 081,090 etc
        setPhoneNumber(number);

        // Prefix lists
        const mtnPrefixes = [
            "0803", "0806", "0703","0706","0704", "0813", "0814", "0816", "0903", "0906", "0913", "0916"
        ];
        const gloPrefixes = [
            "0805", "0807", "0705", "0811", "0815", "0905", "0915"
        ];
        const etisalatPrefixes = [
            "0809", "0817", "0818", "0909", "0908"
        ];
        const airtelPrefixes = [
            "0802", "0808", "0701", "0708", "0812", "0901", "0902", "0904", "0907", "0912"
        ];

        const Lastprefix = number.substring(0, 4);
        // Match the prefix to a provider
        if (mtnPrefixes.includes(Lastprefix)) {
            setSelectedNetwork(networkOptions.find(net => net.name === "MTN"));
            return "MTN";

        } else if (gloPrefixes.includes(Lastprefix)) {
            setSelectedNetwork(networkOptions.find(net => net.name === "Glo"));
            return "Glo";

        } else if (etisalatPrefixes.includes(Lastprefix)) {
            setSelectedNetwork(networkOptions.find(net => net.name === "9mobile"));
            return "9mobile";

        } else if (airtelPrefixes.includes(Lastprefix)) {
            setSelectedNetwork(networkOptions.find(net => net.name === "Airtel"));
            return "Airtel";

        } else {
            return "Unknown provider";
        }
    }
    // will collect the input number and set it appropriately
    // also identify its provider
    const setNumber = (e) => {
         // Allow only numeric input and limit to 5 digits
         const inputValue = e.target.value;
         if (/^\d*$/.test(inputValue) && inputValue.length <= 11) {
            setPhoneNumber(e.target.value)
            if (e.target.value.length >= 4){
                identifyTelecomProvider(e.target.value)
            }
        }
    }
    useEffect(() => {
       if (phoneNumber.length >= 4){
        identifyTelecomProvider(phoneNumber)
       }
    }, [selectedNetwork,]);
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 flex flex-col items-center">
      
      <div className="bg-white shadow-2xl rounded-2xl w-full max-w-3xl p-6 animate-fadeIn relative">
        <div className="flex items-center justify-between mb-6 border-b pb-3">
          <div className="flex items-center gap-2">
            <Wifi className="text-blue-600" size={28} />
            <h1 className="text-2xl font-bold text-gray-800">Buy Data Bundle</h1>
          </div>
          <button onClick={() => setShowHistory(!showHistory)} className="flex items-center gap-1 text-gray-600 hover:text-blue-600 transition">
            <History size={20} /> <span className="text-sm font-medium">History</span>
          </button>
        </div>
        {/* show pins here  */}
        {showHistory && (
          <div className="mb-6 bg-gray-50 border rounded-xl p-3 animate-fadeIn">
            <h3 className="text-gray-700 font-semibold mb-2 flex items-center gap-2">
              <History className="text-blue-600" size={18} /> Recent Purchases
            </h3>
            <ul className="space-y-2">
              {mockHistory.map((item, i) => (
                <li key={i} className="flex justify-between items-center bg-white p-2 rounded-lg shadow-sm">
                  <div>
                    <p className="font-medium text-gray-800">{item.number}</p>
                    <p className="text-gray-500 text-xs">{item.network} • {item.date}</p>
                  </div>
                  <CheckCircle size={16} className="text-green-500" />
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Select Network */}
        <div className="relative mb-4">
          <button onClick={() => setShowDropdown(!showDropdown)} className="w-full flex justify-between items-center px-4 py-3 border rounded-xl hover:border-blue-400 bg-gray-50">
            {selectedNetwork ? (
              <div className="flex items-center gap-3">
                <img src={selectedNetwork.logo} alt="logo" className="h-6 w-6 rounded-full" />
                <span className="font-medium text-gray-700">{selectedNetwork.name}</span>
              </div>
            ) : (
              <span className="text-gray-500">Select Network</span>
            )}
            <ChevronDown size={20} className="text-gray-400" />
          </button>

          {showDropdown && (
            <div className="absolute mt-2 w-full bg-white shadow-lg rounded-xl border z-10 animate-fadeIn overflow-hidden">
              {networkOptions.map((network) => (
                <button key={network.name} onClick={() => { setSelectedNetwork(network); setShowDropdown(false); }} className="w-full flex items-center gap-3 px-4 py-2 hover:bg-blue-50 text-left">
                  <img src={network.logo} alt={network.name} className="h-6 w-6 rounded-md" />
                  <span className="text-gray-700 font-medium">{network.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Input phone number */}
        <div className="mb-6 flex items-center border rounded-xl px-3 py-2 bg-gray-50 focus-within:border-blue-400">
          <Smartphone size={20} className="text-gray-500 mr-2" />
          <input type="tel" placeholder="Enter recipient phone number" value={phoneNumber} 
          onChange={(e) => setNumber(e)} className="w-full bg-transparent outline-none text-gray-700 placeholder-gray-400" />
        </div>

        {selectedNetwork && (
          <div className="bg-gray-50 rounded-xl p-4 shadow-inner">
            <div className="flex items-center gap-3 mb-3">
              <img src={selectedNetwork.logo} alt="selected" className="h-8 w-8 rounded-full" />
              <h2 className="text-lg font-semibold text-gray-800">{selectedNetwork.name} Data Plans</h2>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {selectedNetwork.plans.map((plan, index) => (
                <div key={index} className="border rounded-xl p-3 flex justify-between items-center bg-white hover:shadow-md transition-all">
                  <div>
                    <p className="text-gray-800 font-semibold">{plan.size}</p>
                    <p className="text-gray-500 text-sm">₦{plan.price}</p>
                  </div>
                  <button onClick={() => handleBuy(plan)} className="px-3 py-1.5 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 flex items-center gap-1">
                    <CreditCard size={14} /> Buy
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Confirmation Modal */}
        {confirmation && (
          <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-10">
            <div className="bg-white rounded-2xl shadow-2xl p-6 w-[90%] max-w-sm relative animate-fadeIn">
              <button onClick={closeConfirmation} className="absolute top-3 right-3 text-gray-400 hover:text-gray-600">
                <XCircle size={22} />
              </button>

              <div className="text-center mb-5">
                <img src={confirmation.logo} alt="network" className="h-12 w-12 mx-auto mb-2 rounded-full " />
                <h2 className="text-xl font-semibold text-gray-800">Confirm Your Purchase</h2>
                <p className="text-gray-500 text-sm">Please review your details before proceeding.</p>
              </div>

              <div className="border rounded-xl bg-gray-50 p-4 text-sm text-gray-700 space-y-2">
                <p><strong>Network:</strong> {confirmation.network}</p>
                <p><strong>Recipient Number:</strong> {confirmation.number}</p>
                <p><strong>Data Plan:</strong> {confirmation.size}</p>
                <p><strong>Amount:</strong> ₦{confirmation.price}</p>
                <p><strong>Date:</strong> {confirmation.date}</p>
              </div>

              <div className="flex justify-center gap-4 mt-5">
                <button onClick={closeConfirmation} className="px-4 py-2 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-100">Cancel</button>
                <button onClick={() => { setShowPins(true) }}
                    className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700">Confirm</button>
              </div>
            </div>
          </div>
        )}

        {/* display pins  modal here  */}
        {showPins && <div className="fixed inset-0 top-8 bg-black/40 backdrop-blur-sm flex items-center justify-center z-40 shadow-lg max-w-md mx-auto rounded-md ">
            <Pins close={setShowPins} triggerFunc={verifyPins} />
          </div>}

        <div className="mt-8 bg-blue-50 border border-blue-100 rounded-xl p-4 text-center">
          <CheckCircle className="mx-auto text-green-500 mb-2" />
          <p className="text-gray-700 text-sm">Enjoy instant delivery and reliable service. Your data will be delivered automatically to your line.</p>
        </div>
      </div>
    </div>
  );
}
