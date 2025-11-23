const LoginTab = (verificationSent,logindetails,setLoginDetails,showPassword,setShowPassword,setShowForgotPassword,showForgotPassword) => {
    return ( 
         <div className="space-y-2">
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <i className="fas fa-envelope text-blue-400"></i>
                        </div>
                        <input
                        readOnly={verificationSent}
                        value={logindetails.username_field}
                        onChange={(e) => {
                          setLoginDetails((prev) => ({
                             ...prev,
                             username_field: e.target.value
                           }));
                          }}
                          type="text"
                          className="w-full  bg-opacity-20 border-none text-blue-900 placeholder-blue-00 pl-10 pr-2 py-3 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none text-sm font-medium"
                          placeholder="Email or Username or phone number "
                        />
                      </div>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <i className="fas fa-lock text-blue-400"></i>
                        </div>
                        <input
                        readOnly={verificationSent}
                        value={logindetails.password}
                        onChange={(e) => setLoginDetails((prev) => ({
                          ...prev,password:e.target.value
                        }))}
                        maxLength={'15'}
                        minLength={'8'}
                          type={showPassword ? "text" : "password"}
                          className="w-full  bg-opacity-20 border-none text-blue-900 placeholder-blue-00 pl-10 pr-4 py-3 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none text-sm font-medium"

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
                      {verificationSent && (
                        <div className="space-y-2">
                          <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                              <i className="fas fa-key text-blue-400"></i>
                            </div>
                            <div className="relative ">
                              <input
                              value={logindetails.otp}
                                onChange={(e) => setLoginDetails((prev) => ({
                                  ...prev,otp:e.target.value
                                }))}
                                maxLength={'15'}
                                minLength={'8'}
                                type="text"
                                className="w-full bg-white bg-opacity-25 border-none font-medium pl-10 pr-4 py-3 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none text-sm"
                                placeholder="Enter Email Verification Code Sent"
                              />
                              {resendIn === 0  && <span className="absolute rounded-full text-xs right-2 bg-gray-800 text-white hover:bg-opacity-70 px-1 top-1/2 transform -translate-y-1/2 "
                              onClick={() => {
                                c(30);
                                c();
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
                      <div className="text-right">
                        <button
                          onClick={() => setShowForgotPassword(true)}
                          className="text-sm text-blue-100 hover:text-white transition-colors"
                        >
                          Forgot Password?
                        </button>
                      </div>

                      {showForgotPassword && (
                        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
                          <div className="bg-white rounded-lg p-6 w-96 relative">
                            <button
                              onClick={() => setShowForgotPassword(false)}
                              className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
                            >
                              <i className="fas fa-times"></i>
                            </button>
                            <h3 className="text-xl font-semibold text-gray-800 mb-4">
                              Reset Password
                            </h3>
                            <p className="text-gray-600 mb-4">
                              Enter your registered email address and we'll send you a link
                              to reset your password. Check your spam folder if you did not receive the link 
                            </p>
                            <div className="relative mb-4">
                              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <i className="fas fa-envelope text-gray-400"></i>
                              </div>
                              <input
                                type="email"
                                value={resetEmail}
                                onChange={(e) => setResetEmail(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-400 focus:outline-none"
                                placeholder="Enter your email"
                              />
                            </div>
                            <button
                              className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors !rounded-button"
                              onClick={() => {
                                alert(
                                  "Password reset link sent to your email!",
                                );
                                setShowForgotPassword(false);
                              }}
                            >
                              Send Reset Link
                            </button>
                          </div>
                        </div>
                      )}
                      <button 
                      onClick={handleLogin}
                      className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-3 px-4 rounded-lg transition-colors cursor-pointer whitespace-nowrap !rounded-button">
                        Login
                      </button>
                      <div className="relative flex items-center justify-center my-6">
                        <div className="border-t border-blue-200 border-opacity-30 absolute w-full"></div>
                        <span className="bg-blue-500 bg-opacity-50 text-blue-100 text-xs px-3 relative rounded-lg">
                          Or continue with
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <button
                          id="googleLoginBtn"
                          onClick={handleGoogleLogin}
                          className="flex items-center justify-center bg-gray-900 bg-opacity-40 border backdrop-blur-md hover:bg-opacity-20 text-white py-2 px-4 rounded-lg transition-all cursor-pointer whitespace-nowrap !rounded-button"
                        >
                          <i className="fab fa-google mr-2"></i>
                          Google
                        </button>
                        <button className="flex items-center justify-center  border bg-opacity-10 hover:bg-opacity-20 text-white py-2 px-4 rounded-lg transition-all cursor-pointer whitespace-nowrap !rounded-button">
                          <i className="fab fa-apple mr-2"></i>
                          Apple
                        </button>
                      </div>
        </div>
    );
}
 
export default LoginTab;