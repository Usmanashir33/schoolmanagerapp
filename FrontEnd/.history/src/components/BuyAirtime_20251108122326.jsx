import React, { useContext, useEffect, useState } from "react";
import { ShoppingBag, PhoneCall, ChevronDown, CreditCard, CheckCircle, History, XCircle, Smartphone } from "lucide-react";
import mtnLogo from "../assets/images/mtn.jpg";
import airtelLogo from "../assets/images/airtel.png";
import gloLogo from "../assets/images/glo.png";
import nineMobileLogo from "../assets/images/9mobile.png";
import { uiContext } from "../customContexts/UiContext";
import Pins from "./PinsPage";

const networkOptions = [
  { name: "MTN", logo: mtnLogo },
  { name: "Airtel", logo: airtelLogo },
  { name: "Glo", logo: gloLogo },
  { name: "9mobile", logo: nineMobileLogo },
];

const mockHistory = [
  { number: "08123456789", network: "MTN", date: "2025-10-28" },
  { number: "09012345678", network: "Airtel", date: "2025-10-29" },
  { number: "08055555555", network: "Glo", date: "2025-11-01" },
];

export default function AirtimeSellingPage() {
  const { setError } = useContext(uiContext);
  const [selectedNetwork, setSelectedNetwork] = useState(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [confirmation, setConfirmation] = useState(null);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [amount, setAmount] = useState("");
  const [showPins, setShowPins] = useState(false);

  const recommendedAmounts = [100, 200, 500, 1000, 5000, 10000];

  const verifyPins = (pins) => {
    setShowPins(false);
  };

  const handleBuy = (amt) => {
    setAmount(amt);
    if (selectedNetwork && phoneNumber && amt) {
      setConfirmation({
        network: selectedNetwork.name,
        amount: amt,
        number: phoneNumber,
        logo: selectedNetwork.logo,
        date: new Date().toLocaleDateString(),
      });
    } else {
      setError("Please select a network, enter a valid number, and specify amount.");
    }
  };

  const closeConfirmation = () => setConfirmation(null);

  function identifyTelecomProvider(phoneNumber) {
    let number = phoneNumber;
    const prefix = phoneNumber.substring(0, 4);
    const prefix2 = phoneNumber.substring(0, 3);
    const possibleInputs = ["+234", "234"];
    let found = possibleInputs.find((num) => num === prefix) ?? possibleInputs.find((num) => num === prefix2);
    if (found) number = number.replace(found, "");
    if (number.substring(0, 1) !== "0") number = "0" + number;
    setPhoneNumber(number);

    const mtnPrefixes = ["0803", "0806", "0703", "0706", "0813", "0814", "0816", "0903", "0906", "0913", "0916"];
    const gloPrefixes = ["0805", "0807", "0705", "0811", "0815", "0905", "0915"];
    const etisalatPrefixes = ["0809", "0817", "0818", "0909", "0908"];
    const airtelPrefixes = ["0802", "0808", "0701", "0708", "0812", "0901", "0902", "0904", "0907", "0912"];

    const Lastprefix = number.substring(0, 4);
    if (mtnPrefixes.includes(Lastprefix)) setSelectedNetwork(networkOptions.find((n) => n.name === "MTN"));
    else if (gloPrefixes.includes(Lastprefix)) setSelectedNetwork(networkOptions.find((n) => n.name === "Glo"));
    else if (etisalatPrefixes.includes(Lastprefix)) setSelectedNetwork(networkOptions.find((n) => n.name === "9mobile"));
    else if (airtelPrefixes.includes(Lastprefix)) setSelectedNetwork(networkOptions.find((n) => n.name === "Airtel"));
  }

  const setNumber = (e) => {
    const inputValue = e.target.value;
    if (/^\d*$/.test(inputValue) && inputValue.length <= 11) {
      setPhoneNumber(e.target.value);
      if (e.target.value.length >= 4) identifyTelecomProvider(e.target.value);
    }
  };
  const setAmountTyped = (input) => {
         // Allow only numeric input and limit to 5 digits
         if (/^\d*$/.test(input) && input.length <= 4) {
            setAmount(input)
        }
    }

  useEffect(() => {
    if (phoneNumber.length >= 4) identifyTelecomProvider(phoneNumber);
  }, [selectedNetwork]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 flex flex-col items-center">
      <div className="bg-white shadow-2xl rounded-2xl w-full max-w-3xl p-6 animate-fadeIn relative">
        <div className="flex items-center justify-between mb-6 border-b pb-3">
          <div className="flex items-center gap-2">
            <PhoneCall className="text-blue-600" size={28} />
            <h1 className="text-2xl font-bold text-gray-800">Buy Airtime</h1>
          </div>
          <button onClick={() => setShowHistory(!showHistory)} className="flex items-center gap-1 text-gray-600 hover:text-blue-600 transition">
            <History size={20} /> <span className="text-sm font-medium">History</span>
          </button>
        </div>

        {showHistory && (
          <div className="mb-6 bg-gray-50 border rounded-xl p-3 animate-fadeIn">
            <h3 className="text-gray-700 font-semibold mb-2 flex items-center gap-2">
              <History className="text-blue-600" size={18} /> Recent Airtime Purchases
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

        <div className="mb-4 flex items-center border rounded-xl px-3 py-2 bg-gray-50 focus-within:border-blue-400">
          <Smartphone size={20} className="text-gray-500 mr-2" />
          <input type="tel" placeholder="Enter recipient phone number" value={phoneNumber} onChange={(e) => setNumber(e)} className="w-full bg-transparent outline-none text-gray-700 placeholder-gray-400" />
        </div>


        {selectedNetwork && (
          <div className="bg-gray-50 rounded-xl p-4 shadow-inner">
            <div className="flex items-center gap-3 mb-3">
              <img src={selectedNetwork.logo} alt="selected" className="h-8 w-8 rounded-full" />
              <h2 className="text-lg font-semibold text-gray-800">Recommended Airtime Amounts</h2>
            </div>

            <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
              {recommendedAmounts.map((amt, i) => (
                <button key={i} onClick={() => handleBuy(amt)} className="border rounded-xl p-3 bg-white hover:bg-blue-50 hover:border-blue-400 transition-all text-gray-700 font-medium">
                  ₦{amt}
                </button>
              ))}
            </div>
          </div>
        )}
        <div className="mb-4  ">
          <label className="block text-gray-700 mb-2 text-sm font-medium">Enter Amount (₦)</label>
          {/* remove the up and down arrows from number input */}
          <span className="flex">
             <input type="tel" placeholder="Custom amount (<₦ 10,000)" value={amount} onChange={(e) => setAmountTyped(e.target.value)} className="w-full px-4 py-2 border  rounded-xl bg-gray-50 outline-none focus:border-blue-400" />
        
          </span>
        </div>

        {confirmation && (
          <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-10">
            <div className="bg-white rounded-2xl shadow-2xl p-6 w-[90%] max-w-sm relative animate-fadeIn">
              <button onClick={closeConfirmation} className="absolute top-3 right-3 text-gray-400 hover:text-gray-600">
                <XCircle size={22} />
              </button>

              <div className="text-center mb-5">
                <img src={confirmation.logo} alt="network" className="h-12 w-12 mx-auto mb-2 rounded-full" />
                <h2 className="text-xl font-semibold text-gray-800">Confirm Airtime Purchase</h2>
                <p className="text-gray-500 text-sm">Review your details before proceeding.</p>
              </div>

              <div className="border rounded-xl bg-gray-50 p-4 text-sm text-gray-700 space-y-2">
                <p><strong>Network:</strong> {confirmation.network}</p>
                <p><strong>Recipient Number:</strong> {confirmation.number}</p>
                <p><strong>Amount:</strong> ₦{confirmation.amount}</p>
                <p><strong>Date:</strong> {confirmation.date}</p>
              </div>

              <div className="flex justify-center gap-4 mt-5">
                <button onClick={closeConfirmation} className="px-4 py-2 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-100">Cancel</button>
                <button onClick={() => setShowPins(true)} className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700">Confirm</button>
              </div>
            </div>
          </div>
        )}

        {showPins && (
          <div className="fixed inset-0 top-8 bg-black/40 backdrop-blur-sm flex items-center justify-center z-40 shadow-lg max-w-md mx-auto rounded-md">
            <Pins close={setShowPins} triggerFunc={verifyPins} />
          </div>
        )}

        <div className="mt-8 bg-blue-50 border border-blue-100 rounded-xl p-4 text-center">
          <CheckCircle className="mx-auto text-green-500 mb-2" />
          <p className="text-gray-700 text-sm">Enjoy instant airtime top-up service. Your airtime will be credited immediately after purchase.</p>
        </div>
      </div>
    </div>
  );
}
