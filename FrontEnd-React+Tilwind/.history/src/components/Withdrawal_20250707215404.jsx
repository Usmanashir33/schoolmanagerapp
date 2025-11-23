import { ArrowLeft, ExpandIcon, LucideBanknoteArrowDown, PlusCircleIcon, RotateCw } from "lucide-react";
import { useContext, useEffect, useState } from "react";
import { useNavigate } from 'react-router-dom';
import useRequest from "../customHooks/RequestHook";
import ConfirmTrx from "./ConfirmTrx";
import Pins from "./PinsPage";
import TrxStatus from "./TrxStatus";
import { uiContext } from "../customContexts/UiContext";
import { authContext } from "../customContexts/AuthContext";
import useSendTransection from "../customHooks/SendTransection";
import { liveContext } from "../customContexts/LiveContext";


const Withdrawal = () => {
    const navigate = useNavigate();
    const {setError} = useContext(uiContext);
    const {currentUser,setCurrentUser} = useContext(authContext);
    const {setTransections} = useContext(liveContext);
    const [defaultBank, setDefaultBank] = useState();
    const {sendArbitRequest} = useRequest();
    const {sendTransectionRequest} = useSendTransection();
    const [showConfirm, setShowConfirm] = useState(false);
    const [showPin, setShowPin] = useState(false);
    const [status,setShowStatus] = useState(false);
    const [trxDetails, setTrxDetails] = useState({}); 
    const [comfirmedDetails,setConfirmedDetails] = useState({})
    const [amount, setAmount] = useState();

    const toggleConfirm = () => {
        setShowConfirm(!showConfirm);       
    }
    const togglePin = () => {
        setShowPin(!showPin);       
    }
    const getWithdrawalStatus = (data) => { 
        if (data.success === "success") {
            setCurrentUser(data.resp.user);
            setConfirmedDetails(() => ({
                "Status" : data.resp.trx?.status,
                "Amount" : data.resp.trx?.amount,
                "Bank": defaultBank?.bank_name,
                "Account Number": defaultBank?.account_number,
                "Date & Time " : data.resp.trx?.trx_date,
                "Trx Id " : data.resp.trx?.id,
            }))
            setShowStatus(true);
            toggleConfirm();  // close the windows 
            togglePin(); // close the windows 
            setAmount('')
            setTransections((prev) =>({
                prev,
                results: [data.resp.trx, ...prev?.results]
                }))
        }else {
        }
    }
    const handlesubmitwithPins = (payment_pin) => {
        let url = "/account/withdraw-money/";
        let data = {
            amount: amount,
            payment_pin: payment_pin, 
            account_number: defaultBank.account_number,
            account_name: defaultBank.account_name,
            bank_name: defaultBank.bank_name,
            bank_code: defaultBank.bank_code,
        };
        sendTransectionRequest(url,"POST",data,getWithdrawalStatus,true)

    }
    const handleSubmit = () => { 
        if (!defaultBank) {
        setError("Please select Bank to proceed or add new one.");
        return;
        }
        if (!amount || amount <= 0) {
            setError("Please enter a valid amount.");
            return;
        }
        if (amount < 50 || amount > 5000) {
        setError("Amount must be between 100 and 5000.");
        return;
        }
        if (Number(amount) > Number(currentUser.account.account_balance)) {
        setError("Insufficient balance.");
        return;
        }
        // Handle withdrawal submission logic here
        setTrxDetails((prev) => ({
            ...prev,
            "Amount": amount,
            "Bank": defaultBank?.bank_name,
            "Account Number": defaultBank?.account_number,
            "Account Name": defaultBank?.account_name,
        }));
        toggleConfirm()
    };
    const grabBankData = (data) => {
        const defaultBank = data?.accounts?.find((bank) => bank.is_default);
        setDefaultBank(defaultBank);
  }
    useEffect(() => {
    // tetch banks data
    const url = '/account/getting_withdrowal_acc/'
    sendArbitRequest(url,"GET",null,grabBankData)
  },[])
    return ( 
        // {/* Add New Bank Account */}
        <div className="h-full relative ">
          <div className=" flex-col bg-white rounded-2xl shadow-md p-2 items-center ">
            {/* header  */}
            <div className="bg-white sticky top-0 z-20 border-b w-full   ">
                <div className=" flex gap-3  items-center ">
                        <ArrowLeft
                            onClick={() => navigate(-1)}
                            className="text-xl mb-2 w-5 hover:text-yellow-600 transition-colors duration-200"
                        />
                        <h3 className="text-sm font-medium text-gray-800 mb-2">
                        Withdraw
                        </h3>
                </div>
            </div>
            {/* main */}
            <div className="p-2">
                
                    <form className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-600 mb-1">
                            Amount
                            </label>
                            <div className="relative">
                            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
                                ₦
                            </span>
                            <input
                            value={amount}
                                onChange={(e) => setAmount(e.target.value)}
                                type="number"
                                placeholder="0.00"
                                className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm bg-gray-50"
                            />
                            <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-xs text-gray-400">
                                NGN
                            </span>
                            </div>
                        </div>

                        <div className="mt-2 bg-white rounded-2xl shadow-md px-2 py-2 transform transition-all duration-300 ease-in-out hover:shadow-lg">
                            <div className="text-md font-medium text-gray-700 mb-2 flex justify-between">
                                <span>Withdrawal Bank </span>
                                <RotateCw 
                                className="hover:bg-gray-100 hover:py-2 p-1 rounded-full text-green-400"
                                onClick={() => navigate('/payment-meth')}
                                />
                            </div>
                            {/* selected bank  */}
                            {defaultBank && <div
                                className=" relative bg-whiterounded-lg border border-gray-200 p-4 hover:shadow-md transition-all duration-300 rounded-lg"
                            >
                                <div className="absolute top-0 text-xs bg-green-100 px-2 text-green-900 rounded-full"> Default</div>
                                <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-4">
                                    <div className="flex-shrink-0">
                                    <i className="fas fa-university text-green-700 text-2xl"></i>
                                    </div>
                                    <div>
                                    <div className="flex items-center">
                                        <span className="font-medium text-gray-800">
                                        {`${defaultBank?.bank_name} ••••
                                        ${
                                            defaultBank?.account_number?.slice(-4)
                                        }`}
                                            
                                        </span>
                                    </div>
                                    
                                    <div className="text-medium font-medium text-gray-500 ">
                                        {defaultBank?.account_name}
                                    </div>
                                    </div>
                                </div>
                                </div>
                            </div>}
                            {!defaultBank && <div className="flex justify-center items-center font-medium text-gray-500 mt-2">
                                No Bank Account Selected
                                <button
                                    type="button"
                                    className="text-blue-500 hover:text-blue-700 ml-2"
                                    onClick={() => navigate('/payment-meth')}
                                >
                                    <PlusCircleIcon className="inline-block mr-1" />
                                </button>
                            </div>}

                        </div>
                        <button
                            onClick={(e) => {
                                e.preventDefault();
                                handleSubmit();
                            }}
                            type="button"
                            className="w-full bg-indigo-700 text-white hover:opacity-90 py-2 px-4 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2 !rounded-button whitespace-nowrap"
                        >
                            <div className="flex gap-2">
                                < LucideBanknoteArrowDown/>
                                <span>Withdraw</span>
                            </div>
                        
                        </button>
                    </form>
            </div>
            </div>
            {showConfirm && <ConfirmTrx close={toggleConfirm} confirmWithpins={togglePin} trxDetails={trxDetails} mode={'Withdraw'}/>}
           {showPin && <Pins close={togglePin}  triggerFunc={handlesubmitwithPins}/>}
            {status && <TrxStatus close={setShowStatus} trxDetails={comfirmedDetails} />}

        </div>
    );
}
 
export default Withdrawal;