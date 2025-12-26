<template>
  <div class="tree-container" :style="{ width: '300px' }">
    <div v-for="node in processedTree" :key="node.parent" class="parent-node">
      <div class="parent-header" @click="toggleExpand(node.parent)">
        <span class="arrow">{{ isExpanded(node.parent) ? '▼' : '▶' }}</span>
        {{ node.parent }}
      </div>
      <div v-if="isExpanded(node.parent)" class="children-container">
        <div
          v-for="item in node.children"
          :key="item.task_name"
          class="child-node"
          :class="['status-' + item.status, 'transition-item']"
        >
          <span class="child-content">
            <span class="status-icon">
              {{ statusIcons[item.status] }}
            </span>
            {{ item.childName }}
          </span>
          <button class="child-button" @click.stop="handleClick(item)">➔</button>
        </div>
      </div>
    </div>

    <div class="action-buttons">
      <button class="btn" @click="handleRefresh">重新请求</button>
      <button class="btn" @click="handleReload">重新加载</button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    items: {
      type: Array,
      required: true,
      validator: (value) =>
        value.every(
          (item) =>
            typeof item.task_name === 'string' &&
            item.task_name.split('/').length === 2 &&
            ['unfinished', 'processing', 'finished'].includes(item.status),
        ),
    },
  },
  data() {
    return {
      expandedParents: [],
      statusIcons: {
        unfinished: '◯',
        processing: '◑',
        finished: '●',
      },
    }
  },
  computed: {
    processedTree() {
      const treeMap = {}

      this.items.forEach((item) => {
        const [parent, childName] = item.task_name.split('/')
        if (!treeMap[parent]) {
          treeMap[parent] = []
        }
        treeMap[parent].push({
          ...item,
          childName,
        })
      })

      return Object.entries(treeMap).map(([parent, children]) => ({
        parent,
        children: children.sort((a, b) => a.childName.localeCompare(b.childName)),
      }))
    },
  },
  methods: {
    isExpanded(parent) {
      return this.expandedParents.includes(parent)
    },
    toggleExpand(parent) {
      const index = this.expandedParents.indexOf(parent)
      if (index > -1) {
        this.expandedParents.splice(index, 1)
      } else {
        this.expandedParents.push(parent)
      }
    },
    handleClick(item) {
      this.$emit('node-click', item)
    },
    handleRefresh() {
      this.$emit('refresh')
    },
    handleReload() {
      this.$emit('reload')
    },
  },
}
</script>

<style scoped>
.tree-container {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 8px;
  font-family: Arial, sans-serif;
  position: relative;
  padding-bottom: 48px;
}

.parent-header {
  cursor: pointer;
  padding: 8px;
  background-color: #f5f5f5;
  border-radius: 4px;
  margin: 4px 0;
  display: flex;
  align-items: center;
  transition: background-color 0.2s;
}

.parent-header:hover {
  background-color: #eee;
}

.arrow {
  margin-right: 8px;
  font-size: 0.8em;
}

.children-container {
  margin-left: 20px;
  max-height: 60vh; /* 最大高度为视窗高度的60% */
  overflow-y: auto; /* 超出时显示垂直滚动条 */
  scrollbar-width: thin; /* 细滚动条 */
  scrollbar-color: #c1c1c1 #f5f5f5; /* 滚动条颜色 */
}
.children-container::-webkit-scrollbar {
  width: 8px;
}
.children-container::-webkit-scrollbar-track {
  background: #f5f5f5;
  border-radius: 4px;
}

.children-container::-webkit-scrollbar-thumb {
  background-color: #c1c1c1;
  border-radius: 4px;
  border: 2px solid #f5f5f5;
}

.child-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  margin: 4px 0;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.transition-item {
  transition:
    background-color 0.3s ease,
    opacity 0.3s ease;
}

.child-node:hover {
  transform: translateX(4px);
}

.status-unfinished {
  background-color: #fff3e0;
}
.status-processing {
  background-color: #e3f2fd;
}
.status-finished {
  background-color: #e8f5e9;
}

.child-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-icon {
  font-size: 0.9em;
}

.action-buttons {
  position: absolute;
  bottom: 8px;
  left: 8px;
  right: 8px;
  display: flex;
  gap: 8px;
  padding-top: 8px;
  border-top: 1px solid #eee;
}

.btn {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f8f9fa;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:hover {
  background-color: #e9ecef;
  transform: translateY(-1px);
}

.child-button {
  cursor: pointer;
  border: none;
  background: none;
  padding: 2px 8px;
  border-radius: 3px;
  transition: background-color 0.2s;
}

.child-button:hover {
  background-color: #e0e0e0;
}
</style>
