import { faMultiply } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome" ;
import {  AlignCenter, ArrowLeft, CheckCircle,HandCoins,  } from "lucide-react" ;

import { useContext, useEffect, useState } from "react" ;
// import { useNavigation } from "react-router";
import { useNavigate } from 'react-router-dom';
import useSearchRequest from "../customHooks/SearchRequest" ;
import { authContext } from "../customContexts/AuthContext" ;
import { uiContext } from "../customContexts/UiContext";
import config from "../customHooks/ConfigDetails" ;
import ConfirmTrx from "./ConfirmTrx" ;
import Pins from "./PinsPage";
import useSendTransection from "../customHooks/SendTransection" ;
import TrxStatus from "./TrxStatus" ;
import {liveContext} from "../customContexts/LiveContext" ;

const SendingMoney = () => {
    const navigate = useNavigate();
    const {sendSearchRequest} = useSearchRequest();
    const {sendTransectionRequest} = useSendTransection();

    const {currentUser,setCurrentUser} = useContext(authContext);
    const {setTransections} = useContext(liveContext);
    const {setError} = useContext(uiContext);
    const [showPins,setShowPins]= useState(false);
    const [showTrxStatus,setShowTrxStatus]= useState(false);
    const [showConfirm,setShowConfirm]= useState(false);
    const [confirmedDetails,setConfirmedDetails] = useState({})

    const [formData, setFormData] = useState({
      validRecipient: false,
      receiver: {},
      transMode : '',
      amount: "",
      note: "",
  });
    const togglePins = () => {
      setShowPins(!showPins)
    }
    const toggleConfirm = () => {
      setShowConfirm(!showConfirm);
    }
    const toggleTrxStatus = () => {
      setShowTrxStatus(!showTrxStatus);
    }
    const [showReceipients,setShowReciepient ] = useState(false)
    const [recipients,setrecipients] = useState([])
    const [receiver,setReceiver] = useState('');
    const [transMode,setTransMode] = useState('sending')

    const toggleShowrecipients = () => {
        setShowReciepient(!showReceipients)
    }

    const grabResentRecipients = (data) => {
      setrecipients(data?.data)
    }

    const fetchRecentRecipients = () => {
      if (!showReceipients){
        const url = "/account/recent_recipients/"
        sendSearchRequest(url,"GET",'',grabResentRecipients,)
      }
    }

    const selectReceipient = (parson) => {
        setReceiver(parson)
        setFormData((prev) => ({
          ...prev,receiver:parson,validRecipient:true
        }))
        toggleShowrecipients()
    }

    const getPaymentStatus = (data) => {
    if (data.success){
      const {trx,user} = data.data;
      setCurrentUser(user);
      setConfirmedDetails((prev) => ({
        "Status" : trx?.status,
        "Amount" : trx?.amount,
        "Recipient" : formData.receiver?.username,
        "Date & Time " : trx?.trx_date,
        "Trx Id " : trx?.id,
      }))
      toggleTrxStatus();
      toggleConfirm();  // close the windows 
      togglePins(); // close the windows 
      setReceiver('')
      setrecipients([])
      setFormData({
          validRecipient: false,
          receiver: {},
          transMode : '',
          amount: "",
          note: "",
      })
      // setTransections([trx,...transections]);
      setTransections((prev) =>({
          ...prev,
          results: [trx, ...prev?.results]
        }))
    }
  }
  const initiatePayment = (payment_pins) => {
    let url = "/account/send-money/";
    let data = {
      amount: formData.amount,
      note: formData.note, 
      recipient: formData?.receiver?.id,
      payment_pin: payment_pins,
    };
    sendTransectionRequest(url,"POST",data,getPaymentStatus,true)
  }
    const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData?.validRecipient){
      setError('Invalid Recipient')
      return
    }
    if (Number(formData?.amount) > Number(currentUser.account.account_balance)){
      setError('Insufficient Balance !')
      return
    }
    if (formData?.receiver.id === currentUser.id){
      setError('You can not make transfer to your self!')
      return
    }
    setConfirmedDetails((prev) => ({
      "Recipient Username" : formData.receiver?.username,
      "Recipient Email" : formData.receiver?.email,
      "Amount" : formData?.amount,
      "Note" : formData?.note,
    }))
    toggleConfirm();
  };
  
  const checkValidRecipient = (data) => {
    if (data.error){ 
      setFormData((prev) => ({
        ...prev,validRecipient:false,receiver:{}
      }) )
    } else {
      setFormData((prev) => ({
        ...prev,validRecipient:true,receiver:data
      }) )
    }
  }

  useEffect(() => {
    if (receiver.length >= 5){
      let waiting = 500 // seconds
      setTimeout(() => {
        let search = receiver
        const url = "/authuser/search-user/"
        sendSearchRequest(url,"POST",{search},checkValidRecipient)
      }, waiting);
    }else if (receiver.length < 5){ // remove ui validation
      setFormData((prev) => ({
        ...prev,validRecipient:false,receiver:{}
      }) )
    }
  },[receiver])
    return ( 
         <div className=" relative ">
          {/* Make a Transaction */}
          {(showConfirm || showPins || showTrxStatus) && <div className={`w-full  h-full  absolute z-10 transition-all duration-500 ease-in-out transform ${
          (showPins || showConfirm || showTrxStatus)
            ? "opacity-100 scale-100 translate-y-0"
            : "opacity-0 scale-95 -translate-y-4 "
            } bg-white shadow-lg `}>
            {showConfirm && <ConfirmTrx 
              close={toggleConfirm}
              confirmWithpins={togglePins}
              trxDetails={confirmedDetails}
              mode={transMode==='sending'? "Transfer":"Request"}
            />}
            {showPins && <Pins 
              close={togglePins}
              triggerFunc={initiatePayment}
            />}
            {showTrxStatus && <TrxStatus 
              close={toggleTrxStatus}
              trxDetails={confirmedDetails}
            />}
          </div>}
          <div className="  bg-white relative  rounded-md shadow-md  px-4 py-2 ">
            <div className="absolute top-0  flex justify-between items-center ">
                <ArrowLeft
                  onClick={() => navigate(-1)}
                 className="text-xl mb-4  hover:text-yellow-600 transition-colors duration-200"
                />
                
            </div>
            <div className="flex space-x-2 mb-3  mt-5 ">
              <button
                onClick={() => setTransMode('sending')}
               className={`flex-1 ${transMode=== 'sending'? "bg-indigo-600 text-white ":'bg-gray-100 text-gray-800'} py-2 px-4 rounded-lg !rounded-button whitespace-nowrap`}>
                Send
              </button>
              <button
                onClick={() => setTransMode('requesting')}
               className={`flex-1 ${transMode=== 'requesting'? "bg-indigo-600 text-white ":'bg-gray-100 text-gray-800'} py-2 px-4 rounded-lg !rounded-button whitespace-nowrap`}>
                Request 
              </button>
            </div>

            <form className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">
                  <span className="flex items-center gap-2  ">
                    {formData.validRecipient   &&
                    <div className="flex items-center gap-2 ">
                      <CheckCircle className="w-4 h-4 text-green-600" />
                      <span>Recipient</span>
                      {formData?.receiver?.username && <span className="text-green-600">{`(${formData?.receiver?.username})`} </span>}
                    </div>
                     }
                    
                  </span>
                  {!formData.validRecipient && <span>Recipient</span>}
                </label>
                <div className="relative">
                  <input
                  value={receiver?.username }
                  onChange={(e) => {setReceiver(e.target.value)}}
                    type="text"
                    required
                    placeholder="Search by name or username"
                    className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm pr-32 bg-gray-50"
                  />
                  <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                  ></i>
                  <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex space-x-2">
                    {/* <Users2/> */}
                    <button type="button"
                    onClick={() => {
                      fetchRecentRecipients(); 
                      toggleShowrecipients();
                    }}
                     className=" text-blue-400 hover:text-indigo-600 transition-colors duration-200">
                      <i className="fas fa-users"></i>
                    </button>
                  </div>
                </div>

                {/* Recent Recipients */}
                {showReceipients && <div className=" mt-2 bg-white rounded-lg border border-gray-200 shadow-sm">
                  <div className="p-3 border-b border-gray-100">
                    <span className="flex justify-between ">
                        <h4 className="text-sm font-medium text-gray-700">
                        Recent Recipients
                        </h4>
                        <FontAwesomeIcon icon={faMultiply}
                        onClick={toggleShowrecipients}
                            className="text-xl mb-4 text-gray-700 hover:text-yellow-600 transition-colors duration-200"
                    />
                    </span>
                  </div>
                  <div className="divide-y divide-gray-100  overflow-y-auto h-50">
                    {recipients && recipients.map((parson,index) => 
                      <div
                      key={`${index}${parson.id}`}
                          onClick={() => {
                              selectReceipient(parson)
                          }}
                      className="p-3 flex items-center justify-between hover:bg-gray-50 cursor-pointer transition-colors duration-200">
                        <div className="flex items-center space-x-3">
                          <img
                          src = {`${config.BASE_URL}${parson.picture}`}
                            alt="User"
                            className="w-10 h-10 rounded-full object-cover border"
                          />
                          <div>
                            <p className="text-sm font-medium text-gray-800">
                              {parson.first_name} {parson.last_name}
                            </p>
                            <p className="text-xs text-gray-500">@{parson.username}</p>
                          </div>
                        </div>
                        <span className="text-xs text-gray-500">
                          Last sent: 2 days ago
                        </span>
                      </div>
                    )}
                    {!recipients && <div className="flex text-gray-900 opacity-10">
                      No data recorded
                    </div>}
                  </div>
                </div>}

              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">
                  Amount
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                    ₦
                  </span>
                  <input
                  value={formData?.amount}
                  onChange={(e) => {
                    setFormData((prev) => ({
                      ...prev,amount:e.target.value
                    }))
                  }}
                    type="number"
                    required
                    placeholder="0.00"
                    className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm bg-gray-50"
                  />
                  <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-xs text-gray-400">
                    NGN
                  </span>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">
                  Note (Optional)
                </label>
                <div className="relative">
                  <textarea
                  value={formData?.note}
                  onChange={(e) => {
                    setFormData((prev) => ({
                      ...prev,note:e.target.value
                    }))
                  }}
                    placeholder="Add a note about this transaction"
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm bg-gray-50 pr-10"
                  ></textarea>
                  <i className="fas fa-sticky-note absolute right-3 top-3 text-gray-400"></i>
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  Maximum 100 characters
                </p>
              </div>
              <button
                type="button"
                className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2 !rounded-button whitespace-nowrap"
              >
                {transMode === 'sending' ?
                    (<div onClick={(e) => {
                      handleSubmit(e)
                    }}>
                         <i className="fas fa-paper-plane"></i>
                        <span>Send Money</span>
                    </div>)
                :

                (<div className="flex " onClick={(e) => {
                  handleSubmit(e)
                }}>
                    < HandCoins/>
                    <span>Request Money</span>
                </div>)
                }
               
              </button>
            </form>
          </div>
        </div>
    );
}
 
export default SendingMoney;