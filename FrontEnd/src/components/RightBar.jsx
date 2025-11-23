import { useContext, useEffect, useState, } from "react";
import { liveContext } from "../customContexts/LiveContext";
import {LucideTrash2, Trash } from "lucide-react";
import { uiContext } from "../customContexts/UiContext";

const Rightbar = () => {
    const {notifications,sendRequest} = useContext(liveContext);
    const [deleteAll,setShowDeleteAll] = useState(false);
    
    useEffect(() => {
    //   const unread = notifications.filter(notification => notification.viewed === false);
    //   if (unread.length > 0){ // read un read ones
    //     sendRequest('/account/read_notif/','GET','')
    // }
  },[])
    
    return ( 
        <>
         {deleteAll && <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 w-md ">
          <div className="bg-white rounded-xl p-4 w-[90%] max-w-md">
            <div className="flex justify-between items-center mb-6 gap-10">
              <h3 className="text-xl font-semibold">Delete All Notification </h3>
              <button onClick={() => {setShowDeleteAll(false)}} className="text-gray-500">
                <i className="fas fa-times"></i>
              </button>
            </div>
            <p className="text-sm text-red-600 bg-red-100 p-1 px-2 rounded-full">All notifications will be permanently deleted !</p>

            <div className="flex justify-between gap-4 mt-4">
              <button type="button" className="bg-red-500 text-white p-2 rounded-md w-full hover:opacity-70 flex gap-3 justify-center items-center"
                onClick={() => {
                  setShowDeleteAll(false)
                  sendRequest(`/account/delete_notifs/`,'GET',null);

                }}
              > 
                <Trash className="w-4 h-4"/>
                Confirm Delete 

              </button>
            </div>
            
          </div>
        </div>}
          <div className="p-3 border-b sticky top-0 z-10 bg-white flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Notifications</h3>
            <LucideTrash2 className="p-1 text-yellow-900 rounded-lg hover:bg-red-500 hover:text-white"
            onClick={() => {
              setShowDeleteAll(true);
            }}
            />
          </div>
          {/* notifications here  */}
          
        </>
     );
}
 
export default Rightbar;