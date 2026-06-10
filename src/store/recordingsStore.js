import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useRecordingsStore = defineStore('recordings', () => {
    // 原始數據
    const items = ref([
        { id: 1, patientName: 'John Doe', patientId: 'P-101', date: '2026-04-07', time: '14:30', operatory: 'Op 1', procedures: 'Cleaning', tags: ['High Risk', 'Bleeding'], markers: [], videoUrl: '/procedure_demo.mp4' },
        { id: 2, patientName: 'Alice Smith', patientId: 'P-992', date: '2026-04-06', time: '09:15', operatory: 'Op 2', procedures: 'Extraction', tags: ['Routine'], markers: [], videoUrl: '/procedure_demo.mp4' },
        { id: 3, patientName: 'Bob Wilson', patientId: 'P-342', date: '2026-03-31', time: '11:00', operatory: 'Op 1', procedures: 'Implant', tags: [], markers: [], videoUrl: '/procedure_demo.mp4' },
        { id: 4, patientName: 'Sarah Connor', patientId: 'P-887', date: '2026-03-30', time: '16:45', operatory: 'Op 3', procedures: 'Cleaning', tags: ['Allergy'], markers: [], videoUrl: '/procedure_demo.mp4' },
        { id: 5, patientName: 'Michael Corleone', patientId: 'P-554', date: '2026-04-08', time: '10:00', operatory: 'Op 1', procedures: 'Implant', tags: [], markers: [], videoUrl: '/procedure_demo.mp4' },
        { id: 6, patientName: 'Ellen Ripley', patientId: 'P-776', date: '2026-04-09', time: '13:20', operatory: 'Op 2', procedures: 'Cleaning', tags: [], markers: [], videoUrl: '/procedure_demo.mp4' }
    ]);

    // 模擬 PMS 系統自動帶入的當前活躍病患
    const activePatientFromPMS = ref({
        patientName: '王大明',
        patientId: 'P-101',
        operatory: 'Op 1',
        procedures: 'Root Canal'
    });

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
            const matchesSearch = item.patientName.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                                  (item.patientId && item.patientId.toLowerCase().includes(searchQuery.value.toLowerCase()));
            const matchesType = selectedType.value === 'All' || item.procedures === selectedType.value;
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
                    let title = v.title || `API Video ${v.id}`;
                    let parsedPatientName = title;
                    let parsedPatientId = 'Unknown';
                    let parsedProcedures = 'Cloud Sync';
                    let parsedDate = v.created_at ? v.created_at.split('T')[0] : new Date().toISOString().split('T')[0];
                    let parsedOperatory = 'Op 1'; // 預設給個診間
                    
                    // 嘗試解析格式：李明輝_P-554_根管治療_20260520
                    if (title.includes('_')) {
                        const parts = title.split('_');
                        if (parts.length >= 3) {
                            parsedPatientName = parts[0];
                            parsedPatientId = parts[1];
                            parsedProcedures = parts[2];
                            if (parts.length >= 4) {
                                const dateStr = parts[3];
                                if (dateStr.length === 8) {
                                    parsedDate = `${dateStr.substring(0,4)}-${dateStr.substring(4,6)}-${dateStr.substring(6,8)}`;
                                }
                            }
                        }
                    }

                    return {
                        id: v.id,
                        patientName: parsedPatientName,
                        patientId: parsedPatientId,
                        date: parsedDate,
                        time: v.created_at ? v.created_at.split('T')[1].substring(0, 5) : '00:00',
                        operatory: parsedOperatory,
                        procedures: parsedProcedures,
                        tags: [],
                        markers: [],
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
        activePatientFromPMS,
        filteredRecordings,
        fetchRecordings,
        saveClipToDatabase,
        resetFilters
    };
});
