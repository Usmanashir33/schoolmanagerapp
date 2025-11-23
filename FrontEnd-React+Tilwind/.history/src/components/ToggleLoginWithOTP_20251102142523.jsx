import React, { useContext, useState } from "react";
import { ShieldCheck, AlertTriangle, X, Check } from "lucide-react";
import { authContext } from "../customContexts/AuthContext";

const ToggleLoginWithOTP = ({closePopup}) => {
  const [otpEnabled, setOtpEnabled] = useState(false);
  const [confirmVisible, setConfirmVisible] = useState(false);
  const {currentUser} = useContext(authContext);

  const handleToggle = () => {
    setConfirmVisible(true);
  };

  const handleProceed = () => {
    setOtpEnabled(!otpEnabled);
    setConfirmVisible(false);
    // ⚡️ Trigger your backend call here
    // fetch("/api/toggle-otp", { method: "POST", body: JSON.stringify({ enabled: !otpEnabled }) })
  };
  check if current user has log with otp setting 

  return (
    <div className="absolute">
      {/* Popup Modal */}
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-xl z-10">
          <div className="bg-white rounded-2xl shadow-xl p-6 w-[90%] max-w-md animate-fadeIn relative">
            <button
              onClick={() => closePopup(false)}
              className="absolute top-3 right-3 text-gray-400 hover:text-gray-600"
            >
              <X size={20} />
            </button>

            <div className="text-center mb-4">
              <ShieldCheck className="mx-auto text-blue-600" size={48} />
              <h2 className="text-xl font-semibold text-gray-800 mt-2">
                Login with OTP
              </h2>
              <p className="text-gray-500 text-sm mt-1">
                Control whether users must verify with an OTP sent to their email before logging in.
              </p>
            </div>

            {/* Toggle Switch */}
            <div className="flex items-center justify-between border rounded-lg p-3 bg-gray-50">
              <span className="text-gray-700 font-medium">
                {otpEnabled ? "Enabled" : "Disabled"}
              </span>
              <button
                onClick={handleToggle}
                className={`relative inline-flex h-6 w-12 items-center rounded-full transition-colors ${
                  otpEnabled ? "bg-green-500" : "bg-gray-300"
                }`}
              >
                <span
                  className={`inline-block h-5 w-5 transform bg-white rounded-full transition-transform ${
                    otpEnabled ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>
            </div>

            {/* Confirmation Modal */}
            {confirmVisible && (
              <div className="mt-4 border rounded-xl bg-gray-50 p-4 text-center shadow-inner">
                {otpEnabled ? (
                  <>
                    <AlertTriangle
                      size={36}
                      className="mx-auto text-yellow-500 mb-2"
                    />
                    <p className="text-gray-700 font-medium">
                      Disabling this means users can log in directly if they know your password.
                    </p>
                  </>
                ) : (
                  <>
                    <ShieldCheck
                      size={36}
                      className="mx-auto text-blue-600 mb-2"
                    />
                    <p className="text-gray-700 font-medium">
                      Enabling this means users must verify with an OTP sent to their email.
                    </p>
                  </>
                )}

                <div className="flex justify-center gap-3 mt-4">
                  <button
                    onClick={() => setConfirmVisible(false)}
                    className="px-4 py-2 rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-100 flex items-center gap-1"
                  >
                    <X size={16} /> Cancel
                  </button>
                  <button
                    onClick={handleProceed}
                    className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 flex items-center gap-1"
                  >
                    <Check size={16} /> Proceed
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
    </div>
  );
}
export default ToggleLoginWithOTP;