<template>
  <div class="container">
    <TaskList
      :items="taskList"
      @node-click="fetchTask"
      @refresh="fetchTaskList"
      @reload="require_reload"
    />

    <!-- 主内容区 -->
    <div class="main-content" v-if="currentTask.task_name.length !== 0">
      <ImagePlayer
        :frames="currentTask.frames"
        :task_name="currentTask.task_name"
        :image-map="imageMap"
        v-model:current-frame-index="currentFrameIndex"
      ></ImagePlayer>

      <TineLine
        :n="currentTask.frames.length"
        :spans="currentTask.spans ?? []"
        :progress="currentFrameIndex"
        :current-span="currentSpan"
        :is-editing="isEditing"
        @span-click="selectCurrentSpan"
        @jump-to="currentFrameIndex = $event"
      ></TineLine>

      <!-- 标注功能 -->
      <div class="annotation-controls">
        <div>
          <button
            @click="setStartFrame"
            :disabled="!(!isEditing && currentSpan.start_index === -1)"
          >
            设为起始
          </button>
          <button @click="setEndFrame" :disabled="!isEditing">设为结束</button>
          <button @click="saveAnnotation" :disabled="!(currentSpan.end_index !== -1)">
            保存标注
          </button>
          <button
            @click="resetAnnotationState"
            :disabled="!(!isEditing && currentSpan.start_index !== -1)"
          >
            取消选择
          </button>
          <button
            @click="deleteAnnotation"
            :disabled="!(!isEditing && currentSpan.start_index !== -1)"
          >
            删除选中
          </button>

          <ImageCacheManager
            :urlList="allImageUrls"
            v-model:imageUrls="imageMap"
          ></ImageCacheManager>
        </div>

        <div>
          <input v-model="currentSpan.annotation" placeholder="输入注解" />
          <label>
            <input type="checkbox" v-model="currentSpan.used_for_vlm" />
            用于VLM
          </label>
        </div>
      </div>

      <SpanList
        :current-task="currentTask"
        :current-span="currentSpan"
        @span-selected="selectCurrentSpan"
      ></SpanList>

      <!-- 提交按钮 -->
      <div>
        <!-- task status select -->
        <input
          type="radio"
          id="unfinished"
          name="status"
          value="unfinished"
          v-model="currentTask.status"
        />
        <label for="unfinished">未完成</label>
        <input
          type="radio"
          id="processing"
          name="status"
          value="processing"
          v-model="currentTask.status"
        />
        <label for="processing">处理中</label>
        <input
          type="radio"
          id="finished"
          name="status"
          value="finished"
          v-model="currentTask.status"
        />
        <label for="finished">已完成</label>
        <br />
        <label> 标注者： </label> <input type="text" v-model="currentTask.annotator" />
        <br />
        <button class="submit-btn" @click="submitTask">提交标注</button>
      </div>

      <!-- <NameExpander></NameExpander> -->
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import TineLine from './anno/TimeLine.vue'
import ImagePlayer from './ImagePlayer.vue'
import TaskList from './TaskList.vue'
import SpanList from './SpanList.vue'
import ImageCacheManager from './ImageCacheManager.vue'
// import NameExpander from './NameExpander.vue'

import constants from './constants'
const BaseURL = constants.BaseUrl
axios.defaults.baseURL = `${BaseURL}/api`

export default {
  components: {
    TineLine,
    ImagePlayer,
    TaskList,
    SpanList,
    // NameExpander,
    ImageCacheManager,
  },
  data() {
    return {
      taskList: [],
      currentTask: {
        task_name: '',
        annotator: '',
      },
      currentFrameIndex: 0,

      currentSpan: {
        start_index: -1,
        end_index: -1,
        annotation: '',
        used_for_vlm: false,
      },
      isEditing: false,

      imageMap: new Map(),
    }
  },
  computed: {
    allImageUrls() {
      return this.currentTask.frames
        .map((frame) => [
          `${BaseURL}/tasks/${this.currentTask.task_name}/img/front_color/${frame[0]}`,
          `${BaseURL}/tasks/${this.currentTask.task_name}/img/wrist_color/${frame[1]}`,
        ])
        .flat()
    },
  },
  mounted() {
    this.fetchTaskList()
  },
  methods: {
    async fetchTaskList() {
      try {
        const response = await axios.get('/get_task_list')
        this.taskList = response.data
      } catch (error) {
        console.error('获取任务列表失败:', error)
      }
    },

    async fetchTask(task) {
      try {
        // console.log(taskName)
        const taskName = task.task_name
        const response = await axios.get('/get_task', {
          params: { task_name: taskName },
        })
        this.currentTask = response.data
        this.currentFrameIndex = 0
      } catch (error) {
        console.error('获取任务详情失败:', error)
      }
    },

    async require_reload() {
      try {
        await axios.post('/reload')
        await this.fetchTaskList()
      } catch (error) {
        console.error('重新加载失败:', error)
      }
    },

    setStartFrame() {
      this.resetAnnotationState()
      this.currentSpan.start_index = this.currentFrameIndex
      this.currentSpan.end_index = -1
      this.isEditing = true
    },

    setEndFrame() {
      this.currentSpan.end_index = this.currentFrameIndex
      this.isEditing = false
    },

    saveAnnotation() {
      if (this.startFrame === -1 || this.endFrame === -1) return

      const newSpan = {
        start_index: this.currentSpan.start_index,
        end_index: this.currentSpan.end_index,
        annotation: this.currentSpan.annotation,
        used_for_vlm: this.currentSpan.used_for_vlm,
      }

      // console.log(`save nya: ${newSpan.start_index} - ${newSpan.end_index}: ${newSpan.annotation}`)
      // this.currentTask.spans = [...this.currentTask.spans, newSpan]

      // 如果spans中有相同的start_index，替换掉
      const idx = this.currentTask.spans.findIndex(
        (s) => s.start_index === this.currentSpan.start_index,
      )
      if (idx !== -1) {
        this.currentTask.spans.splice(idx, 1, newSpan)
      } else {
        this.currentTask.spans.push(newSpan)
        this.currentTask.spans.sort((a, b) => a.start_index - b.start_index)
      }
      this.resetAnnotationState()
    },

    deleteAnnotation() {
      this.currentTask.spans = this.currentTask.spans.filter(
        (s) => s.start_index !== this.currentSpan.start_index,
      )
      this.resetAnnotationState()
    },

    selectCurrentSpan(span) {
      if (this.isEditing) return
      this.currentSpan.start_index = span.start_index
      this.currentSpan.end_index = span.end_index
      this.currentSpan.annotation = span.annotation
      this.currentSpan.used_for_vlm = span.used_for_vlm
      this.currentFrameIndex = span.start_index
    },

    resetAnnotationState() {
      this.currentSpan.start_index = -1
      this.currentSpan.end_index = -1
      this.currentSpan.annotation = ''
      this.currentSpan.used_for_vlm = false
      this.isEditing = false
    },

    async submitTask(val = null) {
      try {
        if (val === null) {
          val = this.currentTask
        }
        await axios.post('/update_task', this.currentTask)
        alert('提交成功！')
        await this.fetchTaskList()
      } catch (error) {
        console.error('提交失败:', error)
      }
    },
  },
  watch: {
    currentTask(newVal, oldVal) {
      if (oldVal.task_name.length !== 0) {
        if (confirm('尝试切换任务，是否保存当前任务？')) {
          this.submitTask(oldVal)
        }
      }
    },
  },
}
</script>

<style>
.container {
  display: flex;
  height: 100vh;
}

.sidebar {
  width: 250px;
  border-right: 1px solid #ccc;
  padding: 10px;
  overflow-y: auto;
}

.task-item {
  padding: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.active {
  font-weight: bold;
  color: #42b983;
}

.main-content {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;

  position: relative;
}

.annotation-controls {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 20px;
  margin-top: 20px;
}

.span-list {
  border-top: 1px solid #ccc;
  padding: 10px;
  max-height: 200px;
  overflow-y: auto;
}

.span-list div {
  padding: 5px;
  cursor: pointer;
}

.selected {
  background-color: #e3f2fd;
}

.submit-btn {
  margin-top: auto;
  align-self: flex-start;
}
</style>
