import axios from 'axios';
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

    // 未來對接 Django 的 API 呼叫方法
    async function fetchRecordings() {
        this.loading = true;
        try {
            const response = await axios.get('http://127.0.0.1:8000/api/videos/');
            
            // 把 Django 回傳的資料對應到 Vue 預期顯示的格式
            this.recordings = response.data.map(video => ({
            id: video.id,
            patientName: video.title, // 把影片標題顯示在病患姓名位置
            type: "Django Video",
            date: new Date(video.created_at).toLocaleDateString(),
            videoUrl: video.file  // 重要：確保這裡叫 videoUrl，對應 VideoPlayer.vue
            }));
            
            if (this.recordings.length > 0 && !this.selectedId) {
            this.selectedId = this.recordings[0].id;
            }
        } catch (error) {
            console.error("無法連線到 Django:", error);
        } finally {
            this.loading = false;
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
        resetFilters
    };
});
