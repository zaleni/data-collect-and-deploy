<template>
  <div class="table-container">
    <table class="span-table">
      <thead>
        <tr>
          <th>开始帧</th>
          <th>结束帧</th>
          <th>标注文本</th>
          <th>用于VLM训练</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(span, index) in currentTask?.spans"
          :key="index"
          :class="{ selected: currentSpan.start_index === span.start_index }"
          @click="selectSpan(span)"
        >
          <td>{{ span.start_index }}</td>
          <td>{{ span.end_index }}</td>
          <td>{{ span.annotation }}</td>
          <td>{{ span.used_for_vlm ? '是' : '否' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  props: {
    currentTask: {
      type: Object,
      default: () => ({ spans: [] })
    },
    currentSpan: {
      type: Object,
      required: true
    }
  },
  methods: {
    selectSpan(span) {
      this.$emit('span-selected', span)
    }
  }
}
</script>

<style scoped>
.table-container {
  flex: 1;
  overflow-y: auto;
  min-height: 200px; /* 保持最小高度 */
}

.span-table {
  width: 100%;
  border-collapse: collapse;
}

.span-table th,
.span-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.span-table th {
  background-color: #f5f5f5;
  position: sticky;
  top: 0;
}

.span-table tr:hover {
  background-color: #fafafa;
  cursor: pointer;
}

.span-table tr.selected {
  background-color: #e3f2fd;
}
</style>
