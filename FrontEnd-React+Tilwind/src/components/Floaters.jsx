import { useContext, useEffect } from "react";
import { uiContext } from "../customContexts/UiContext";

const Floaters = () => {
  const { isLoading, setIsLoading, error, setError, success, setSuccess } = useContext(uiContext);

  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError('');
        setSuccess('');
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [success, error]);

  return (
    <div className="fixed inset-x-0 top-0 z-50 flex items-start justify-end px-4 pt-4 pointer-events-none">
      <div className="space-y-2 max-w-sm w-full">

        {/* Success Toast */}
        {success && (
          <div className="flex items-center justify-between gap-3 px-4 py-2 bg-green-500 text-white rounded-md shadow-lg pointer-events-auto">
            <i className="fas fa-check-circle text-xl"></i>
            <span className="flex-1">{success}</span>
            <button onClick={() => setSuccess('')} className="hover:text-gray-200">
              <i className="fas fa-times"></i>
            </button>
          </div>
        )}

        {/* Error Toast */}
        {error && (
          <div className="flex items-center justify-between gap-3 px-4 py-2 bg-red-500 text-white rounded-md shadow-lg pointer-events-auto">
            <i className="fas fa-exclamation-circle text-xl"></i>
            <span className="flex-1">{error}</span>
            <button onClick={() => setError('')} className="hover:text-gray-200">
              <i className="fas fa-times"></i>
            </button>
          </div>
        )}
      </div>

      {/* Loading Spinner */}
      {isLoading && (
        <div className="fixed  top-5 left-1/2 transform -translate-x-1/2 bg-gray-50 opacity-90 p-1 rounded-md shadow-lg flex flex-col items-center z-50">
          <div className="animate-spin text-blue-500 mb-1">
            <i className="fas fa-spinner fa-lg"></i>
          </div>
          <span className="text-gray-700 text-xs font-medium">Loading...</span>
        </div>
      )}
    </div>
  );
};

export default Floaters;