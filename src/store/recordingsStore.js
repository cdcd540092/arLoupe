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
        loading.value = true;
        try {
            // 目前先模擬延遲
            await new Promise(resolve => setTimeout(resolve, 800));
            // 未來範例：
            // const response = await axios.get('/api/recordings/', { params: { search: searchQuery.value, type: selectedType.value } });
            // items.value = response.data;
        } catch (error) {
            console.error('Failed to fetch recordings:', error);
        } finally {
            loading.value = false;
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
