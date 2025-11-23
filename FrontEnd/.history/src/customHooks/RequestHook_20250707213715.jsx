import { useContext, useEffect, useState } from "react";
import { uiContext } from "../customContexts/UiContext";
import config from "../customHooks/ConfigDetails";
import { authContext } from "../customContexts/AuthContext"; 


const useRequest = (
    transections,setTransections,setNotifications,notifications) => {
    const Aborter = new AbortController();
    const {getToken,isAuthenticated} = useContext(authContext) ;
    const {setIsLoading,setError} = useContext(uiContext);

    const applyErrors = (error) => {
        setError(error)
        setTimeout(() => {
            setError('')
        }, 1000);
    }
    // function to remove deleted notification
    const deleteNotifications = (id) => {
        setNotifications(
            notifications.filter( notif => notif.id !== id)
        )
    }
    // function to read all notifications 
    const readNotifications = () => {
        setNotifications(
            notifications.map((notif) => {
                notif.viewed = true
                return notif
            }))
    }
    const processResponseData = (data) => {
        // console.log('data: ', data);
        if (data?.name === 'transections'){
            // setTransections(data?.data)
            if (data?.data?.previous){ // is refetch call
                setTransections((prev) =>({
                    ...data?.data,
                    results: [...prev.results, ...data?.data?.results], // append new results
                }))
            }else{ // its a new call
                setTransections(data?.data)
            }
        }
        if (data?.name === 'notifications'){
            setNotifications(data.data)
        }
        if (data?.name === 'notif_read'){
            readNotifications()
        }
        if (data?.name === 'notif_delete'){
            deleteNotifications(data.id)
        }
        if (data?.name === 'notif_delete_all'){
            setNotifications([]);
        }
    }
    const sendRequest = async (url,method,formdata="",withLoading = true) => {
        if (!isAuthenticated){return}
        if (withLoading){
            setIsLoading(true);
        }   
        let token = await getToken()
        if (!token) {
            setIsLoading(false);
            return setError('Try again later')
        }
        let options = {
            signal : Aborter.signal ,
            method:method,
            headers : {
                "Content-Type":"application/json",
                Authorization : `Bearer ${token}`
            }}
        if (method !== "GET"){
            options.body = JSON.stringify(formdata)
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
                if (!data.error){
                    // grab response here 
                    processResponseData(data)
                } else if (data.error){
                    applyErrors(data.error)
                }
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
    const sendArbitRequest = async (url,method,formdata="",triggeredFunc,load=false,is_formData=false) => {
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
        // if (method !== "GET" &&  method !== "DELETE"){
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
    return ({sendRequest,sendArbitRequest});
}
 
export default useRequest;