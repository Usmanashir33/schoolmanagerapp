const RegTab = () => {
    return ( 
         <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="relative">
                          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <i className="fas fa-user text-blue-400"></i>
                          </div>
                          <input
                          value={registerDetails.firstName}
                          readOnly={verificationSentReg}
                          onChange={(e) => {setRegisterDetails((prev) => ({
                            ...prev,firstName:e.target.value
                          }))}}
                            type="text" 
                          className="w-full border-none pl-10 pr-4 py-3 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none text-sm font-medium"

                            placeholder="First Name"
                          />
                        </div>
                        <div className="relative">
                          <div 
                          
                          className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
                          >
                            <i className="fas fa-user text-blue-400"></i>
                          </div>
                          <input
                          value={registerDetails.lastName}
                          readOnly={verificationSentReg}
                          onChange={(e) => {setRegisterDetails((prev) => ({
                            ...prev,lastName:e.target.value
                          }))}}
                            type="text"
                            className="w-full font-medium  bg-opacity-25 border-none  pl-10 pr-4 py-3 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none text-sm"
                            placeholder="Last Name"
                          />
                        </div>
                      </div>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <i className="fas fa-phone text-blue-400"></i>
                        </div>
                        <input
                        value={registerDetails.phone_number}
                        readOnly={verificationSentReg}
                          onChange={(e) => {setRegisterDetails((prev) => ({
                            ...prev,phone_number:e.target.value
                          }))}}
                          type="tel"
                          className="w-full font-medium bg-opacity-25 border-none font-medium pl-10 pr-4 py-3 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none text-sm"
                          placeholder="Phone Number"
                        />
                      </div>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <i className="fas fa-envelope text-blue-400"></i>
                        </div>
                        <input
                        value={registerDetails.email}
                        readOnly={verificationSentReg}
                          onChange={(e) => {setRegisterDetails((prev) => ({
                            ...prev,email:e.target.value
                          }))}}
                          type="email"
                          className="w-full bg-white bg-opacity-25 border-none font-medium pl-10 pr-4 py-3 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none text-sm"
                          placeholder="Email Address"
                        />
                      </div>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <i className="fas fa-user-circle text-blue-400"></i>
                        </div>
                        <input
                        value={registerDetails.username}
                        readOnly={verificationSentReg}
                          onChange={(e) => {setRegisterDetails((prev) => ({
                            ...prev,username:e.target.value
                          }))}}
                          type="text"
                          className="w-full bg-white bg-opacity-25 border-none font-medium pl-10 pr-4 py-3 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none text-sm"
                          placeholder="Username"
                        />
                      </div>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <i className="fas fa-lock text-blue-400"></i>
                        </div>
                        <input
                        value={registerDetails.password}
                        readOnly={verificationSentReg}
                          onChange={(e) => {setRegisterDetails((prev) => ({
                            ...prev,password:e.target.value
                          }))}}
                          type={showPassword ? "text" : "password"}
                          className="w-full font-medium  bg-opacity-10 border-none  pl-10 pr-10 py-3 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none text-sm"
                          placeholder="Password"
                        />
                        <div
                          className="absolute inset-y-0 right-0 pr-3 flex items-center cursor-pointer"
                          onClick={() => setShowPassword(!showPassword)}
                        >
                          <i
                            className={`fas ${showPassword ? "fa-eye-slash" : "fa-eye"} text-blue-400`}
                          ></i>
                        </div>
                      </div>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <i className="fas fa-lock text-blue-400"></i>
                        </div>
                        <input
                        value={registerDetails.password2}
                        readOnly={verificationSentReg}
                          onChange={(e) => {setRegisterDetails((prev) => ({
                            ...prev,password2:e.target.value
                          }))}}
                          type={showConfirmPassword ? "text" : "password"}
                          className="w-full font-medium bg-opacity-10 border-noneplaceholder-blue-200 pl-10 pr-10 py-3 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none text-sm"
                          placeholder="Confirm Password"
                        />
                        <div
                          className="absolute inset-y-0 right-0 pr-3 flex items-center cursor-pointer"
                          onClick={() =>
                            setShowConfirmPassword(!showConfirmPassword)
                          }>
                            
                          <i
                            className={`fas ${showConfirmPassword ? "fa-eye-slash" : "fa-eye"} text-blue-400`}
                          ></i>
                        </div>
                      </div>
                        {verificationSentReg && (
                        <div className="space-y-2">
                          <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                              <i className="fas fa-key text-blue-400"></i>
                            </div>
                            <div className="relative">
                              <input
                                value={registerDetails.otp} 
                                onChange={(e) => {setRegisterDetails((prev) => ({
                                  ...prev,otp:e.target.value
                                }))}}
                                type="text"
                                className="w-full bg-white bg-opacity-25 border-none font-medium pl-10 pr-4 py-3 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none text-sm"
                                placeholder="Enter Email Verification Code"
                              />
                              {resendIn === 0  && <span className="absolute rounded-full text-xs right-2 bg-gray-800 text-white hover:bg-opacity-70 px-1 top-1/2 transform -translate-y-1/2 "
                              onClick={() => {
                                setResendIn(30);
                                resendOtp();
                              }}
                              >resend Otp
                              </span>}

                              {resendIn !== 0  && <span className=" absolute rounded-full text-xs right-2  text-green-900 hover:bg-opacity-70 px-1 top-1/2 transform -translate-y-1/2 "
                              >{resendIn}
                              </span>}
                            </div>
                          </div>
                          <p className="text-xs text-blue-100">
                            Verification code has been sent to your email.
                          </p>
                        </div>
                      )}

                      <div className="space-y-4">
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            id="terms"
                            checked={acceptedTerms}
                            onChange={(e) => setAcceptedTerms(e.target.checked)}
                            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <label
                            htmlFor="terms"
                            className="ml-2 text-sm text-blue-100"
                          >
                            I accept the{" "}
                            <a
                              href="#"
                              className="text-blue-300 hover:text-white"
                            >
                              Terms of Service
                            </a>{" "}
                            and{" "}
                            <a
                              href="#"
                              className="text-blue-300 hover:text-white"
                            >
                              Privacy Policy
                            </a>
                          </label>
                        </div>
                        {!registerRedirectUrl && <button
                          id="signUpButton"
                          onClick={async () => {
                            if (!acceptedTerms) return;

                            setIsLoading(true);
                            const firstName = (
                              document.querySelector(
                                'input[placeholder="First Name"]',
                              ) 
                            )?.value;
                            const lastName = (
                              document.querySelector(
                                'input[placeholder="Last Name"]',
                              )
                            )?.value;
                            const phone = (
                              document.querySelector(
                                'input[placeholder="Phone Number"]',
                              )
                            )?.value;
                            const email = (
                              document.querySelector(
                                'input[placeholder="Email Address"]',
                              ) 
                            )?.value;
                            const username = (
                              document.querySelector(
                                'input[placeholder="Username"]',
                              )
                            )?.value;
                            const password = (
                              document.querySelector(
                                'input[placeholder="Password"]',
                              ) 
                            )?.value;
                            const confirmPassword = (
                              document.querySelector(
                                'input[placeholder="Confirm Password"]',
                              ) 
                            )?.value;

                            // Validation
                            const errors = [];
                            if (!firstName)
                              errors.push("First Name is required");
                            if (!lastName) errors.push("Last Name is required");
                            if (!phone) errors.push("Phone Number is required");
                            if (!email)
                              errors.push("Email Address is required");
                            if (!username) errors.push("Username is required");
                            if (!password) errors.push("Password is required");
                            if (password !== confirmPassword)
                              errors.push("Passwords do not match");
                            if (password && password.length < 8)
                              errors.push(
                                "Password must be at least 8 characters",
                              );
                            if (
                              email &&
                              !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
                            )
                              errors.push("Invalid email format");

                            if (errors.length > 0) {
                              const errorMessage = errors.join("\n");
                              const errorDiv = document.createElement("div");
                              errorDiv.className =
                                "fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50";
                              errorDiv.textContent = errorMessage;
                              document.body.appendChild(errorDiv);
                              setTimeout(() => errorDiv.remove(), 2000);
                              setIsLoading(false);
                              return;
                            }

                            try {
                              // Simulate API call
                              // register 
                              register(registerDetails);
                            } catch (error) {
                              console.error("Registration error:", error);
                            } finally {
                              setIsLoading(false);
                            }
                          }}
                          className={`w-full ${acceptedTerms ? "bg-blue-500 border hover:bg-blue-600" : "bg-blue-900 cursor-not-allowed"} text-white font-medium py-3 px-4 rounded-lg transition-colors whitespace-nowrap !rounded-button relative`}
                          readOnly={!acceptedTerms || isLoading}
                        >
                          {isLoading ? (
                            <div className="flex items-center justify-center ">
                              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-2"></div>
                              Processing...
                            </div>
                          ) : (
                            "Sign Up"
                          )}
                        </button>}

                        {registerRedirectUrl && <button
                          id="signUpButton"
                          onClick={() => {completeRegisterAccount(registerDetails,registerRedirectUrl),console.log(registerRedirectUrl);}}
                          className={`bbd w-full ${acceptedTerms ? "bg-blue-500 border hover:bg-blue-600" : "bg-blue-900 cursor-not-allowed"} text-white font-medium py-3 px-4 rounded-lg transition-colors whitespace-nowrap !rounded-button relative`}
                          readOnly={!acceptedTerms || isLoading}
                        >
                          {isLoading ? (
                            <div className="flex items-center justify-center ">
                              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-2"></div>
                              Processing...
                            </div>
                          ) : (
                            "Complete Registration"
                          )}
                        </button>}
                      </div>
        </div>
     );
}
 
export default RegTab;