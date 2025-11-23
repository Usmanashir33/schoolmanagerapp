import React, { useContext, useEffect, useState } from "react";
import useRequest from "../customHooks/RequestHook";
import { uiContext } from "../customContexts/UiContext";
const Register = () => {
  
  
  const handleLogin = () => {
    if (logindetails.username_field && logindetails.password.length >= 8) {
      login(logindetails,'/authuser/loginRequest/');
    }
  }
  const handleGoogleLogin = async () => {
    setIsLoading(true);
    try {
      const googleAuthUrl = "https://accounts.google.com/o/oauth2/v2/auth";
      const params = {
        client_id: "YOUR_GOOGLE_CLIENT_ID",
        redirect_uri: `${window.location.origin}/auth/google/callback`,
        response_type: "code",
        scope: "email profile",
        access_type: "offline",
        prompt: "consent",
      };
      const queryString = Object.entries(params)
        .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
        .join("&");
      const authUrl = `${googleAuthUrl}?${queryString}`;
      window.location.href = authUrl;
    } catch (error) {
      console.error("Google login error:", error);
    } finally {
      setIsLoading(false);
    }
  };
  const handleShowForm = (tab) => {
    setActiveTab(tab);
    setShowForm(true);
  };
  return (
    <div
      className="min-h-screen w-full flex flex-col bg-blue-600 pb-12 relative "
      style={{
        backgroundImage: `url('https://readdy.ai/api/search-image?query=Modern%20fintech%20abstract%20background%20with%20soft%20blue%20gradient%20and%20subtle%20geometric%20patterns%2C%20financial%20technology%20concept%20with%20flowing%20digital%20elements%2C%20clean%20professional%20design%20with%20light%20particle%20effects&width=1440&height=1024&seq=1&orientation=landscape')`,
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      {/* Main Content */}
      <div className="text-center">
        Register Page and login 
      </div>
    </div>
  );
};
export default Register;
