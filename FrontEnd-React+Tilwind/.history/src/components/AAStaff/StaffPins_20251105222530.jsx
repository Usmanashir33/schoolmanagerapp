// The exported code uses Tailwind CSS. Install Tailwind CSS in your dev environment to ensure all styles work.
import React, { useEffect, useState } from "react";
const StaffPins = ({close,triggeredFunc,title=''}) => {
  const [pin, setPin] = useState(Array(5).fill(""));
  const [currentIndex, setCurrentIndex] = useState(0);
  // const [showModal, setShowModal] = useState(true);
  const [showError, setShowError] = useState(false);
  const [showForgotPinForm, setShowForgotPinForm] = useState(false);
  const [newPin, setNewPin] = useState(Array(5).fill(""));
  const [confirmPin, setConfirmPin] = useState(Array(5).fill(""));
  const [newPinIndex, setNewPinIndex] = useState(0);
  const [confirmPinIndex, setConfirmPinIndex] = useState(0);
  const [pinStep, setPinStep] = useState("new");
  const [error, setError] = useState('');

  const handleNumberClick = (number) => {
    if (currentIndex < 5) {
      const newPin = [...pin];
      newPin[currentIndex] = number.toString();
      setPin(newPin);
      setCurrentIndex(currentIndex + 1);
      setShowError(false);
    }
  };
  const handleSubmit = () => {
    if (pin.filter(Boolean).length === 5) {
        let pins = pin.join('')
        triggeredFunc(pins)
        // setPin(Array(5).fill(""));
        // setCurrentIndex(0);
        setShowError(false);
    } else {
        setShowError(true);
    }
  };
  const handleNewPinSubmit = () => {
    if (pinStep === "new") {
      if (newPin.filter(Boolean).length === 5) {
        setPinStep("confirm");
      } else {
        setShowError(true);
      }
    } else {
      if (confirmPin.filter(Boolean).length === 5) {
        if (newPin.join("") === confirmPin.join("")) {
          setShowForgotPinForm(false);
          setNewPin(Array(5).fill(""));
          setConfirmPin(Array(5).fill(""));
          setNewPinIndex(0);
          setConfirmPinIndex(0);
          setPinStep("new");
          alert("PIN successfully updated!");
        } else {
          setShowError("PINs do not match. Please try again.");
          setConfirmPin(Array(5).fill(""));
          setConfirmPinIndex(0);
        }
      } else {
        setShowError(true);
      }
    }
  };
  useEffect(() => {
    setTimeout(() => {
      setError('')
    }, 2000);
  },[error])
  const handleClose = () => {
    close(false);
  };
  
  return (
    <div className="min-h-screen bg-gray-00 flex items-center justify-center">
      {(
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-30">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-4 relative">
            {/* Close button */}
            <button
              onClick={handleClose}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 cursor-pointer !rounded-button whitespace-nowrap"
            >
              <i className="fas fa-times text-xl"></i>
            </button>
            {/* Header */}
            <div className="flex flex-col items-center mb-4">
              <div className="text-blue-500 mb-2">
                <i className="fas fa-lock text-2xl"></i>
              </div>
              <h2 className="text-xl font-semibold text-gray-800">
                Enter Your PIN
              </h2>
              <p className="text-gray-500 text-sm mt-1">
                Please enter your 5-digit security PIN
              </p>
            </div>
            {/* PIN display */}
            <div className="flex justify-center space-x-3 mb-4">
              {Array(5)
                .fill(0)
                .map((_, index) => (
                  <div
                    key={index}
                    className={`w-10 h-10 flex items-center justify-center border  ${
                      index === currentIndex - 1
                        ? "border-blue-500 bg-blue-50"
                        : index < currentIndex
                        ? "border-gray-300 bg-gray-50"
                        : "border-gray-300"
                    } rounded-md text-lg font-medium`}
                  >
                    {pin[index] ? " * " : ""}
                  </div>
                ))}
            </div>
            {showError && (
              <div className="text-red-500 text-sm text-center mt-2 mb-4">
                Please enter all 5 digits of your PIN
              </div>
            )}
            {!error &&
              <div className="w-full text-red-500 text-sm text-center mt-2 mb-4">
              {/* {error} */} Abubakar 
              </div>
            }
            {/* Number pad */}
            <div className="grid grid-cols-3 gap-2 mb-2">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((number) => (
                <button
                  key={number}
                  onClick={() => handleNumberClick(number)}
                  className="w-full h-12 bg-gray-100 rounded-lg text-gray-800 text-xl font-medium hover:bg-gray-200 transition-colors duration-200 cursor-pointer !rounded-button whitespace-nowrap"
                >
                  {number}
                </button>
              ))}
              <div className="col-start-2">
                <button
                  onClick={() => handleNumberClick(0)}
                  className="w-full h-12 bg-gray-100 rounded-lg text-gray-800 text-xl font-medium hover:bg-gray-200 transition-colors duration-200 cursor-pointer !rounded-button whitespace-nowrap"
                >
                  0
                </button>
              </div>
              <button
                onClick={() => {
                  if (currentIndex > 0) {
                    const newPin = [...pin];
                    newPin[currentIndex - 1] = "";
                    setPin(newPin);
                    setCurrentIndex(currentIndex - 1);
                  }
                }}
                className="w-full h-12 bg-gray-100 rounded-lg text-gray-800 text-xl font-medium hover:bg-gray-200 transition-colors duration-200 cursor-pointer !rounded-button whitespace-nowrap"
              >
                <i className="fas fa-backspace"></i>
              </button>
            </div>
            {/* Forgot PIN link */}
            <div className="text-center mb-4">
              <button
                onClick={() => {
                  setShowForgotPinForm(true);
                  setShowError(false);
                }}
                className="text-blue-500 hover:text-blue-600 text-sm font-medium !rounded-button whitespace-nowrap"
              >
                Forgot PIN?
              </button>
            </div>
            {showForgotPinForm && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-4 relative">
                  <button
                    onClick={() => {
                      setShowForgotPinForm(false);
                      setNewPin(Array(5).fill(""));
                      setConfirmPin(Array(5).fill(""));
                      setNewPinIndex(0);
                      setConfirmPinIndex(0);
                      setPinStep("new");
                      setShowError(false);
                    }}
                    className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 cursor-pointer !rounded-button whitespace-nowrap"
                  >
                    <i className="fas fa-times text-xl"></i>
                  </button>
                  <div className="flex flex-col items-center mb-4">
                    <div className="text-blue-500 mb-2">
                      <i className="fas fa-key text-2xl"></i>
                    </div>
                    <h2 className="text-xl font-semibold text-gray-800">
                      {pinStep === "new" ? "Create New PIN" : "Confirm New PIN"}
                    </h2>
                    <p className="text-gray-500 text-sm mt-1">
                      {pinStep === "new"
                        ? "Please enter your new 5-digit PIN"
                        : "Please confirm your new PIN"}
                    </p>
                  </div>
                  <div className="flex justify-center space-x-3 mb-4">
                    {Array(5)
                      .fill(0)
                      .map((_, index) => (
                        <div
                          key={index}
                          className={`w-10 h-10 flex items-center justify-center border ${
                            pinStep === "new"
                              ? index === newPinIndex - 1
                                ? "border-blue-500 bg-blue-50"
                                : index < newPinIndex
                                  ? "border-gray-300 bg-gray-50"
                                  : "border-gray-300"
                              : index === confirmPinIndex - 1
                                ? "border-blue-500 bg-blue-50"
                                : index < confirmPinIndex
                                  ? "border-gray-300 bg-gray-50"
                                  : "border-gray-300"
                          } rounded-md text-lg font-medium`}
                        >
                          {pinStep === "new"
                            ? newPin[index]
                              ? "*"
                              : ""
                            : confirmPin[index]
                              ? "*"
                              : ""}
                        </div>
                      ))}
                  </div>
                  {showError && (
                    <div className="text-red-500 text-sm text-center mt-2 mb-4">
                      Please enter all 5 digits of your PIN
                    </div>
                  )}
                  <div className="grid grid-cols-3 gap-3 mb-2">
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((number) => (
                      <button
                        key={number}
                        onClick={() => {
                          if (pinStep === "new" && newPinIndex < 5) {
                            const newPinArray = [...newPin];
                            newPinArray[newPinIndex] = number.toString();
                            setNewPin(newPinArray);
                            setNewPinIndex(newPinIndex + 1);
                          } else if (
                            pinStep === "confirm" &&
                            confirmPinIndex < 5
                          ) {
                            const confirmPinArray = [...confirmPin];
                            confirmPinArray[confirmPinIndex] =
                              number.toString();
                            setConfirmPin(confirmPinArray);
                            setConfirmPinIndex(confirmPinIndex + 1);
                          }
                        }}
                        className="w-full h-14 bg-gray-100 rounded-lg text-gray-800 text-xl font-medium hover:bg-gray-200 transition-colors duration-200 cursor-pointer !rounded-button whitespace-nowrap"
                      >
                        {number}
                      </button>
                    ))}
                    <div className="col-start-2">
                      <button
                        onClick={() => {
                          if (pinStep === "new" && newPinIndex < 5) {
                            const newPinArray = [...newPin];
                            newPinArray[newPinIndex] = "0";
                            setNewPin(newPinArray);
                            setNewPinIndex(newPinIndex + 1);
                          } else if (
                            pinStep === "confirm" &&
                            confirmPinIndex < 5
                          ) {
                            const confirmPinArray = [...confirmPin];
                            confirmPinArray[confirmPinIndex] = "0";
                            setConfirmPin(confirmPinArray);
                            setConfirmPinIndex(confirmPinIndex + 1);
                          }
                        }}
                        className="w-full h-14 bg-gray-100 rounded-lg text-gray-800 text-xl font-medium hover:bg-gray-200 transition-colors duration-200 cursor-pointer !rounded-button whitespace-nowrap"
                      >
                        0
                      </button>
                    </div>
                    <button
                      onClick={() => {
                        if (pinStep === "new" && newPinIndex > 0) {
                          const newPinArray = [...newPin];
                          newPinArray[newPinIndex - 1] = "";
                          setNewPin(newPinArray);
                          setNewPinIndex(newPinIndex - 1);
                        } else if (
                          pinStep === "confirm" &&
                          confirmPinIndex > 0
                        ) {
                          const confirmPinArray = [...confirmPin];
                          confirmPinArray[confirmPinIndex - 1] = "";
                          setConfirmPin(confirmPinArray);
                          setConfirmPinIndex(confirmPinIndex - 1);
                        }
                      }}
                      className="w-full h-14 bg-gray-100 rounded-lg text-gray-800 text-xl font-medium hover:bg-gray-200 transition-colors duration-200 cursor-pointer !rounded-button whitespace-nowrap"
                    >
                      <i className="fas fa-backspace"></i>
                    </button>
                  </div>
                  <button
                    onClick={handleNewPinSubmit}
                    className="w-full py-3 bg-blue-500 text-white rounded-lg text-base font-medium hover:bg-blue-600 transition-colors duration-200 cursor-pointer !rounded-button whitespace-nowrap"
                  >
                    {pinStep === "new" ? "Continue" : "Create PIN"}
                  </button>
                </div>
              </div>
            )}
            {/* Submit button */}
            <button
              onClick={handleSubmit}
              className="w-full py-3 bg-blue-500 text-white rounded-lg text-base font-medium hover:bg-blue-600 transition-colors duration-200 cursor-pointer !rounded-button whitespace-nowrap"
            >
              Submit
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
export default StaffPins;
