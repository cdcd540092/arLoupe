import { defineStore } from 'pinia';

export const useImagingStore = defineStore('imaging', {
    state: () => ({
        images: [],
        loading: false,
        selectedImage: null,
        metadata: {}
    }),
    actions: {
        async fetchImages() {
            // API call placeholder
            this.loading = true;
            try {
                // const response = await api.getImages();
                // this.images = response.data;
            } finally {
                this.loading = false;
            }
        },
        selectImage(image) {
            this.selectedImage = image;
        }
    }
});
