
import { useEffect, useRef, useState } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:5000";

const ALLOWED_EXTENSIONS = [".pdf", ".txt", ".docx", ".md"];

function FileUpload({ onReady, onProcessing }) {
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState("");
    const [status, setStatus] = useState("idle");
    const [uploadProgress, setUploadProgress] = useState(0);

    const timerRef = useRef(null);
    const inputRef = useRef(null);

    useEffect(() => {
        return () => {
            if (timerRef.current) {
                clearTimeout(timerRef.current);
            }
        };
    }, []);

    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0];

        if (!selectedFile) return;

        const extension = selectedFile.name
            .substring(selectedFile.name.lastIndexOf("."))
            .toLowerCase();

        if (!ALLOWED_EXTENSIONS.includes(extension)) {
            setFile(null);
            setMessage(
                "Unsupported format. Select PDF, TXT, DOCX or MD."
            );
            setStatus("idle");
            event.target.value = "";
            return;
        }

        setFile(selectedFile);
        setMessage("");
        setStatus("idle");
        setUploadProgress(0);
    };

    const checkStatus = async (jobId) => {
        try {
            const response = await axios.get(
                `${API_URL}/status/${jobId}`
            );

            const data = response.data;

            if (data.status === "ready") {
                setStatus("ready");
                setMessage("Document is ready!");
                onReady();
                return;
            }

            if (data.status === "failed") {
                setStatus("failed");
                setMessage(
                    data.error || "Document processing failed."
                );
                return;
            }

            setStatus("processing");
            setMessage("Preparing your document...");

            timerRef.current = setTimeout(
                () => checkStatus(jobId),
                2000
            );

        } catch (error) {
            setStatus("failed");
            setMessage(
                "Unable to check document processing status."
            );
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setMessage("Please select a document first.");
            return;
        }

        if (timerRef.current) {
            clearTimeout(timerRef.current);
        }

        onProcessing();

        setStatus("uploading");
        setMessage("");
        setUploadProgress(0);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const response = await axios.post(
                `${API_URL}/upload`,
                formData,
                {
                    onUploadProgress: (progressEvent) => {
                        if (progressEvent.total) {
                            const percentage = Math.round(
                                (progressEvent.loaded * 100) /
                                progressEvent.total
                            );

                            setUploadProgress(percentage);
                        }
                    }
                }
            );

            const { job_id } = response.data;

            setUploadProgress(100);
            setStatus("processing");
            setMessage("Document uploaded successfully!");

            checkStatus(job_id);

        } catch (error) {
            setStatus("failed");
            setMessage(
                error.response?.data?.error ||
                "Document upload failed."
            );
        }
    };

    const isBusy =
        status === "uploading" || status === "processing";

    return (
        <div className="file-upload">

            <div className="upload-heading">
                <h2>Knowledge Base</h2>
                <p>Add a document to start chatting with AI.</p>
            </div>

            {/* File Selection Area */}
            <div
                className="upload-dropzone"
                onClick={() => {
                    if (!isBusy) inputRef.current?.click();
                }}
            >
                <div className="upload-icon">↑</div>

                <h3>
                    {file ? "Document selected" : "Upload a document"}
                </h3>

                <p>
                    {file
                        ? file.name
                        : "Click here to browse your files"}
                </p>

                <span>PDF · DOCX · TXT · MD</span>

                <input
                    ref={inputRef}
                    type="file"
                    accept=".pdf,.txt,.docx,.md"
                    onChange={handleFileChange}
                    disabled={isBusy}
                    hidden
                />
            </div>

            {/* Upload Button */}
            <button
                className="upload-button"
                onClick={handleUpload}
                disabled={!file || isBusy || status === "ready"}
            >
                {status === "uploading"
                    ? "Uploading..."
                    : status === "processing"
                    ? "Processing..."
                    : status === "ready"
                    ? "Document Ready"
                    : "Upload Document"}
            </button>

            {/* Upload Progress */}
            {status === "uploading" && (
                <div className="progress-container">
                    <div className="progress-info">
                        <span>Uploading document</span>
                        <span>{uploadProgress}%</span>
                    </div>

                    <div className="progress-track">
                        <div
                            className="progress-fill"
                            style={{
                                width: `${uploadProgress}%`
                            }}
                        />
                    </div>
                </div>
            )}

            {/* Processing Status */}
            {status === "processing" && (
                <div className="upload-status processing-status">
                    <span className="status-dot"></span>
                    Preparing document for AI...
                </div>
            )}

            {status === "ready" && (
                <div className="upload-status ready-status">
                    <span>✓</span>
                    Document is ready for chat.
                </div>
            )}

            {status === "failed" && (
                <div className="upload-status failed-status">
                    {message}
                </div>
            )}

            {status === "idle" && message && (
                <div className="upload-status failed-status">
                    {message}
                </div>
            )}

            <div className="upload-info">
                Your documents are processed locally by this application.
            </div>

        </div>
    );
}

export default FileUpload;
