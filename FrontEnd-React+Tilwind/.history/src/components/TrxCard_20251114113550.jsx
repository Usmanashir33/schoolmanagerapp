import { useContext } from "react"
import { uiContext } from "../customContexts/UiContext"
import { useNavigate } from "react-router";
import mtnLogo from "../assets/images/mtn.jpg";
import airtelLogo from "../assets/images/airtel.png";
import gloLogo from "../assets/images/glo.png";
import nineMobileLogo from "../assets/images/9mobile.png";

const TrxCard = ({trx}) => {
    const navigate = useNavigate();
    const {getFormattedDate,formatNaira} = useContext(uiContext);
    const {
        amount,
        sender,receiver,
        net_charges,
        status,
        transaction_type,
        payment_type,trx_date} = trx
    // data r irtime purchse 
    const {
      ph
    } = trx;

    const setStatusColor = (sts) => {
        let status = sts.toLowerCase()
        return  (status === 'success' || status === 'approved')? 'bg-green-100 text-green-800' :
                (status === 'pending' || status === 'processing')? 'bg-yellow-100 text-yellow-800' :
                (status === 'failed' || status === 'cancelled')? 'bg-red-100 text-red-800' :' '
    }
    
    const RefundTrx = () => {
        return(
            <div className="flex items-center justify-between p-2 bg-gray-50
             rounded-lg cursor-pointer transform transition-all duration-300 
             hover:bg-white hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]"
                         >
                  <div className="flex items-center space-x-4 w-full">
                    <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center transition-all duration-300 group-hover:scale-110">
                      <i className="fas fa-arrow-down text-green-500 text-lg"></i>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">Refund </div>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs text-gray-500">To: Wallet</span>
                        <span className="text-xs text-gray-400">•</span>
                        <span className="text-xs text-gray-500">{getFormattedDate(trx_date)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div 

                    className="text-sm font-semibold text-green-600">+{formatNaira(amount)}</div>
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${setStatusColor(status)}`}>{status}</span>
                  </div>
            </div>          
        )
    };
    const InternalTrx = () => {
        return(
            <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg cursor-pointer transform transition-all duration-300 hover:bg-white hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]">
                  <div className="flex items-center space-x-4 w-full">
                    <div className="h-12 w-12 rounded-full bg-green-100 flex items-center justify-center transition-all duration-300 group-hover:scale-110">
                      <i className="fas fa-arrow-down text-green-500 text-lg"></i>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">Money In</div>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs text-gray-500">From: {sender?.username}</span>
                        <span className="text-xs text-gray-400">•</span>
                        <span className="text-xs text-gray-500">{getFormattedDate(trx_date)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-green-600">+{formatNaira(amount)}</div>
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${setStatusColor(status)}`}>{status}</span>
                  </div>
            </div>          
        )
    };
    const DepositeTrx = () => {
        return (
            <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg cursor-pointer transform transition-all duration-300 hover:bg-white hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]">
                  <div className="flex items-center space-x-4">
                    <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                      <i className="fas fa-piggy-bank text-blue-500 text-lg"></i>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">Bank Deposit</div>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs text-gray-500">To: Wallet</span>
                        <span className="text-xs text-gray-400">•</span>
                        <span className="text-xs text-gray-500">{getFormattedDate(trx_date)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-blue-600">+{formatNaira(amount)}</div>
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${setStatusColor(status)}`}>{status}</span>
                  </div>
            </div>
        )
    }
    const TransOutTrx = () => {
      return(
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg cursor-pointer transform transition-all duration-300 hover:bg-white hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]">
                  <div className="flex items-center space-x-4">
                    <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center">
                      <i className="fas fa-arrow-up text-red-500 text-lg"></i>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">Transfer</div>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs text-gray-500">To : {receiver?.username} </span>
                        <span className="text-xs text-gray-400">•</span>
                        <span className="text-xs text-gray-500">{getFormattedDate(trx_date)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-red-600">-{formatNaira(amount)}</div>
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${setStatusColor(status)}`}>{status}</span>
                  </div>
        </div>

      )
    }
    const WithdrawalTrx = () => {
      return (
        <div className=" flex items-center justify-between p-2 bg-gray-50 rounded-lg cursor-pointer transform transition-all duration-300 hover:bg-white hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]">
                  <div className="flex items-center space-x-4">
                    <div className="h-12 w-12 rounded-full bg-red-100 flex items-center justify-center">
                      <i className="fas fa-arrow-up text-red-500 text-lg"></i>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">Withdrawal</div>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs text-gray-500">To :{`
                        ${trx?.withdrawal_account_number.slice(0,2)}....${trx?.withdrawal_account_number.slice(-4)}
                        •(${trx?.withdrawal_bank_name})
                        `}</span>
                        <span className="text-xs text-gray-400">•</span>
                        <span className="text-xs text-gray-500">{getFormattedDate(trx_date)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-red-600">-{formatNaira(amount)}</div>
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${setStatusColor(status)}`}>{status}</span>
                  </div>
        </div>
      )
    }
    const AirtimePurchase = () => {
        return(
            <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg cursor-pointer transform transition-all duration-300 hover:bg-white hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]">
                  <div className="flex items-center space-x-4">
                    <div className="h-12 w-12 rounded-full bg-purple-100 flex items-center justify-center">
                      <i className="fas fa-phone text-purple-500 text-lg"></i>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">Airtime Purchase</div>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs text-gray-500">Phone: +1234567890</span>
                        <span className="text-xs text-gray-400">•</span>
                        <span className="text-xs text-gray-500">{getFormattedDate( )}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-red-600">-₦{formatNaira(amount)}</div>
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${setStatusColor(status)}`}>{status}</span>
                  </div>
            </div>
        )
    }
    const DataPurchase = () => {
        return (
            <div className="flex items-center justify-between p-2  bg-gray-50 rounded-lg cursor-pointer transform transition-all duration-300 hover:bg-white hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]">
                  <div className="flex items-center space-x-4">
                    <div className="h-12 w-12 rounded-full bg-indigo-100 flex items-center justify-center">
                      <i className="fas fa-wifi text-indigo-500 text-lg"></i>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">Data Purchase</div>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs text-gray-500">5GB : 816699172</span>
                        <span className="text-xs text-gray-400">•</span>
                        <span className="text-xs text-gray-500">{getFormattedDate(trx_date)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-red-600">-₦{amount}</div>
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${setStatusColor(status)}`}>{status}</span>
                  </div>
            </div>
        )
    }

    return ( 
      <>
      {/* transections  */}
              <div className="p-1 grid grid-cols-1 " onClick={() => {navigate(`/trx-status/${trx.id}`)}}>
                    {transaction_type === 'Deposite' &&  <DepositeTrx/> }
                    {transaction_type === 'Transfer-In' && <InternalTrx/>}
                    {transaction_type === 'Withdraw' &&  <WithdrawalTrx/> }
                    {transaction_type === 'Transfer-Out' &&  <TransOutTrx/>}
                    {transaction_type === 'Airtime' && <AirtimePurchase/>}
                    {transaction_type === 'Data'&&  <DataPurchase/> }
                    {transaction_type === 'Refund'&& <RefundTrx /> }
                
              </div>
            </>
    );
}
 
export default TrxCard;