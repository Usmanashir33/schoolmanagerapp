import { useContext, useEffect, useState } from "react";
import { uiContext } from "../customContexts/UiContext";
import config from "../customHooks/ConfigDetails";
import { authContext } from "../customContexts/AuthContext"; 


const useRequest = ( ) => {
    const Aborter = new AbortController();
    const {getToken,isAuthenticated} = useContext(authContext) ;
    const {setIsLoading,setError} = useContext(uiContext);

    const sendRequest = async (url,method,formdata="",triggeredFunc,load=false,is_formData=false) => {
        if (!isAuthenticated){return}
        if (load){
            setIsLoading(true);
        }
        let token = await getToken()
        if (!token) {
            return setError('Try again later')
        }
        let options = {
            signal : Aborter.signal ,
            method:method,
            headers : {
                "Content-Type":"application/json",
                Authorization : `Bearer ${token}`
            }}
        if (method !== "GET" &&  method !== "DELETE"){
            if (!is_formData){options.body = JSON.stringify(formdata)}
            if (is_formData){
                options.headers = {Authorization : `Bearer ${token}`};
                options.body = formdata
            }
         }
        setTimeout(() => {
            fetch(`${config.BASE_URL}${url}`,options
        ).then((resp) => {
                if (resp.ok){
                    return resp.json();
                }
                setIsLoading(false);
            })
            .then((data) => {
                if (data?.error){
                    return setError(data?.error)
                }
                triggeredFunc(data)
                setIsLoading(false);
            }).catch((err) => {
                 //    show error here 
                setIsLoading(false);
                applyErrors(err.message)
            })
            .finally(() => {
                setTimeout(() => {
                    setIsLoading(false)
                }, 1000);
            })
            }, 500);
            return (() => {Aborter.abort()})
    }
    return ({sendRequest});
}
 
export default useRequest;