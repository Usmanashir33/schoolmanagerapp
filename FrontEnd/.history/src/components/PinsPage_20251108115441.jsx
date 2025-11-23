import {  ArrowLeft } from "lucide-react";
import { useContext, useEffect, useState } from "react";
import { uiContext } from "../customContexts/UiContext";
import { authContext } from "../customContexts/AuthContext";
import PinPasswordManger from "./PinPasswordManger";
const Pins= ({close,triggerFunc}) => {
  // the close is not toggle is function 
  const {currentUser,setCurrentUser} = useContext(authContext);
  const [allowPin, setAllowPin] = useState(true); 

  const [pinValues, setPinValues] = useState(Array(4).fill(""));
  const [currentIndex, setCurrentIndex] = useState(0);
  const {isLoading} = useContext(uiContext);
  const [error, setError] = useState("");

  const settingNewPin = () => {
    //close is triggerd and new pins is set 
      setAllowPin(true);
      setCurrentUser((prev) => ({
        ...prev,
        payment_pin_set: true,
      }));
  };

  const handleNumberClick = (number) => {
    if (currentIndex < 4) {
      setError(""); 
      const newPinValues = [...pinValues];
      newPinValues[currentIndex] = number.toString();
      setPinValues(newPinValues);
      setCurrentIndex(currentIndex + 1);
    }
  };
  const handleBackspace = () => {
    if (currentIndex > 0) {
      const newPinValues = [...pinValues];
      newPinValues[currentIndex - 1] = "";
      setPinValues(newPinValues);
      setCurrentIndex(currentIndex - 1);
    }
  };
  
  useEffect(() => {
    if (currentUser && currentUser.payment_pin_set) {
      setAllowPin(true);
    } else {
      setAllowPin(false);
    }
  }, [currentUser]);
  const handleConfirm = () => {
    if (pinValues.some((value) => value === "")) {
      setError("Please enter all 4 digits"); 
      return;
    }
    const pins = pinValues.slice().splice(',').join('') 
    triggerFunc(pins);
    };
  return (
    <div 
    className="flex   justify-center items-cente  bg-gray-50 absolute w-full top-0 min-h-full z-30 ">
      {allowPin ? 
      <div className="w-full bg-white rounded-lg shadow-md px-5 relative py-2  ">
        <span 
        onClick={() => {close(false)}}
        className="text-blue-600 flex gap-2 items-center  mx-auto cursor-pointer !rounded-button whitespace-nowrap text-sm">
            <ArrowLeft  strockWidth={1.5}/>
            Back
        </span>
        {
          <>
            <div className="text-center mb-3 ">
              <h1 className="text-xl font-semibold text-gray-800">Enter PIN</h1>
              <p className="text-sm text-gray-500 mt-1">
                Please enter your 4-digit PIN to confirm transaction.
              </p>
            </div> 

            <div className="flex justify-center gap-10  space-x-3 p-2   bg-gray-100 bg-opacity-40">
              {pinValues.map((value, index) => (
                <div
                  key={index}
                  className="w-10 h-10 rounded-lg border border-gray-300 flex items-center justify-center"
                >
                  {value ? (
                    <div className="w-3 h-3 bg-black rounded-full  "> </div>
                  ) : null}
                </div>
              ))}
            </div>
             {error && (
                <div className="text-red-500 text-sm text-center">{error}</div>
              )}
            <div className=" w-full flex justify-center  ">
                <div className="grid grid-cols-3 gap-2 mb-3  max-w-max ">
                {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((number) => (
                    <button
                    key={number}
                    onClick={() => handleNumberClick(number)}
                    className="w-14 h-14 mx-9  rounded-full bg-white border border-gray-500 text-xl font-medium text-gray-800 flex items-center justify-center cursor-pointer !rounded-button whitespace-nowrap hover:bg-gray-50"
                    >
                    {number}
                    </button>
                ))}
                <div className="col-start ">
                    <button
                    onClick={handleBackspace}
                    className="w-14 h-14 mx-9 rounded-full bg-white border border-gray-500  text-xl flex items-center justify-center cursor-pointer !rounded-button whitespace-nowrap hover:bg-gray-50"
                    >
                    <i className="fas fa-backspace text-gray-600"></i>
                    </button>
                </div>
                <div className=" mx-9 ">
                    <button
                    onClick={() => handleNumberClick(0)}
                    className="w-14 h-14 rounded-full bg-white border border-gray-500  text-xl font-medium text-gray-800 flex items-center justify-center cursor-pointer !rounded-button whitespace-nowrap hover:bg-gray-50"
                    >
                    0
                    </button>
                </div>
                </div>
            </div>
            
            <div className="  ">
              <button
                id="confirmButton"
                onClick={handleConfirm}
                disabled={isLoading}
                className={`w-full mx-w-xs py-1 bg-blue-600 text-white font-medium rounded-md cursor-pointer !rounded-button whitespace-nowrap hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center`}
              >
                {isLoading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Processing...
                  </>
                ) : (
                  "Confirm "
                )}
              </button>
            </div>
            
           
          </>
        }
      </div>
    : 
      <PinPasswordManger mode="Reset" closeModal={close} grabSuccess={settingNewPin}/>
    }
    </div>
  );
};
export default Pins;
