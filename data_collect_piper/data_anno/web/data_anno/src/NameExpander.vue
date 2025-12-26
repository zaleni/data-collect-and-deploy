<template>
  <div class="container">
    <div class="trigger" @click="togglePanel">
      {{ triggerText }}
    </div>

    <div v-if="isExpanded" class="panel">
      <div class="item" v-for="(item, index) in items" :key="index">
        <img :src="item.image" class="item-image" />
        <span class="item-text">{{ item.text }}</span>
      </div>
    </div>
  </div>
</template>

<script>
const image =
  'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAIAAADTED8xAAADMElEQVR4nOzVwQnAIBQFQYXff81RUkQCOyDj1YOPnbXWPmeTRef+/3O/OyBjzh3CD95BfqICMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMO0TAAD//2Anhf4QtqobAAAAAElFTkSuQmCC'

export default {
  data() {
    return {
      isExpanded: false,
      triggerText: '物品名称',
      items: [
        { image: image, text: '玫瑰' },
        { image: image, text: '书籍' },
        { image: image, text: '茶杯' },
      ],
    }
  },
  methods: {
    togglePanel() {
      this.isExpanded = !this.isExpanded
    },
  },
}
</script>

<style scoped>
.container {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  /* height: 10vh; */
  height: fit-content;
}

.trigger {
  padding: 12px 20px;
  background-color: #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  text-align: center;
  transition: background-color 0.3s;

  /* 新增样式 */
  width: fit-content; /* 宽度自适应内容 */
  margin: 0 auto; /* 水平居中 */
  padding: 0 20px; /* 仅水平内边距 */
  line-height: 1.5; /* 保持文本自然高度 */
  height: fit-content;
}

.trigger:hover {
  background-color: #e0e0e0;
}

.panel {
  position: absolute;
  bottom: 100%;
  left: 0;
  width: 100%;
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  gap: 20px;
  overflow-x: auto;

  position: absolute;
  bottom: calc(100% + 10px); /* 在trigger上方保留10px间隙 */
  left: 0;
}

.item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 120px;
}

.item-image {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 8px;
}

.item-text {
  font-size: 14px;
  color: #666;
}
</style>
