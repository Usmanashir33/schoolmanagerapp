import { useContext, useEffect, useState } from "react";
// import { jwtDecode } from "jwt-decode";
import { authContext } from "../customContexts/AuthContext";
import { Navigate } from "react-router-dom";

const ProtectedRoute = ({children}) => {
    const {isAuthenticated,} = useContext(authContext);
    const [allow,setAllow] = useState(true);

    const allow_access =  () => {
        if (isAuthenticated){
            let token = localStorage.getItem('a_token')
            if (token){
                setAllow(true)
            }else{setAllow(false)};
        }else{
            setAllow(false);
        }
    }
    useEffect(() => {
        allow_access()
    },[isAuthenticated])
    return allow? children : <Navigate to='/auth' replace/>;
}
 
export default ProtectedRoute;