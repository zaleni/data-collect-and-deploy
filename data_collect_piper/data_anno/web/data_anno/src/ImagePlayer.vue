<template>
  <div class="image-container">
    <img :src="currentFrontFrame" class="frame" />
    <img :src="currentWristFrame" class="frame" />
  </div>

  <div class="controls">
    <button @click="playPause">{{ isPlaying ? '暂停' : '播放' }}</button>
    <button @click="stepFrame(-5)">-5</button>
    <button @click="stepFrame(-1)">-1</button>
    <button @click="stepFrame(1)">+1</button>
    <button @click="stepFrame(5)">+5</button>
    <input type="range" min="1" max="100" v-model="fps" /> <span>FPS: {{ fps }}</span>
    <span>当前帧：{{ currentFrameIndex }} / {{ frames.length }}</span>
  </div>
</template>

<script>
import constants from './constants'
const BaseURL = constants.BaseUrl
export default {
  props: ['frames', 'task_name', 'currentFrameIndex', 'imageMap'],
  emits: ['update:currentFrameIndex'],
  data() {
    return {
      isPlaying: false,
      timeout_id: null,
      fps: 10,
    }
  },
  computed: {
    currentFrontFrame() {
      return this.try_load_from_indexdb(
        `${BaseURL}/tasks/${this.task_name}/img/front_color/${this.frames[this.currentFrameIndex]?.[0]}`,
      )
    },
    currentWristFrame() {
      return this.try_load_from_indexdb(
        `${BaseURL}/tasks/${this.task_name}/img/wrist_color/${this.frames[this.currentFrameIndex]?.[1]}`,
      )
    },
  },

  methods: {
    playPause() {
      this.isPlaying = !this.isPlaying
      if (this.isPlaying) {
        this.timeout_id = setInterval(() => {
          this.stepFrame(1)
        }, 1000 / this.fps)
      } else {
        clearInterval(this.timeout_id)
      }
    },
    stepFrame(step) {
      let new_index = this.currentFrameIndex + step
      new_index = Math.max(0, Math.min(this.frames.length - 1, new_index))
      this.$emit('update:currentFrameIndex', new_index)
    },
    handleKeyDown(event) {
      // A for previous, D for next
      const isInputElement = ['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)
      if (isInputElement) return
      if (event.key === 'a') {
        this.stepFrame(-1)
      } else if (event.key === 'd') {
        this.stepFrame(1)
      } else if (event.key === 'w') {
        this.stepFrame(5)
      } else if (event.key === 's') {
        this.stepFrame(-5)
      } else if (event.key === ' ') {
        this.playPause()
      }
    },
    try_load_from_indexdb(url) {
      if (this.imageMap.has(url)) {
        return this.imageMap.get(url)
      }
      return url
    },
  },
  mounted() {
    window.addEventListener('keydown', this.handleKeyDown)
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.handleKeyDown)
  },
}
</script>

<style scoped>
.image-container {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.frame {
  width: 640px;
  height: 360px;
  object-fit: contain;
  border: 1px solid #ddd;
}

.controls {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}
</style>
