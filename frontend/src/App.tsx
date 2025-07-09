import { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Plot from 'react-plotly.js';
import { Upload, TrendingUp, ImageIcon, BarChart3, DollarSign, Target, Trophy, Mail, CheckCircle, AlertCircle, FileImage, X, ZoomIn } from 'lucide-react';

const API_BASE = "http://localhost:8001";

function App() {
  const [images, setImages] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadMsg, setUploadMsg] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [sendEmail, setSendEmail] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  // Fetch images
  useEffect(() => {
    axios.get(`${API_BASE}/list-images`).then(res => {
      setImages(res.data.data.images || []);
    }).catch(err => console.error('Failed to fetch images:', err));
    
    axios.get(`${API_BASE}/trading-stats`).then(res => {
      setStats(res.data.data);
    }).catch(err => console.error('Failed to fetch stats:', err));
  }, [uploadMsg]);

  // Handle keyboard events for modal
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && selectedImage) {
        setSelectedImage(null);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [selectedImage]);

  // Handle file upload
  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    setUploading(true);
    setUploadMsg("");
    setUploadResult(null);
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      const res = await axios.post(`${API_BASE}/extract-trade-upload?send_email=${sendEmail}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setUploadMsg(res.data.message || "Upload successful!");
      setUploadResult({
        success: true,
        data: res.data.data,
        message: res.data.message
      });
      setSelectedFile(null);
      if (fileInput.current) fileInput.current.value = "";
    } catch (err: any) {
      const errorMsg = err?.response?.data?.detail || "Upload failed";
      setUploadMsg(errorMsg);
      setUploadResult({
        success: false,
        error: errorMsg
      });
    } finally {
      setUploading(false);
    }
  };

  // Handle drag and drop
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  // Prepare PnL chart data
  const pnlData = stats?.pnl_history || [];
  const pnlChart = pnlData.length > 0 ? (
    <Plot
      data={[{
        x: pnlData.map((d: any) => d.date),
        y: pnlData.map((d: any) => d.pnl),
        type: 'scatter',
        mode: 'lines+markers',
        marker: { color: '#10b981', size: 6 },
        line: { color: '#10b981', width: 2 },
        name: 'PnL',
        fill: 'tonexty',
        fillcolor: 'rgba(16, 185, 129, 0.1)',
      }]}
      layout={{
        title: {
          text: 'PnL Over Time',
          font: { size: 16, color: '#374151' }
        },
        autosize: true,
        height: 280,
        margin: { t: 40, l: 60, r: 20, b: 40 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        xaxis: {
          gridcolor: '#e5e7eb',
          tickfont: { color: '#6b7280' }
        },
        yaxis: {
          gridcolor: '#e5e7eb',
          tickfont: { color: '#6b7280' }
        }
      }}
      style={{ width: '100%' }}
      config={{ displayModeBar: false }}
    />
  ) : (
    <div className="flex flex-col items-center justify-center h-64 text-gray-400">
      <BarChart3 className="w-12 h-12 mb-2" />
      <p>No PnL data available</p>
    </div>
  );

  const formatCurrency = (value: number | null) => {
    if (value === null || value === undefined) return '-';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  const getWinRateColor = (rate: number) => {
    if (rate >= 0.6) return 'text-green-600';
    if (rate >= 0.4) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-3">
            Trading Analysis Dashboard
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Upload trading screenshots, analyze your performance, and track your trading journey with advanced analytics.
          </p>
        </div>

        {/* Enhanced Upload Section */}
        <Card className="mb-8 border-0 shadow-lg bg-white/70 backdrop-blur-sm">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-xl">
              <Upload className="w-5 h-5 text-blue-600" />
              Upload & Analyze Your Trade
              <span className="text-sm font-normal text-gray-500 ml-2">• Email alerts available</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleUpload} className="space-y-6">
              {/* Drop Zone */}
              <div
                className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ${
                  dragActive
                    ? 'border-purple-400 bg-purple-50'
                    : selectedFile
                    ? 'border-green-300 bg-green-50'
                    : 'border-gray-300 hover:border-purple-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => !selectedFile && fileInput.current?.click()}
              >
                <input
                  type="file"
                  accept="image/*"
                  ref={fileInput}
                  onChange={e => setSelectedFile(e.target.files?.[0] || null)}
                  className="hidden"
                  disabled={uploading}
                />

                {selectedFile ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-center">
                      <FileImage className="w-12 h-12 text-green-500" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 text-lg">
                        {selectedFile.name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatFileSize(selectedFile.size)}
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedFile(null);
                        setUploadResult(null);
                        if (fileInput.current) fileInput.current.value = '';
                      }}
                      className="text-sm text-red-600 hover:text-red-700 font-medium"
                    >
                      Remove file
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex items-center justify-center">
                      <Upload className="w-12 h-12 text-gray-400" />
                    </div>
                    <div>
                      <p className="text-lg font-medium text-gray-700">
                        Drop your trade screenshot here
                      </p>
                      <p className="text-sm text-gray-500">
                        or click to browse files
                      </p>
                    </div>
                    <p className="text-xs text-gray-400">
                      PNG, JPG, JPEG up to 10MB
                    </p>
                  </div>
                )}
              </div>

              {/* Email Option */}
              <div className="p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-100">
                <label className="flex items-center justify-between cursor-pointer">
                  <div className="flex items-center space-x-3">
                    <Mail className="w-5 h-5 text-purple-600" />
                    <div>
                      <span className="text-sm font-medium text-gray-900">
                        Send trade summary email
                      </span>
                      <p className="text-xs text-gray-600">
                        Get instant AI-generated trade analysis via email
                      </p>
                    </div>
                  </div>
                  <div className="relative">
                    <input
                      type="checkbox"
                      checked={sendEmail}
                      onChange={(e) => setSendEmail(e.target.checked)}
                      className="sr-only"
                    />
                    <div
                      className={`w-11 h-6 rounded-full transition-colors duration-200 ${
                        sendEmail
                          ? 'bg-purple-600'
                          : 'bg-gray-300'
                      }`}
                    >
                      <div
                        className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform duration-200 ${
                          sendEmail ? 'translate-x-5' : 'translate-x-0.5'
                        } mt-0.5`}
                      />
                    </div>
                  </div>
                </label>
              </div>

              {/* Upload Button */}
              <div className="flex justify-center">
                <Button 
                  type="submit" 
                  disabled={uploading || !selectedFile}
                  className={`px-8 py-3 font-medium transition-all duration-200 flex items-center gap-2 ${
                    !selectedFile || uploading
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                  }`}
                >
                  {uploading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Analyzing trade...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      Upload & Analyze
                      {sendEmail && <Mail className="w-4 h-4 ml-1" />}
                    </>
                  )}
                </Button>
              </div>

              {/* Results */}
              {uploadResult && (
                <div className="mt-6">
                  {uploadResult.success ? (
                    <div className="p-6 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-start gap-3">
                        <CheckCircle className="w-6 h-6 text-green-500 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <h4 className="font-semibold text-green-900 text-lg">
                            Analysis Complete!
                          </h4>
                          <p className="text-sm text-green-700 mt-1">
                            {uploadResult.message}
                          </p>
                          
                          {/* Trade Details */}
                          <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                            <div className="bg-white p-3 rounded border">
                              <span className="text-green-600 font-medium block">Trade ID:</span>
                              <span className="text-green-800 font-mono">
                                {uploadResult.data.trade_id || 'N/A'}
                              </span>
                            </div>
                            <div className="bg-white p-3 rounded border">
                              <span className="text-green-600 font-medium block">Ticker:</span>
                              <span className="text-green-800 font-semibold">
                                {uploadResult.data.ticker || 'N/A'}
                              </span>
                            </div>
                            <div className="bg-white p-3 rounded border">
                              <span className="text-green-600 font-medium block">Direction:</span>
                              <span className={`font-semibold ${
                                uploadResult.data.direction === 'long' ? 'text-green-700' : 
                                uploadResult.data.direction === 'short' ? 'text-red-700' : 'text-gray-700'
                              }`}>
                                {uploadResult.data.direction?.toUpperCase() || 'N/A'}
                              </span>
                            </div>
                            <div className="bg-white p-3 rounded border">
                              <span className="text-green-600 font-medium block">P&L:</span>
                              <span className={`font-bold text-lg ${
                                (uploadResult.data.pnl_amount || 0) > 0 
                                  ? 'text-green-600' 
                                  : 'text-red-600'
                              }`}>
                                {uploadResult.data.pnl_amount ? `${uploadResult.data.pnl_amount}` : 'N/A'}
                              </span>
                            </div>
                          </div>

                          {/* Email Status */}
                          {sendEmail && (
                            <div className="mt-4 p-4 bg-white rounded border">
                              <div className="flex items-center gap-2 mb-3">
                                <Mail className="w-5 h-5 text-purple-600" />
                                <span className="font-medium text-gray-900">
                                  Email Status
                                </span>
                              </div>
                              <div className="space-y-2 text-sm">
                                <div className="flex justify-between items-center">
                                  <span className="text-gray-600">Primary Email:</span>
                                  <span className={`font-medium ${
                                    uploadResult.data.email_sent ? 'text-green-600' : 'text-yellow-600'
                                  }`}>
                                    {uploadResult.data.email_status || 'Unknown'}
                                  </span>
                                </div>
                                <div className="flex justify-between items-center">
                                  <span className="text-gray-600">Auto Alert:</span>
                                  <span className={`font-medium ${
                                    uploadResult.data.auto_email_sent ? 'text-green-600' : 'text-yellow-600'
                                  }`}>
                                    {uploadResult.data.auto_email_status || 'Unknown'}
                                  </span>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                      <div className="flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
                        <div>
                          <h4 className="font-medium text-red-900">
                            Upload Failed
                          </h4>
                          <p className="text-sm text-red-700 mt-1">
                            {uploadResult.error}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Legacy message display for backward compatibility */}
              {uploadMsg && !uploadResult && (
                <div className={`text-center p-3 rounded-lg ${
                  uploadMsg.includes('successful') || uploadMsg.includes('Upload successful') 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-red-100 text-red-700'
                }`}>
                  {uploadMsg}
                </div>
              )}

              {/* Usage Tips */}
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="text-sm font-medium text-blue-900 mb-2">
                  💡 Tips for best results:
                </h4>
                <ul className="text-xs text-blue-700 space-y-1">
                  <li>• Upload clear, high-resolution screenshots</li>
                  <li>• Ensure trade details are visible and unobstructed</li>
                  <li>• Enable email alerts for instant trade summaries</li>
                  <li>• Supported formats: PNG, JPG, JPEG</li>
                </ul>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Stats and Chart Grid */}
        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          {/* Trading Stats */}
          <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-xl">
                <TrendingUp className="w-5 h-5 text-green-600" />
                Trading Performance
              </CardTitle>
            </CardHeader>
            <CardContent>
              {stats ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <Target className="w-4 h-4 text-blue-600" />
                        <span className="text-sm font-medium text-blue-700">Total Trades</span>
                      </div>
                      <div className="text-2xl font-bold text-blue-800">
                        {stats.total_trades ?? '-'}
                      </div>
                    </div>
                    
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <Trophy className="w-4 h-4 text-purple-600" />
                        <span className="text-sm font-medium text-purple-700">Win Rate</span>
                      </div>
                      <div className={`text-2xl font-bold ${stats.win_rate ? getWinRateColor(stats.win_rate) : 'text-gray-400'}`}>
                        {stats.win_rate ? `${(stats.win_rate * 100).toFixed(1)}%` : '-'}
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <DollarSign className="w-4 h-4 text-green-600" />
                      <span className="text-sm font-medium text-green-700">Total PnL</span>
                    </div>
                    <div className="text-2xl font-bold text-green-800">
                      {formatCurrency(stats.total_pnl)}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-emerald-50 p-3 rounded-lg">
                      <div className="text-xs font-medium text-emerald-700 mb-1">Best Trade</div>
                      <div className="text-lg font-bold text-emerald-800">
                        {formatCurrency(stats.best_trade)}
                      </div>
                    </div>
                    
                    <div className="bg-red-50 p-3 rounded-lg">
                      <div className="text-xs font-medium text-red-700 mb-1">Worst Trade</div>
                      <div className="text-lg font-bold text-red-800">
                        {formatCurrency(stats.worst_trade)}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-64 text-gray-400">
                  <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-400 mx-auto mb-4"></div>
                    <p>Loading trading stats...</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* PnL Chart */}
          <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-2 text-xl">
                <BarChart3 className="w-5 h-5 text-purple-600" />
                PnL Trend
              </CardTitle>
            </CardHeader>
            <CardContent>
              {pnlChart}
            </CardContent>
          </Card>
        </div>

        {/* Enhanced Images Gallery */}
        <Card className="border-0 shadow-lg bg-white/70 backdrop-blur-sm">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-2 text-xl">
              <ImageIcon className="w-5 h-5 text-indigo-600" />
              Trade Screenshots Gallery
              <span className="text-sm font-normal text-gray-500 ml-2">
                {images.length} {images.length === 1 ? 'image' : 'images'}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {images.length === 0 ? (
                <div className="col-span-full flex flex-col items-center justify-center py-12 text-gray-400">
                  <ImageIcon className="w-16 h-16 mb-4" />
                  <p className="text-lg font-medium">No screenshots uploaded yet</p>
                  <p className="text-sm">Upload your first trade screenshot to get started</p>
                </div>
              ) : (
                images.map((img, index) => (
                  <div key={img.path} className="group relative">
                    <div 
                      className="aspect-square bg-gray-100 rounded-lg overflow-hidden shadow-md hover:shadow-lg transition-all duration-200 cursor-pointer transform hover:scale-105"
                      onClick={() => setSelectedImage(`${API_BASE}/uploads/${img.filename}`)}
                    >
                      <img
                        src={`${API_BASE}/uploads/${img.filename}`}
                        alt={`Trade screenshot ${index + 1}`}
                        className="w-full h-full object-cover"
                        loading="lazy"
                      />
                      
                      {/* Hover Overlay */}
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-all duration-200 flex items-center justify-center">
                        <ZoomIn className="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                      </div>
                    </div>
                    
                    <div className="mt-2">
                      <p className="text-xs text-gray-600 truncate font-medium">
                        {img.filename}
                      </p>
                      <p className="text-xs text-gray-400">
                        {(img.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Image Modal/Lightbox */}
        {selectedImage && (
          <div 
            className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedImage(null)}
          >
            <div className="relative max-w-7xl max-h-full w-full h-full flex items-center justify-center">
              {/* Close Button */}
              <button
                onClick={() => setSelectedImage(null)}
                className="absolute top-4 right-4 z-10 p-2 bg-black/50 hover:bg-black/70 rounded-full text-white transition-colors duration-200"
              >
                <X className="w-6 h-6" />
              </button>
              
              {/* Image */}
              <img
                src={selectedImage}
                alt="Trade screenshot"
                className="max-w-full max-h-full object-contain rounded-lg shadow-2xl"
                onClick={(e) => e.stopPropagation()}
              />
              
              {/* Image Info */}
              <div className="absolute bottom-4 left-4 bg-black/70 text-white px-4 py-2 rounded-lg">
                <p className="text-sm font-medium">
                  {selectedImage.split('/').pop()}
                </p>
                <p className="text-xs text-gray-300">
                  Press ESC to close
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;