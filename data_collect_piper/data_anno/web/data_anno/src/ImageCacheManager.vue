<template>
  <button @click="downloadAndStoreImages(urlList)">load_images</button>
  <button @click="clearEntireDatabase">clear_database</button>
  <span>已加载图片数量: {{ imageMap.size }} / {{ urlList.length }}</span>
</template>

<script>
import Dexie from 'dexie'

// 初始化数据库
const db = new Dexie('ImageDatabase')
db.version(1).stores({ images: 'url' })

export default {
  props: {
    urlList: {
      type: Array,
      required: true,
    },
    imageUrls: {
      type: Map,
      required: true,
    },
  },

  data: () => ({
    imageMap: new Map(),
    isDownloading: false,
    currentProgress: 0,
  }),

  async mounted() {
    await this.initializeDatabase()
  },

  methods: {
    // 初始化数据库
    async initializeDatabase() {
      try {
        await db.open()
        await this.loadExistingImages()
      } catch (error) {
        console.error('数据库初始化失败:', error)
      }
    },

    // 加载已有数据
    async loadExistingImages() {
      const records = await db.images.toArray()
      const newUrlMap = new Map()

      records.forEach((record) => {
        const objectURL = URL.createObjectURL(record.blob)
        newUrlMap.set(record.url, objectURL)
      })

      this.imageMap = new Map(records.map((r) => [r.url, r.blob]))
      // this.imageUrls = newUrlMap;
      this.$emit('update:imageUrls', newUrlMap)
    },

    updateImageUrl(url, blob) {
      // 先撤销旧URL（如果存在）
      if (this.imageUrls.has(url)) {
        URL.revokeObjectURL(this.imageUrls.get(url))
      }
      const newUrl = URL.createObjectURL(blob)
      // this.imageUrls = new Map([...this.imageUrls, [url, newUrl]]);
      const new_map = new Map([...this.imageUrls, [url, newUrl]])
      this.$emit('update:imageUrls', new_map)
    },

    // 主下载方法（串行版）
    async downloadAndStoreImages(urlList) {
      if (this.isDownloading) return

      this.isDownloading = true
      this.currentProgress = 0
      const uniqueUrls = [...new Set(urlList)]

      try {
        for (const [index, url] of uniqueUrls.entries()) {
          await this.processSingleImage(url)
          this.currentProgress = Math.round(((index + 1) * 100) / uniqueUrls.length)
        }
      } catch (error) {
        console.error('下载流程中断:', error)
      } finally {
        this.isDownloading = false
        this.currentProgress = 0
      }
    },

    // 单个图片处理流程
    async processSingleImage(url) {
      try {
        if (this.imageMap.has(url)) return

        const blob = await this.retryableDownload(url, {
          retries: 3,
          delay: 1000,
        })

        await db.images.put({ url, blob })
        this.imageMap = new Map([...this.imageMap, [url, blob]])
        this.updateImageUrl(url, blob)
      } catch (error) {
        console.warn(`下载失败: ${url}`, error.message)
      }
    },

    // 可重试的下载方法
    async retryableDownload(url, { retries, delay }) {
      for (let attempt = 1; attempt <= retries; attempt++) {
        try {
          return await this.fetchImage(url)
        } catch (error) {
          if (attempt === retries) throw error
          await new Promise((r) => setTimeout(r, delay * attempt))
        }
      }
    },

    // 实际获取图片
    async fetchImage(url) {
      const response = await fetch(url)
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      return await response.blob()
    },

    // 更新内存映射
    updateImageMap(url, blob) {
      // this.imageMap = new Map(this.imageMap).set(url, blob)
      const new_map = new Map(this.imageMap).set(url, blob)
      this.$emit('update:imageMap', new_map)
    },

    async clearEntireDatabase() {
      try {
        await db.images.clear();
        this.cleanupMemoryResources();
        console.log('数据库已完全清空');
      } catch (error) {
        console.error('清空数据库失败:', error);
        throw error;
      }
    },

    cleanupMemoryResources() {
      // 释放所有ObjectURL
      this.imageUrls.forEach(url => URL.revokeObjectURL(url));
      // 清空内存映射
      this.imageMap = new Map();
      // this.imageUrls = new Map();
      this.$emit('update:imageUrls', new Map());
    },
  },
  beforeUnmount() {
    this.imageUrls.forEach((url) => URL.revokeObjectURL(url))
  },
}
</script>
