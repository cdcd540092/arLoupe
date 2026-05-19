import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useRecordingsStore = defineStore('recordings', () => {
    // 原始數據
    const items = ref([
        { id: 1, patientName: 'John Doe (P-101)', date: '2026-04-07', type: 'Cleaning', videoUrl: '/procedure_demo.mp4' },
        { id: 2, patientName: 'Alice Smith (P-992)', date: '2026-04-06', type: 'Extraction', videoUrl: '/procedure_demo.mp4' },
        { id: 3, patientName: 'Bob Wilson (P-342)', date: '2026-03-31', type: 'Implant', videoUrl: '/procedure_demo.mp4' },
        { id: 4, patientName: 'Sarah Connor (P-887)', date: '2026-03-30', type: 'Cleaning', videoUrl: '/procedure_demo.mp4' },
        { id: 5, patientName: 'Michael Corleone (P-554)', date: '2026-04-08', type: 'Implant', videoUrl: '/procedure_demo.mp4' },
        { id: 6, patientName: 'Ellen Ripley (P-776)', date: '2026-04-09', type: 'Cleaning', videoUrl: '/procedure_demo.mp4' }
    ]);

    const loading = ref(false);
    const searchQuery = ref('');
    const selectedType = ref('All');
    const selectedDate = ref('');
    const selectedId = ref(1);

    // 目前選中的錄影物件
    const currentRecording = computed(() => {
        return items.value.find(item => item.id === selectedId.value) || items.value[0];
    });

    // 過濾後的清單
    const filteredRecordings = computed(() => {
        return items.value.filter(item => {
            const matchesSearch = item.patientName.toLowerCase().includes(searchQuery.value.toLowerCase());
            const matchesType = selectedType.value === 'All' || item.type === selectedType.value;
            const matchesDate = !selectedDate.value || item.date === selectedDate.value;
            return matchesSearch && matchesType && matchesDate;
        });
    });

    async function fetchRecordings() {
        loading.value = true;
        try {
            const response = await fetch('/api/videos/');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            
            if (data && data.length > 0) {
                // 將 Django 的資料結構對應回前端預期的格式
                items.value = data.map(v => {
                    // 去除 Django 回傳的絕對主機位址，改由前端 proxy 處理，避免 COEP 跨域問題
                    let videoUrl = v.file;
                    if (videoUrl.includes('8000')) {
                        videoUrl = new URL(videoUrl).pathname;
                    }
                    return {
                        id: v.id,
                        patientName: v.title || `API Video ${v.id}`,
                        date: v.created_at ? v.created_at.split('T')[0] : new Date().toISOString().split('T')[0],
                        type: 'Cloud Sync',
                        videoUrl: videoUrl 
                    };
                });
                // 自動選取第一個
                selectedId.value = items.value[0].id;
            } else {
                console.warn('Django API 返回了空陣列');
            }
        } catch (error) {
            console.error('Failed to fetch from Django API:', error);
            // 發生錯誤時先不蓋掉原本的 Mock 資料，方便預覽
        } finally {
            loading.value = false;
        }
    }

    async function saveClipToDatabase(clip) {
        try {
            let blobData;
            if (clip.physicalBlobUrl) {
                // 如果前端 FFmpeg 已成功生成實體剪輯，抓取這個 Blob
                const response = await fetch(clip.physicalBlobUrl);
                blobData = await response.blob();
            } else {
                // Fallback: 如果沒有實體剪輯，抓取原始影片檔案
                const currentRec = currentRecording.value;
                const response = await fetch(currentRec.videoUrl.split('#')[0]);
                blobData = await response.blob();
            }

            // 打包成 FormData 發送給 Django
            const formData = new FormData();
            formData.append('title', `[片段] ${clip.name}`);
            formData.append('file', blobData, `clip_${Date.now()}.mp4`);

            const uploadRes = await fetch('/api/videos/', {
                method: 'POST',
                body: formData
            });

            if (!uploadRes.ok) throw new Error('上傳伺服器失敗');

            // 重新向後端拉取最新清單，這會自動包含剛上傳的片段
            await fetchRecordings();
            
            return { success: true, message: 'Saved to DB' };
        } catch (error) {
            console.error('儲存片段至資料庫時發生錯誤:', error);
            throw error;
        }
    }

    function resetFilters() {
        searchQuery.value = '';
        selectedType.value = 'All';
        selectedDate.value = '';
    }

    return {
        items,
        loading,
        searchQuery,
        selectedType,
        selectedDate,
        selectedId,
        currentRecording,
        filteredRecordings,
        fetchRecordings,
        saveClipToDatabase,
        resetFilters
    };
});
