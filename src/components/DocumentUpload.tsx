import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { Upload, File, X, CheckCircle2 } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { ACCEPTED_MIME_TYPES } from "@/lib/fileTypes";

// Sanitize filenames to avoid storage InvalidKey errors (spaces, Unicode, punctuation)
const sanitizeFileName = (name: string) => {
  const dot = name.lastIndexOf(".");
  const base = dot > 0 ? name.slice(0, dot) : name;
  const ext = dot > 0 ? name.slice(dot + 1) : "";
  const normalized = base.normalize("NFKD").replace(/[\u0300-\u036f]/g, "");
  const cleaned = normalized.replace(/[^A-Za-z0-9._-]+/g, "_").replace(/^_+|_+$/g, "");
  const trimmed = cleaned.replace(/\.+$/g, "").slice(0, 120) || "file";
  const safeExt = ext.toLowerCase().replace(/[^a-z0-9]+/g, "");
  return safeExt ? `${trimmed}.${safeExt}` : trimmed;
};

interface UploadedFile {
  file: File;
  progress: number;
  status: "uploading" | "complete" | "error";
  id: string;
  path?: string;
}

interface DocumentUploadProps {
  onUploadComplete?: (filePath: string) => void;
}

const DocumentUpload = ({ onUploadComplete }: DocumentUploadProps) => {
  const { toast } = useToast();
  const [files, setFiles] = useState<UploadedFile[]>([]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: crypto.randomUUID(),
      progress: 0,
      status: "uploading" as const,
    }));

    setFiles(prev => [...prev, ...newFiles]);

    // Process each file
    for (const fileObj of newFiles) {
      try {
        let sessionToken = "vidhichakshu-local-admin-token";
        let userId = "a0000000-0000-0000-0000-000000000001";

        try {
          const { data: sessionData } = await supabase.auth.getSession();
          if (sessionData?.session?.access_token) {
            sessionToken = sessionData.session.access_token;
            userId = sessionData.session.user?.id || userId;
          }
        } catch (e) {
          // ignore offline session retrieval
        }

        const safeName = sanitizeFileName(fileObj.file.name);
        let finalPath = `${userId}/${Date.now()}_${safeName}`;
        let uploadSucceeded = false;

        // Attempt 1: Upload to Supabase Storage if URL is not a placeholder
        const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
        if (supabaseUrl && !supabaseUrl.includes("placeholder") && !supabaseUrl.includes("harbkllyyyatxqwolsea")) {
          try {
            await new Promise<void>((resolve, reject) => {
              const xhr = new XMLHttpRequest();
              const url = `${supabaseUrl}/storage/v1/object/documents/${finalPath}`;
              
              xhr.upload.onprogress = (event) => {
                if (event.lengthComputable) {
                  const progress = Math.round((event.loaded / event.total) * 100);
                  setFiles(prev => prev.map(f => f.id === fileObj.id ? { ...f, progress } : f));
                }
              };

              xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                  uploadSucceeded = true;
                  resolve();
                } else {
                  reject(new Error(xhr.responseText || "Upload failed"));
                }
              };

              xhr.onerror = () => reject(new Error("Network error"));
              xhr.open("POST", url, true);
              xhr.setRequestHeader("Authorization", `Bearer ${sessionToken}`);
              xhr.setRequestHeader("apikey", import.meta.env.VITE_SUPABASE_ANON_KEY || import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY);
              xhr.setRequestHeader("Content-Type", fileObj.file.type || "application/octet-stream");
              xhr.send(fileObj.file);
            });
          } catch (e) {
            console.warn("[Upload Notice] Supabase cloud storage unreachable, falling back to local gateway upload:", e);
          }
        }

        // Attempt 2: Local Gateway Upload Fallback (Works 100% Offline)
        if (!uploadSucceeded) {
          const reader = new FileReader();
          await new Promise<void>((resolve, reject) => {
            reader.onload = async () => {
              try {
                const base64Data = reader.result as string;
                const apiUrl = import.meta.env.VITE_API_GATEWAY_URL || 'http://localhost:3000';
                
                // Track simulated progress
                setFiles(prev => prev.map(f => f.id === fileObj.id ? { ...f, progress: 65 } : f));

                const payload = JSON.stringify({
                  fileName: safeName,
                  fileData: base64Data,
                  mimeType: fileObj.file.type || 'application/octet-stream'
                });

                let response: Response | null = null;
                let lastError = "";

                // Route 1: Node.js API Gateway (Port 3000)
                try {
                  response = await fetch(`${apiUrl}/api/upload-file`, {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'Authorization': `Bearer ${sessionToken}`
                    },
                    body: payload
                  });
                } catch (netErr: any) {
                  lastError = netErr.message;
                  console.warn('[Upload] Node gateway unreachable, attempting direct AI engine:', netErr);
                }

                // Route 2: Direct Python Engine fallback (Port 8000)
                if (!response || !response.ok) {
                  try {
                    const fallbackRes = await fetch(`http://localhost:8000/api/upload-file`, {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${sessionToken}`
                      },
                      body: payload
                    });
                    if (fallbackRes.ok) {
                      response = fallbackRes;
                    }
                  } catch (pyErr: any) {
                    console.warn('[Upload] Python direct fallback unreachable:', pyErr);
                  }
                }

                if (!response) {
                  throw new Error(`Upload server unreachable: ${lastError || 'Could not connect to localhost:3000 or localhost:8000'}`);
                }

                const data = await response.json().catch(() => null);

                if (!response.ok) {
                  throw new Error(data?.error || data?.detail || `Server returned error (${response.status})`);
                }

                if (data && data.success && data.filePath) {
                  finalPath = data.filePath;
                  uploadSucceeded = true;
                  setFiles(prev => prev.map(f => f.id === fileObj.id ? { ...f, progress: 100, status: "complete", path: finalPath } : f));
                  resolve();
                } else {
                  reject(new Error(data?.error || "Gateway upload failed"));
                }
              } catch (gatewayErr: any) {
                reject(gatewayErr);
              }
            };
            reader.onerror = () => reject(new Error("File reading error"));
            reader.readAsDataURL(fileObj.file);
          });
        }

        setFiles(prev => prev.map(f => f.id === fileObj.id ? { ...f, status: "complete", progress: 100, path: finalPath } : f));
        toast({
          title: "Upload successful",
          description: `${fileObj.file.name} uploaded successfully`,
        });

        if (onUploadComplete) {
          onUploadComplete(finalPath);
        }
      } catch (error: any) {
        setFiles(prev => prev.map(f => f.id === fileObj.id ? { ...f, status: "error" } : f));
        toast({
          variant: "destructive",
          title: "Upload failed",
          description: error.message || "An error occurred",
        });
      }
    }
  }, [toast, onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_MIME_TYPES,
    maxSize: 50 * 1024 * 1024,
  });

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  };

  return (
    <div className="space-y-4">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
          transition-colors duration-200
          ${isDragActive 
            ? "border-legal-gold bg-legal-gold-light" 
            : "border-border hover:border-legal-gold hover:bg-muted/50"
          }
        `}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
        <p className="text-lg font-medium mb-2">
          {isDragActive ? "Drop files here..." : "Drag & drop files here"}
        </p>
        <p className="text-sm text-muted-foreground mb-4">
          or click to browse files
        </p>
        <div className="text-xs text-muted-foreground space-y-1">
          <p>Supported: PDF, Images (JPG, PNG, TIFF), Audio (WAV, MP3, M4A)</p>
          <p>Max 50MB per file • Up to 10 files at once</p>
        </div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-3">
          <h3 className="font-medium">Uploaded Files</h3>
          {files.map((uploadedFile) => (
            <div
              key={uploadedFile.id}
              className="flex items-center gap-3 p-3 border rounded-lg bg-card"
            >
              <File className="h-8 w-8 text-legal-gold shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {uploadedFile.file.name}
                </p>
                <p className="text-xs text-muted-foreground">
                  {(uploadedFile.file.size / 1024 / 1024).toFixed(2)} MB
                </p>
                {uploadedFile.status === "uploading" && (
                  <Progress value={uploadedFile.progress} className="mt-2 h-1" />
                )}
              </div>
              {uploadedFile.status === "complete" && (
                <CheckCircle2 className="h-5 w-5 text-success shrink-0" />
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeFile(uploadedFile.id)}
                className="shrink-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;
