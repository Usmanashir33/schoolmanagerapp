import { useContext } from "react";
import { uiContext } from "../customContexts/UiContext";
import { TrashIcon } from "lucide-react";
import { liveContext } from "../customContexts/LiveContext";

const NotifCard = ({notification}) => {
    const {getFormattedDate} = useContext(uiContext);
    const {sendRequest} = useContext(liveContext);
    const {id,type,title,body,date} = notification ;

    const Alert = () => {
      return (
        <>
              {/* <TrashIcon className="absolute right-0 w-4 h-4 text-red-700 hover:opacity-9 hover:bg-gray-200 rounded-lg" 
                onClick={() => {sendRequest(`/account/delete_notif/${id}/`,'DELETE',null)}}
              /> */}
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-yellow-100 flex items-center justify-center">
                  <i className="fas fa-bell text-yellow-500"></i>
                </div>
                <div className="ml-3 flex-1">
                  <p className="text-sm font-medium text-gray-900">{title}</p>
                  <p className="text-sm text-gray-500">{body}</p>
                  <p className="mt-1 text-xs text-gray-400">{getFormattedDate(date)}</p>
                </div>
              </div>
          </>

      )
    }
    const Debit = () => {
      return (
         <div className="p-4 hover:bg-gray-50 relative " key={id}>
              {/* <TrashIcon className="absolute right-0 w-4 h-4 text-red-700 hover:opacity-9 hover:bg-gray-200 rounded-lg" 
                onClick={() => {sendRequest(`/account/delete_notif/${id}/`,'DELETE',null)}}
              /> */}
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                  <i className="fas fa-check text-green-500"></i>
                </div>
                <div className="ml-3 flex-1">
                  <p className="text-sm font-medium text-gray-900">{title}</p>
                  <p className="text-sm text-gray-500">{body}</p>
                  <p className="mt-1 text-xs text-gray-400">{getFormattedDate(date)}</p>
                </div>
              </div>
        </div>
      )
    }
    const Credit = () => {
      return (
        <div className="p-4 mb-1 hover:bg-gray-50 border-gray-100 border relative" key={id}>
          {/* <TrashIcon className="absolute right-0 w-4 h-4 text-red-700 hover:opacity-9 hover:bg-gray-200 rounded-lg" 
          onClick={() => {sendRequest(`/account/delete_notif/${id}/`,'DELETE',null)}}
          /> */}
              <div className="flex items-start ">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                  <i className="fas fa-money-bill text-blue-500"></i>
                </div>
                <div className="ml-3 flex-1">
                  <p className="text-sm font-medium text-gray-900">{title}</p>
                  <p className="text-sm text-gray-500">{body}</p>
                  <p className="mt-1 text-xs text-gray-400">{getFormattedDate(date)}</p>
                </div>
              </div>
          </div>
      )
    }
    
    return ( 
        <>
          <div className="divide- ">
            {type === "success" && <Credit />}
            {type === "promotion" && <Debit />}
            {type === "info" && <Alert />} 
          </div>
        </>
     );
}
 
export default NotifCard;