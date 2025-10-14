import React, { useState, useEffect } from 'react';
import { ApiService } from '../api/services';
import { useNavigate } from 'react-router-dom';

// Content types matching your backend schemas
interface ContentPage {
  id: string;
  title: string;
  slug: string;
  content: string;
  is_published: boolean;
  page_type: string;
  author_id: string;
  created_at: string;
  updated_at: string;
}

interface ContentPageCreate {
  title: string;
  slug: string;
  content: string;
  is_published: boolean;
  page_type: string;
}

const Admin: React.FC = () => {
  const [user, setUser] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'import' | 'export' | 'content'>('import');
  const [file, setFile] = useState<File | null>(null);
  const [modelType, setModelType] = useState('fines');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const navigate = useNavigate();

  // Export handler
const [exportFormat, setExportFormat] = useState('csv');

const handleExport = async () => {
  setLoading(true);
  try {
    const blob = await ApiService.exportData(modelType, exportFormat);
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${modelType}_export.${exportFormat === 'excel' ? 'xlsx' : 'csv'}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    alert('Export completed successfully!');
  } catch (error: any) {
    console.error('Export error:', error);
    alert('Export failed: ' + error.message);
  } finally {
    setLoading(false);
  }
};


  // Content Management State
  const [pages, setPages] = useState<ContentPage[]>([]);
  const [editingPage, setEditingPage] = useState<ContentPage | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [contentLoading, setContentLoading] = useState(false);

  // Check authentication on component mount
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const userObj = JSON.parse(userData);
      setUser(userObj);
          // RESTRICT ACCESS - Editors can only see content management
      if (userObj.role === 'redactor') {
        setActiveTab('content'); // Force content tab
        // Hide import/export tabs completely for editors
      }
      
      if (userObj.role !== 'admin' && userObj.role !== 'redactor') {
        navigate('/');
      }
    } else {
      navigate('/login');
    }
  }, [navigate]);

  // Load content pages when content tab is active
  useEffect(() => {
    if (activeTab === 'content') {
      loadContentPages();
    }
  }, [activeTab]);

  const loadContentPages = async () => {
    setContentLoading(true);
    try {
      // This endpoint needs to be added to your services.ts
      const contentPages = await ApiService.getContentPages();
      setPages(contentPages);
    } catch (error) {
      console.error('Failed to load content pages:', error);
      alert('Failed to load content pages');
    } finally {
      setContentLoading(false);
    }
  };

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    try {
      const columnMapping = {
        "issued_at": "Дата нарушения",
        "plate_number": "Номер автомобиля", 
        "violation_code": "Код нарушения",
        "amount": "Сумма штрафа"
      };
      
      const importResult = await ApiService.importData(modelType, file, columnMapping);
      setResult(importResult);
      alert('Data imported successfully!');
    } catch (error: any) {
      console.error('Import error:', error);
      alert('Import failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Content Management Functions
  const handleCreatePage = async (pageData: ContentPageCreate | Partial<ContentPage>) => {
    try {
      // Type guard to ensure we have all required fields for creation
      if (!pageData.title || !pageData.slug || !pageData.content || !pageData.page_type) {
        throw new Error('Missing required fields for page creation');
      }
      
      const createData: ContentPageCreate = {
        title: pageData.title,
        slug: pageData.slug,
        content: pageData.content,
        page_type: pageData.page_type,
        is_published: pageData.is_published || false
      };
      
      await ApiService.createPage(createData);
      await loadContentPages();
      setIsCreating(false);
      alert('Page created successfully!');
    } catch (error) {
      console.error('Failed to create page:', error);
      alert('Failed to create page');
    }
  };

  const handleUpdatePage = async (pageId: string, updates: Partial<ContentPage>) => {
    try {
      await ApiService.updatePage(pageId, updates);
      await loadContentPages();
      setEditingPage(null);
      alert('Page updated successfully!');
    } catch (error) {
      console.error('Failed to update page:', error);
      alert('Failed to update page');
    }
  };

  const handleDeletePage = async (pageId: string) => {
    if (window.confirm('Are you sure you want to delete this page?')) {
      try {
        await ApiService.deletePage(pageId);
        await loadContentPages();
        alert('Page deleted successfully!');
      } catch (error) {
        console.error('Failed to delete page:', error);
        alert('Failed to delete page');
      }
    }
  };

  const generateSlug = (title: string) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9а-яё]/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
  };

  // Show loading while checking auth
  if (!user) {
    return <div className="flex justify-center items-center h-64">Loading...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-2">Admin Panel</h1>
      <p className="text-gray-600 mb-6">Welcome, {user.username} ({user.role})</p>
      
      {/* Tab Navigation - Hide import/export for editors */}
      <div className="flex border-b mb-6">
        {(user.role === 'admin' || user.role === 'redactor') && (
          <button
            className={`px-4 py-2 font-medium ${
              activeTab === 'content' 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-500'
            }`}
            onClick={() => setActiveTab('content')}
          >
            Content Management
          </button>
        )}
        
        {/* Only show import/export for admins */}
        {user.role === 'admin' && (
          <>
            <button
              className={`px-4 py-2 font-medium ${
                activeTab === 'import' 
                  ? 'border-b-2 border-blue-500 text-blue-600' 
                  : 'text-gray-500'
              }`}
              onClick={() => setActiveTab('import')}
            >
              Import Data
            </button>
            <button
              className={`px-4 py-2 font-medium ${
                activeTab === 'export' 
                  ? 'border-b-2 border-blue-500 text-blue-600' 
                  : 'text-gray-500'
              }`}
              onClick={() => setActiveTab('export')}
            >
              Export Data
            </button>
          </>
        )}
      </div>

      {/* Import Tab */}
      {activeTab === 'import' && (
        <div>
          <h2 className="text-xl font-bold mb-4">Import Data</h2>
          <form onSubmit={handleImport} className="max-w-md space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Data Type:</label>
              <select 
                value={modelType} 
                onChange={(e) => setModelType(e.target.value)}
                className="border p-2 w-full rounded"
              >
                <option value="fines">Fines</option>
                <option value="accidents">Accidents</option>
                <option value="traffic_lights">Traffic Lights</option>
                <option value="evacuations">Evacuations</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">File (CSV or Excel):</label>
              <input 
                type="file" 
                accept=".csv,.xlsx,.xls"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="border p-2 w-full rounded"
              />
              <p className="text-sm text-gray-600 mt-1">
                Supported formats: CSV, XLSX, XLS
              </p>
            </div>
            
            <button 
              type="submit" 
              disabled={loading || !file}
              className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50 hover:bg-blue-600 transition"
            >
              {loading ? 'Importing...' : 'Import Data'}
            </button>
          </form>

          {result && (
            <div className="mt-6 p-4 bg-gray-100 rounded">
              <h3 className="font-semibold mb-2">Import Result:</h3>
              <pre className="text-sm">{JSON.stringify(result, null, 2)}</pre>
            </div>
          )}
        </div>
      )}

      {/* Export Tab */}
      {activeTab === 'export' && (
        <div>
          <h2 className="text-xl font-bold mb-4">Export Data</h2>
          <div className="max-w-md space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Export Type:</label>
              <select 
                value={modelType} 
                onChange={(e) => setModelType(e.target.value)}
                className="border p-2 w-full rounded"
              >
                <option value="fines">Fines</option>
                <option value="accidents">Accidents</option>
                <option value="traffic_lights">Traffic Lights</option>
                <option value="evacuations">Evacuations</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Format:</label>
              <select 
                value={exportFormat} 
                onChange={(e) => setExportFormat(e.target.value)}
                className="border p-2 w-full rounded"
              >
                <option value="csv">CSV</option>
                <option value="excel">Excel</option>
              </select>
            </div>
            
            <button 
              onClick={handleExport}
              disabled={loading}
              className="bg-green-500 text-white px-4 py-2 rounded disabled:opacity-50 hover:bg-green-600 transition"
            >
              {loading ? 'Exporting...' : 'Export Data'}
            </button>
          </div>
        </div>
      )}

      {/* Content Management Tab */}
      {activeTab === 'content' && (
        <div>
          <h2 className="text-xl font-bold mb-4">Content Management</h2>
          
          {/* Content Actions */}
          <div className="flex gap-4 mb-6">
            <button
              onClick={() => setIsCreating(true)}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition"
            >
              Create New Page
            </button>
            <button
              onClick={loadContentPages}
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 transition"
            >
              Refresh
            </button>
          </div>

          {/* Page Creation Form */}
          {isCreating && (
            <PageEditor
              page={null}
              onSave={handleCreatePage}
              onCancel={() => setIsCreating(false)}
              generateSlug={generateSlug}
            />
          )}

          {/* Page Editing Form */}
          {editingPage && (
            <PageEditor
              page={editingPage}
              onSave={(data) => handleUpdatePage(editingPage.id, data)}
              onCancel={() => setEditingPage(null)}
              generateSlug={generateSlug}
            />
          )}

          {/* Pages List */}
          {contentLoading ? (
            <div className="flex justify-center items-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            </div>
          ) : (
            <div className="grid gap-4">
              {pages.map((page) => (
                <div key={page.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-semibold text-lg">{page.title}</h3>
                      <p className="text-sm text-gray-600">
                        Slug: {page.slug} • Type: {page.page_type} • 
                        Status: {page.is_published ? 'Published' : 'Draft'}
                      </p>
                      <p className="text-xs text-gray-500">
                        Updated: {new Date(page.updated_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setEditingPage(page)}
                        className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
                      >
                        Edit
                      </button>
                      {user.role === 'admin' && (
                        <button
                          onClick={() => handleDeletePage(page.id)}
                          className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                        >
                          Delete
                        </button>
                      )}
                    </div>
                  </div>
                  <div className="text-sm text-gray-700 line-clamp-2">
                    {page.content.substring(0, 200)}...
                  </div>
                </div>
              ))}
              
              {pages.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No content pages found. Create your first page!
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Page Editor Component
interface PageEditorProps {
  page: ContentPage | null;
  onSave: (data: ContentPageCreate | Partial<ContentPage>) => void;
  onCancel: () => void;
  generateSlug: (title: string) => string;
}

const PageEditor: React.FC<PageEditorProps> = ({ page, onSave, onCancel, generateSlug }) => {
  const [formData, setFormData] = useState({
    title: page?.title || '',
    slug: page?.slug || '',
    content: page?.content || '',
    page_type: page?.page_type || 'news',
    is_published: page?.is_published || false
  });

  const handleTitleChange = (title: string) => {
    setFormData(prev => ({
      ...prev,
      title,
      slug: prev.slug || generateSlug(title)
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="bg-gray-50 p-6 rounded-lg mb-6">
      <h3 className="text-lg font-semibold mb-4">
        {page ? 'Edit Page' : 'Create New Page'}
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Title</label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => handleTitleChange(e.target.value)}
            className="border p-2 w-full rounded"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Slug</label>
          <input
            type="text"
            value={formData.slug}
            onChange={(e) => setFormData(prev => ({ ...prev, slug: e.target.value }))}
            className="border p-2 w-full rounded"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Page Type</label>
          <select
            value={formData.page_type}
            onChange={(e) => setFormData(prev => ({ ...prev, page_type: e.target.value }))}
            className="border p-2 w-full rounded"
          >
            <option value="news">News</option>
            <option value="about">About</option>
            <option value="service">Service</option>
            <option value="statistics">Statistics</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Content</label>
          <textarea
            value={formData.content}
            onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
            rows={10}
            className="border p-2 w-full rounded"
            required
          />
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="is_published"
            checked={formData.is_published}
            onChange={(e) => setFormData(prev => ({ ...prev, is_published: e.target.checked }))}
            className="mr-2"
          />
          <label htmlFor="is_published" className="text-sm font-medium">
            Publish immediately
          </label>
        </div>

        <div className="flex gap-2">
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            {page ? 'Update Page' : 'Create Page'}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default Admin;