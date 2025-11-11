import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ArrowLeft, Upload, FileText, RefreshCw, Loader2, CheckCircle, XCircle, Database } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Brand {
  id: string;
  name: string;
  documents: number;
  chunks: number;
  vectors: number;
  last_ingested_at: string;
}

interface UploadResult {
  filename: string;
  status: string;
  brand_id?: string;
  brand_name?: string;
  documents?: number;
  chunks?: number;
  vectors?: number;
  brands?: Record<string, any>;
  error?: string;
}

export function BrandDataPage() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState<UploadResult[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<string>('');
  const [newBrandName, setNewBrandName] = useState('');
  const [brandColumn, setBrandColumn] = useState('brand');
  const [textColumn, setTextColumn] = useState('text');
  const [dragActive, setDragActive] = useState(false);
  const [reindexing, setReindexing] = useState<string | null>(null);

  useEffect(() => {
    fetchBrands();
  }, []);

  const fetchBrands = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/brand/list`);
      setBrands(response.data.brands || []);
    } catch (error) {
      console.error('Error fetching brands:', error);
    }
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const newFiles = Array.from(e.dataTransfer.files).filter(file => {
        const ext = file.name.split('.').pop()?.toLowerCase();
        return ['csv', 'xlsx', 'xls', 'pdf', 'txt'].includes(ext || '');
      });
      setFiles(prev => [...prev, ...newFiles]);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files);
      setFiles(prev => [...prev, ...newFiles]);
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    const pdfTxtFiles = files.filter(f => {
      const ext = f.name.split('.').pop()?.toLowerCase();
      return ['pdf', 'txt'].includes(ext || '');
    });

    if (pdfTxtFiles.length > 0 && !selectedBrand && !newBrandName) {
      alert('Please select an existing brand or enter a new brand name for PDF/TXT files');
      return;
    }

    setUploading(true);
    setUploadResults([]);

    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      if (selectedBrand) {
        formData.append('brand_id', selectedBrand);
      } else if (newBrandName) {
        formData.append('brand_name', newBrandName);
      }

      formData.append('brand_column', brandColumn);
      formData.append('text_column', textColumn);

      const response = await axios.post(`${API_URL}/api/brand/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadResults(response.data.results || []);
      setFiles([]);
      setNewBrandName('');
      await fetchBrands();
    } catch (error: any) {
      console.error('Error uploading files:', error);
      alert(`Upload failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleReindex = async (brandId: string) => {
    setReindexing(brandId);
    try {
      await axios.post(`${API_URL}/api/brand/reindex`, null, {
        params: { brand_id: brandId }
      });
      await fetchBrands();
      alert('Brand reindexed successfully');
    } catch (error: any) {
      console.error('Error reindexing brand:', error);
      alert(`Reindex failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setReindexing(null);
    }
  };

  const getFileIcon = (_filename: string) => {
    return <FileText className="w-4 h-4" />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
      <header className="container mx-auto px-4 py-6 flex items-center justify-between border-b border-slate-200 bg-white/50 backdrop-blur">
        <div className="flex items-center gap-4">
          <Link to="/">
            <Button variant="ghost" size="sm" className="gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back
            </Button>
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center">
              <Database className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-900">Brand Knowledge</h1>
              <p className="text-xs text-slate-600">Upload and manage brand data</p>
            </div>
          </div>
        </div>
        <Link to="/chat">
          <Button className="gap-2">
            Start Creating
          </Button>
        </Link>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto space-y-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="w-5 h-5" />
                Upload Brand Knowledge
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragActive ? 'border-blue-500 bg-blue-50' : 'border-slate-300 hover:border-slate-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <Upload className="w-12 h-12 mx-auto mb-4 text-slate-400" />
                <p className="text-lg font-medium text-slate-700 mb-2">
                  Drag and drop files here
                </p>
                <p className="text-sm text-slate-500 mb-4">
                  Supports CSV, XLSX, PDF, and TXT files
                </p>
                <input
                  type="file"
                  id="file-upload"
                  multiple
                  accept=".csv,.xlsx,.xls,.pdf,.txt"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <label htmlFor="file-upload">
                  <Button variant="outline" className="cursor-pointer" asChild>
                    <span>Browse Files</span>
                  </Button>
                </label>
              </div>

              {files.length > 0 && (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <h3 className="font-medium text-slate-900">Selected Files ({files.length})</h3>
                    <div className="space-y-2">
                      {files.map((file, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                          <div className="flex items-center gap-3">
                            {getFileIcon(file.name)}
                            <div>
                              <p className="text-sm font-medium text-slate-900">{file.name}</p>
                              <p className="text-xs text-slate-500">
                                {(file.size / 1024).toFixed(1)} KB
                              </p>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeFile(index)}
                          >
                            <XCircle className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="space-y-2">
                      <Label>CSV/XLSX Column Mapping</Label>
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <Label className="text-xs text-slate-600">Brand Column</Label>
                          <Input
                            value={brandColumn}
                            onChange={(e) => setBrandColumn(e.target.value)}
                            placeholder="brand"
                            className="h-8"
                          />
                        </div>
                        <div>
                          <Label className="text-xs text-slate-600">Text Column</Label>
                          <Input
                            value={textColumn}
                            onChange={(e) => setTextColumn(e.target.value)}
                            placeholder="text"
                            className="h-8"
                          />
                        </div>
                      </div>
                      <p className="text-xs text-slate-600">
                        Column names are case-insensitive
                      </p>
                    </div>

                    <div className="space-y-2">
                      <Label>PDF/TXT Brand Assignment</Label>
                      <Select value={selectedBrand} onValueChange={setSelectedBrand}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select existing brand" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="">Create new brand</SelectItem>
                          {brands.map(brand => (
                            <SelectItem key={brand.id} value={brand.id}>
                              {brand.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      {!selectedBrand && (
                        <Input
                          value={newBrandName}
                          onChange={(e) => setNewBrandName(e.target.value)}
                          placeholder="New brand name"
                          className="h-8"
                        />
                      )}
                    </div>
                  </div>

                  <Button
                    onClick={handleUpload}
                    disabled={uploading}
                    className="w-full"
                    size="lg"
                  >
                    {uploading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4 mr-2" />
                        Upload {files.length} File{files.length !== 1 ? 's' : ''}
                      </>
                    )}
                  </Button>
                </div>
              )}

              {uploadResults.length > 0 && (
                <div className="space-y-2">
                  <h3 className="font-medium text-slate-900">Upload Results</h3>
                  <div className="space-y-2">
                    {uploadResults.map((result, index) => (
                      <div
                        key={index}
                        className={`p-3 rounded-lg border ${
                          result.status === 'success'
                            ? 'bg-green-50 border-green-200'
                            : 'bg-red-50 border-red-200'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          {result.status === 'success' ? (
                            <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                          ) : (
                            <XCircle className="w-5 h-5 text-red-600 mt-0.5" />
                          )}
                          <div className="flex-1">
                            <p className="font-medium text-sm text-slate-900">{result.filename}</p>
                            {result.status === 'success' && result.brands && (
                              <div className="mt-2 space-y-1">
                                {Object.entries(result.brands).map(([brandName, stats]: [string, any]) => (
                                  <p key={brandName} className="text-xs text-slate-600">
                                    {brandName}: {stats.chunks} chunks, {stats.vectors} vectors
                                  </p>
                                ))}
                              </div>
                            )}
                            {result.status === 'success' && result.chunks && (
                              <p className="text-xs text-slate-600 mt-1">
                                {result.brand_name}: {result.chunks} chunks, {result.vectors} vectors
                              </p>
                            )}
                            {result.error && (
                              <p className="text-xs text-red-600 mt-1">{result.error}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="w-5 h-5" />
                Brand Catalog
              </CardTitle>
            </CardHeader>
            <CardContent>
              {brands.length === 0 ? (
                <div className="text-center py-12">
                  <Database className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                  <p className="text-slate-600">No brands uploaded yet</p>
                  <p className="text-sm text-slate-500 mt-1">Upload brand knowledge files to get started</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Brand</TableHead>
                      <TableHead className="text-right">Documents</TableHead>
                      <TableHead className="text-right">Chunks</TableHead>
                      <TableHead className="text-right">Vectors</TableHead>
                      <TableHead className="text-right">Last Ingested</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {brands.map(brand => (
                      <TableRow key={brand.id}>
                        <TableCell className="font-medium">{brand.name}</TableCell>
                        <TableCell className="text-right">{brand.documents}</TableCell>
                        <TableCell className="text-right">{brand.chunks}</TableCell>
                        <TableCell className="text-right">{brand.vectors}</TableCell>
                        <TableCell className="text-right text-sm text-slate-600">
                          {brand.last_ingested_at ? new Date(brand.last_ingested_at).toLocaleDateString() : 'N/A'}
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleReindex(brand.id)}
                            disabled={reindexing === brand.id}
                          >
                            {reindexing === brand.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <RefreshCw className="w-4 h-4" />
                            )}
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
