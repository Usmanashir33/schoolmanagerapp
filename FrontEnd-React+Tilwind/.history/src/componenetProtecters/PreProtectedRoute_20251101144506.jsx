import { useContext, useEffect, useState } from "react";
import { authContext } from "../customContexts/AuthContext";
import { Navigate } from "react-router-dom";

const PreProtectedRoute = ({children}) => {
    const {isAuthenticated} = useContext(authContext);
    const [allow,setAllow] = useState(true);

    const disallow_access = () => {
        if (isAuthenticated){
            setAllow(false);
        }else{
            setAllow(true);
        }
    }
    useEffect(() => {
        disallow_access();
    },[isAuthenticated])
    return allow? children : <Navigate to='/h/' replace/>;
}
 
export default PreProtectedRoute;