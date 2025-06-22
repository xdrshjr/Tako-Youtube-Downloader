# YouTube Downloader Web Frontend Design

## 项目概述

基于现有的Python后端YouTube下载器，设计开发一个现代化、美观、优雅的Web前端应用。采用Next.js 14+和React 18+技术栈，提供直观的用户界面和流畅的用户体验。

### 核心设计理念

- 🎨 **现代美学**：采用Material Design 3设计语言，简洁优雅
- ⚡ **性能优先**：代码分割、懒加载、性能优化
- 📱 **响应式设计**：完美适配桌面、平板、移动设备
- 🔄 **实时交互**：WebSocket实时更新下载进度
- 🧩 **模块化架构**：组件化设计，易于维护和扩展
- ♿ **无障碍访问**：符合WCAG 2.1 AA标准

## 技术架构

### 核心技术栈

```typescript
// 主要依赖
{
  "next": "^14.0.0",
  "react": "^18.0.0", 
  "typescript": "^5.0.0",
  "tailwindcss": "^3.3.0",
  "framer-motion": "^10.0.0",
  "zustand": "^4.4.0",
  "@tanstack/react-query": "^4.32.0",
  "socket.io-client": "^4.7.0",
  "react-hook-form": "^7.45.0",
  "zod": "^3.22.0",
  "@headlessui/react": "^1.7.0",
  "@heroicons/react": "^2.0.0"
}
```

### 应用架构

```
src/
├── app/                          # Next.js 14 App Router
│   ├── layout.tsx               # 根布局
│   ├── page.tsx                 # 首页
│   ├── download/                # 单视频下载
│   │   └── page.tsx
│   ├── batch/                   # 批量搜索下载
│   │   └── page.tsx
│   └── history/                 # 下载历史
│       └── page.tsx
├── components/                   # React组件
│   ├── ui/                      # 基础UI组件
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   ├── Modal.tsx
│   │   ├── Progress.tsx
│   │   └── Toast.tsx
│   ├── layout/                  # 布局组件
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── Footer.tsx
│   ├── download/                # 下载相关组件
│   │   ├── URLInput.tsx
│   │   ├── VideoPreview.tsx
│   │   ├── DownloadConfig.tsx
│   │   └── DownloadProgress.tsx
│   ├── batch/                   # 批量下载组件
│   │   ├── SearchInput.tsx
│   │   ├── FilterPanel.tsx
│   │   ├── VideoGrid.tsx
│   │   ├── BatchToolbar.tsx
│   │   └── BatchProgress.tsx
│   └── shared/                  # 共享组件
│       ├── DownloadQueue.tsx
│       ├── SettingsModal.tsx
│       └── NotificationCenter.tsx
├── hooks/                       # 自定义Hooks
│   ├── useDownload.ts
│   ├── useSearch.ts
│   ├── useWebSocket.ts
│   └── useLocalStorage.ts
├── stores/                      # 状态管理
│   ├── downloadStore.ts
│   ├── searchStore.ts
│   └── settingsStore.ts
├── services/                    # API服务
│   ├── api.ts
│   ├── websocket.ts
│   └── types.ts
├── styles/                      # 样式文件
│   ├── globals.css
│   └── components.css
└── utils/                       # 工具函数
    ├── validators.ts
    ├── formatters.ts
    └── constants.ts
```

## 界面设计规范

### 设计系统

#### 颜色系统
```css
:root {
  /* 主色调 - YouTube品牌色的现代化改进 */
  --primary: #ff0000;
  --primary-dark: #cc0000;
  --primary-light: #ff3333;
  
  /* 中性色 */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  
  /* 功能色 */
  --success: #10b981;
  --warning: #f59e0b;
  --error: #ef4444;
  --info: #3b82f6;
  
  /* 背景色 */
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
}

[data-theme="dark"] {
  --bg-primary: #0f172a;
  --bg-secondary: #1e293b;
  --bg-tertiary: #334155;
}
```

#### 字体系统
```css
/* 字体层级 */
.text-display {
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1.1;
}

.text-h1 {
  font-size: 2.25rem;
  font-weight: 700;
  line-height: 1.2;
}

.text-h2 {
  font-size: 1.875rem;
  font-weight: 600;
  line-height: 1.3;
}

.text-body {
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.5;
}

.text-caption {
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1.4;
}
```

#### 组件尺寸规范
```css
/* 间距系统 */
.space-xs { gap: 0.25rem; }
.space-sm { gap: 0.5rem; }
.space-md { gap: 1rem; }
.space-lg { gap: 1.5rem; }
.space-xl { gap: 2rem; }

/* 圆角系统 */
.rounded-sm { border-radius: 0.25rem; }
.rounded-md { border-radius: 0.375rem; }
.rounded-lg { border-radius: 0.5rem; }
.rounded-xl { border-radius: 0.75rem; }

/* 阴影系统 */
.shadow-sm { box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05); }
.shadow-md { box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
.shadow-lg { box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1); }
```

### 动画设计
```css
/* 动画缓动函数 */
.ease-smooth { transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); }
.ease-bounce { transition-timing-function: cubic-bezier(0.68, -0.55, 0.265, 1.55); }

/* 常用动画时长 */
.duration-fast { transition-duration: 150ms; }
.duration-normal { transition-duration: 300ms; }
.duration-slow { transition-duration: 500ms; }
```

## 核心页面设计

### 1. 主布局设计

```typescript
// components/layout/MainLayout.tsx
interface MainLayoutProps {
  children: React.ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-bg-primary">
      {/* 顶部导航栏 */}
      <Header />
      
      <div className="flex">
        {/* 侧边栏 */}
        <Sidebar />
        
        {/* 主内容区 */}
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
      
      {/* 全局组件 */}
      <DownloadQueue />
      <NotificationCenter />
      <SettingsModal />
    </div>
  );
}
```

### 2. 单视频下载页面

#### 页面布局
```typescript
// app/download/page.tsx
export default function DownloadPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* 页面标题 */}
      <div className="text-center">
        <h1 className="text-h1 text-gray-900 mb-2">
          YouTube视频下载
        </h1>
        <p className="text-body text-gray-600">
          输入YouTube视频链接，选择格式和质量进行下载
        </p>
      </div>
      
      {/* URL输入区域 */}
      <URLInputSection />
      
      {/* 视频预览区域 */}
      <VideoPreviewSection />
      
      {/* 下载配置区域 */}
      <DownloadConfigSection />
      
      {/* 下载按钮 */}
      <DownloadActionSection />
    </div>
  );
}
```

#### 核心组件设计

**URL输入组件**
```typescript
// components/download/URLInput.tsx
export function URLInputSection() {
  const [url, setUrl] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);

  return (
    <Card className="p-6">
      <div className="space-y-4">
        <Label htmlFor="url-input" className="text-h2">
          视频链接
        </Label>
        
        <div className="relative">
          <Input
            id="url-input"
            type="url"
            placeholder="请输入YouTube视频链接..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="text-lg py-4 pr-12"
          />
          
          {/* 验证状态指示器 */}
          <div className="absolute right-3 top-1/2 -translate-y-1/2">
            {isValidating && <Spinner className="w-5 h-5" />}
            {validationResult?.isValid && (
              <CheckIcon className="w-5 h-5 text-success" />
            )}
            {validationResult?.isValid === false && (
              <XMarkIcon className="w-5 h-5 text-error" />
            )}
          </div>
        </div>
        
        {/* 快捷粘贴按钮 */}
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm"
            onClick={handlePasteFromClipboard}
          >
            <ClipboardIcon className="w-4 h-4 mr-1" />
            粘贴
          </Button>
          
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleClearInput}
          >
            清空
          </Button>
        </div>
        
        {/* 验证错误信息 */}
        {validationResult?.error && (
          <Alert variant="error">
            {validationResult.error}
          </Alert>
        )}
      </div>
    </Card>
  );
}
```

**视频预览组件**
```typescript
// components/download/VideoPreview.tsx
export function VideoPreviewSection() {
  const { videoInfo, isLoading, error } = useVideoInfo();
  
  if (!videoInfo) return null;
  
  return (
    <Card className="overflow-hidden">
      <div className="md:flex">
        {/* 缩略图 */}
        <div className="md:w-1/3">
          <img 
            src={videoInfo.thumbnail}
            alt={videoInfo.title}
            className="w-full h-48 md:h-full object-cover"
          />
        </div>
        
        {/* 视频信息 */}
        <div className="p-6 md:w-2/3">
          <h3 className="text-h2 mb-2 line-clamp-2">
            {videoInfo.title}
          </h3>
          
          <div className="space-y-2 text-body text-gray-600">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <ClockIcon className="w-4 h-4" />
                {formatDuration(videoInfo.duration)}
              </span>
              
              <span className="flex items-center gap-1">
                <EyeIcon className="w-4 h-4" />
                {formatNumber(videoInfo.viewCount)} 次观看
              </span>
            </div>
            
            <div className="flex items-center gap-1">
              <UserIcon className="w-4 h-4" />
              {videoInfo.uploader}
            </div>
            
            <div className="flex items-center gap-1">
              <CalendarIcon className="w-4 h-4" />
              {formatDate(videoInfo.uploadDate)}
            </div>
          </div>
          
          {/* 可用格式预览 */}
          <div className="mt-4">
            <p className="text-caption text-gray-500 mb-2">可用格式:</p>
            <div className="flex flex-wrap gap-1">
              {videoInfo.availableFormats.map((format) => (
                <Badge key={format.formatId} variant="secondary">
                  {format.quality} - {format.ext}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}
```

### 3. 批量搜索下载页面

#### 页面布局
```typescript
// app/batch/page.tsx
export default function BatchDownloadPage() {
  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* 页面标题 */}
      <div className="text-center">
        <h1 className="text-h1 text-gray-900 mb-2">
          批量搜索下载
        </h1>
        <p className="text-body text-gray-600">
          通过关键词搜索YouTube视频，批量下载符合条件的内容
        </p>
      </div>
      
      {/* 搜索和过滤区域 */}
      <div className="grid lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3">
          <SearchInputSection />
        </div>
        <div>
          <FilterPanel />
        </div>
      </div>
      
      {/* 搜索结果区域 */}
      <SearchResultsSection />
      
      {/* 批量操作工具栏 */}
      <BatchToolbar />
      
      {/* 批量下载进度 */}
      <BatchProgressSection />
    </div>
  );
}
```

#### 核心组件设计

**搜索输入组件**
```typescript
// components/batch/SearchInput.tsx
export function SearchInputSection() {
  const [query, setQuery] = useState('');
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const { mutate: search, isLoading } = useSearch();

  return (
    <Card className="p-6">
      <div className="space-y-4">
        <Label className="text-h2">搜索关键词</Label>
        
        <div className="relative">
          <div className="relative">
            <Input
              type="text"
              placeholder="输入搜索关键词，如：Python教程、机器学习..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="text-lg py-4 pr-12"
            />
            
            <Button
              onClick={handleSearch}
              disabled={!query.trim() || isLoading}
              className="absolute right-2 top-1/2 -translate-y-1/2"
              size="sm"
            >
              {isLoading ? (
                <Spinner className="w-4 h-4" />
              ) : (
                <MagnifyingGlassIcon className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>
        
        {/* 搜索历史 */}
        {searchHistory.length > 0 && (
          <div>
            <p className="text-caption text-gray-500 mb-2">最近搜索:</p>
            <div className="flex flex-wrap gap-2">
              {searchHistory.map((term, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => setQuery(term)}
                  className="text-xs"
                >
                  {term}
                </Button>
              ))}
            </div>
          </div>
        )}
        
        {/* 快速搜索建议 */}
        <div>
          <p className="text-caption text-gray-500 mb-2">推荐搜索:</p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTED_SEARCHES.map((suggestion) => (
              <Button
                key={suggestion}
                variant="ghost"
                size="sm"
                onClick={() => setQuery(suggestion)}
                className="text-xs"
              >
                {suggestion}
              </Button>
            ))}
          </div>
        </div>
      </div>
    </Card>
  );
}
```

**过滤面板组件**
```typescript
// components/batch/FilterPanel.tsx
export function FilterPanel() {
  const { filters, updateFilters } = useSearchStore();

  return (
    <Card className="p-6 sticky top-6">
      <div className="space-y-6">
        <h3 className="text-h2">搜索过滤</h3>
        
        {/* 排序方式 */}
        <div>
          <Label className="mb-2">排序方式</Label>
          <Select
            value={filters.sortBy}
            onValueChange={(value) => updateFilters({ sortBy: value })}
          >
            <SelectItem value="relevance">相关性</SelectItem>
            <SelectItem value="upload_date">上传时间</SelectItem>
            <SelectItem value="view_count">观看量</SelectItem>
            <SelectItem value="rating">评分</SelectItem>
          </Select>
        </div>
        
        {/* 时长过滤 */}
        <div>
          <Label className="mb-2">视频时长</Label>
          <div className="space-y-3">
            <DualRangeSlider
              min={0}
              max={7200}
              value={[filters.minDuration || 0, filters.maxDuration || 7200]}
              onValueChange={([min, max]) => 
                updateFilters({ minDuration: min, maxDuration: max })
              }
              formatLabel={(value) => formatDuration(value)}
            />
            
            <div className="flex justify-between text-caption text-gray-500">
              <span>{formatDuration(filters.minDuration || 0)}</span>
              <span>{formatDuration(filters.maxDuration || 7200)}</span>
            </div>
          </div>
        </div>
        
        {/* 上传时间 */}
        <div>
          <Label className="mb-2">上传时间</Label>
          <Select
            value={filters.uploadDate}
            onValueChange={(value) => updateFilters({ uploadDate: value })}
          >
            <SelectItem value="any">不限</SelectItem>
            <SelectItem value="hour">最近1小时</SelectItem>
            <SelectItem value="today">今天</SelectItem>
            <SelectItem value="week">最近一周</SelectItem>
            <SelectItem value="month">最近一个月</SelectItem>
            <SelectItem value="year">最近一年</SelectItem>
          </Select>
        </div>
        
        {/* 其他过滤选项 */}
        <div className="space-y-3">
          <Label>内容过滤</Label>
          
          <Checkbox
            checked={filters.excludeShorts}
            onCheckedChange={(checked) => 
              updateFilters({ excludeShorts: checked })
            }
          >
            排除YouTube Shorts
          </Checkbox>
          
          <Checkbox
            checked={filters.excludeLive}
            onCheckedChange={(checked) => 
              updateFilters({ excludeLive: checked })
            }
          >
            排除直播内容
          </Checkbox>
        </div>
        
        {/* 最小观看量 */}
        <div>
          <Label className="mb-2">最小观看量</Label>
          <Input
            type="number"
            placeholder="例如: 10000"
            value={filters.minViewCount || ''}
            onChange={(e) => 
              updateFilters({ minViewCount: parseInt(e.target.value) || undefined })
            }
          />
        </div>
        
        {/* 重置按钮 */}
        <Button
          variant="outline"
          onClick={() => updateFilters({})}
          className="w-full"
        >
          重置过滤条件
        </Button>
      </div>
    </Card>
  );
}
```

## 状态管理设计

### 下载状态管理
```typescript
// stores/downloadStore.ts
interface DownloadState {
  // 下载队列
  queue: DownloadTask[];
  
  // 当前下载任务
  currentDownloads: DownloadTask[];
  
  // 下载历史
  history: DownloadTask[];
  
  // 全局设置
  settings: DownloadSettings;
}

interface DownloadTask {
  id: string;
  url: string;
  title: string;
  status: 'pending' | 'downloading' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  speed?: string;
  eta?: string;
  error?: string;
  filePath?: string;
  createdAt: Date;
  completedAt?: Date;
}

export const useDownloadStore = create<DownloadState & DownloadActions>((set, get) => ({
  queue: [],
  currentDownloads: [],
  history: [],
  settings: DEFAULT_SETTINGS,
  
  // Actions
  addToQueue: (task: Omit<DownloadTask, 'id' | 'createdAt'>) => {
    const newTask: DownloadTask = {
      ...task,
      id: generateId(),
      createdAt: new Date(),
    };
    
    set((state) => ({
      queue: [...state.queue, newTask]
    }));
  },
  
  updateProgress: (taskId: string, progress: number, speed?: string, eta?: string) => {
    set((state) => ({
      currentDownloads: state.currentDownloads.map(task =>
        task.id === taskId 
          ? { ...task, progress, speed, eta }
          : task
      )
    }));
  },
  
  completeDownload: (taskId: string, filePath: string) => {
    set((state) => {
      const task = state.currentDownloads.find(t => t.id === taskId);
      if (!task) return state;
      
      const completedTask = {
        ...task,
        status: 'completed' as const,
        progress: 100,
        filePath,
        completedAt: new Date()
      };
      
      return {
        currentDownloads: state.currentDownloads.filter(t => t.id !== taskId),
        history: [completedTask, ...state.history]
      };
    });
  },
}));
```

### 搜索状态管理
```typescript
// stores/searchStore.ts
interface SearchState {
  // 搜索查询
  query: string;
  
  // 搜索结果
  results: VideoSearchResult[];
  
  // 搜索状态
  isLoading: boolean;
  error: string | null;
  
  // 过滤条件
  filters: SearchFilters;
  
  // 选中的视频
  selectedVideos: string[];
  
  // 搜索历史
  searchHistory: string[];
}

export const useSearchStore = create<SearchState & SearchActions>((set, get) => ({
  query: '',
  results: [],
  isLoading: false,
  error: null,
  filters: DEFAULT_FILTERS,
  selectedVideos: [],
  searchHistory: [],
  
  // Actions
  setQuery: (query: string) => set({ query }),
  
  performSearch: async (query: string) => {
    set({ isLoading: true, error: null });
    
    try {
      const results = await searchAPI.search(query, get().filters);
      set({ 
        results, 
        isLoading: false,
        searchHistory: [query, ...get().searchHistory.filter(h => h !== query)].slice(0, 10)
      });
    } catch (error) {
      set({ 
        error: error.message, 
        isLoading: false 
      });
    }
  },
  
  updateFilters: (newFilters: Partial<SearchFilters>) => {
    set((state) => ({
      filters: { ...state.filters, ...newFilters }
    }));
  },
  
  toggleVideoSelection: (videoId: string) => {
    set((state) => ({
      selectedVideos: state.selectedVideos.includes(videoId)
        ? state.selectedVideos.filter(id => id !== videoId)
        : [...state.selectedVideos, videoId]
    }));
  },
}));
```

## 实时通信设计

### WebSocket集成
```typescript
// hooks/useWebSocket.ts
export function useWebSocket() {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  
  const { updateProgress, completeDownload, failDownload } = useDownloadStore();
  
  useEffect(() => {
    const newSocket = io(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000');
    
    newSocket.on('connect', () => {
      setIsConnected(true);
      console.log('WebSocket connected');
    });
    
    newSocket.on('disconnect', () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
    });
    
    // 下载进度更新
    newSocket.on('download_progress', (data: {
      taskId: string;
      progress: number;
      speed: string;
      eta: string;
    }) => {
      updateProgress(data.taskId, data.progress, data.speed, data.eta);
    });
    
    // 下载完成
    newSocket.on('download_complete', (data: {
      taskId: string;
      filePath: string;
    }) => {
      completeDownload(data.taskId, data.filePath);
    });
    
    // 下载失败
    newSocket.on('download_error', (data: {
      taskId: string;
      error: string;
    }) => {
      failDownload(data.taskId, data.error);
    });
    
    setSocket(newSocket);
    
    return () => {
      newSocket.close();
    };
  }, []);
  
  return { socket, isConnected };
}
```

## 性能优化策略

### 1. 代码分割和懒加载
```typescript
// app/layout.tsx
const BatchDownloadPage = dynamic(() => import('./batch/page'), {
  loading: () => <PageSkeleton />,
  ssr: false
});

const HistoryPage = dynamic(() => import('./history/page'), {
  loading: () => <PageSkeleton />,
  ssr: false
});
```

### 2. 图片优化
```typescript
// components/VideoThumbnail.tsx
import Image from 'next/image';

export function VideoThumbnail({ src, alt, className }: ThumbnailProps) {
  return (
    <Image
      src={src}
      alt={alt}
      width={320}
      height={180}
      className={cn('object-cover', className)}
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
    />
  );
}
```

### 3. 虚拟化长列表
```typescript
// components/batch/VideoGrid.tsx
import { FixedSizeGrid as Grid } from 'react-window';

export function VideoGrid({ videos }: VideoGridProps) {
  const itemCount = videos.length;
  const columnCount = Math.floor(containerWidth / ITEM_WIDTH);
  const rowCount = Math.ceil(itemCount / columnCount);
  
  return (
    <Grid
      columnCount={columnCount}
      columnWidth={ITEM_WIDTH}
      height={600}
      rowCount={rowCount}
      rowHeight={ITEM_HEIGHT}
      width={containerWidth}
      itemData={{ videos, columnCount }}
    >
      {VideoGridItem}
    </Grid>
  );
}
```

## 开发实施计划

### Phase 1: 基础架构搭建
- [x] Next.js项目初始化
- [x] 基础UI组件库搭建
- [x] 设计系统实现
- [x] 路由结构设计
- [x] 状态管理架构

### Phase 2: 单视频下载功能
- [ ] URL输入和验证组件
- [ ] 视频预览组件
- [ ] 下载配置组件
- [ ] 下载进度追踪
- [ ] WebSocket集成

### Phase 3: 批量搜索下载功能
- [ ] 搜索输入组件
- [ ] 过滤面板组件
- [ ] 搜索结果展示
- [ ] 批量选择功能
- [ ] 批量下载管理

### Phase 4: 高级功能
- [ ] 下载历史管理
- [ ] 设置面板
- [ ] 主题切换
- [ ] 国际化支持
- [ ] PWA功能

### Phase 5: 优化和测试
- [ ] 性能优化
- [ ] 无障碍访问
- [ ] 跨浏览器测试
- [ ] 移动端适配
- [ ] 用户体验测试

## 质量保证

### 测试策略
```typescript
// 单元测试示例
// __tests__/components/URLInput.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { URLInput } from '@/components/download/URLInput';

describe('URLInput Component', () => {
  it('validates YouTube URL correctly', async () => {
    render(<URLInput />);
    
    const input = screen.getByPlaceholderText(/输入YouTube视频链接/);
    fireEvent.change(input, { 
      target: { value: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' } 
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('validation-success')).toBeInTheDocument();
    });
  });
  
  it('shows error for invalid URL', async () => {
    render(<URLInput />);
    
    const input = screen.getByPlaceholderText(/输入YouTube视频链接/);
    fireEvent.change(input, { 
      target: { value: 'invalid-url' } 
    });
    
    await waitFor(() => {
      expect(screen.getByTestId('validation-error')).toBeInTheDocument();
    });
  });
});
```

### 代码质量工具
```json
// package.json
{
  "scripts": {
    "lint": "next lint",
    "lint:fix": "next lint --fix",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  },
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged",
      "pre-push": "npm run type-check && npm run test"
    }
  },
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ]
  }
}
```

## 部署策略

### 生产环境部署
```dockerfile
# Dockerfile
FROM node:18-alpine AS base

# Install dependencies
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Build the app
FROM base AS builder
WORKDIR /app
COPY . .
COPY --from=deps /app/node_modules ./node_modules
RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app
ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
```

### CI/CD流程
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check
      - run: npm run test -- --coverage
      
  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push Docker image
        run: |
          docker build -t youtube-downloader-web .
          docker push ${{ secrets.DOCKER_REGISTRY }}/youtube-downloader-web:latest
      - name: Deploy to production
        run: |
          # 部署脚本
```

## 总结

这个Web前端设计方案基于现代化的技术栈和最佳实践，提供了：

- 🎨 **美观优雅的界面设计**：采用Material Design 3设计语言
- ⚡ **高性能的用户体验**：代码分割、虚拟化、图片优化
- 📱 **全面的响应式支持**：适配各种设备和屏幕尺寸
- 🔄 **实时的状态同步**：WebSocket实现进度实时更新
- 🧩 **模块化的组件架构**：易于维护和扩展
- ♿ **完整的无障碍支持**：符合WCAG标准