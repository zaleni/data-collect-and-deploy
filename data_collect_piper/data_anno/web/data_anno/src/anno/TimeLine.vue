<template>
  <div class="bar-container" @click="handleContainerDoubleClick" @click.stop>
    <div
      v-for="(span, idx) in spans"
      :key="idx"
      class="highlight"
      :style="getSpanStyle(span, idx)"
      @mouseenter="showTooltip(idx, $event, span)"
      @mouseleave="hideTooltip"
      @dblclick="handleClick(span)"
    ></div>

    <div
      v-if="
        currentSpan && (isEditing || currentSpan.end_index !== -1) && currentSpan.start_index !== -1
      "
      class="highlight"
      :style="
        getSpanStyle(
          {
            start_index: currentSpan.start_index,
            end_index: isEditing ? progress : currentSpan.end_index,
          },
          spans.length,
        )
      "
    ></div>

    <!-- 进度线 -->
    <div class="progress-line" :style="getProgressLineStyle()"></div>

    <!-- 悬浮框 -->
    <div
      v-if="tooltip.visible"
      class="tooltip"
      :style="{ top: tooltip.y + 'px', left: tooltip.x + 'px' }"
    >
      <p>From {{ tooltip.l }} to {{ tooltip.r }}</p>
      <p>Annotation: {{ tooltip.annotation }}</p>
      <p>Used For VLM: {{ tooltip.used_for_vlm }}</p>
    </div>
  </div>
</template>

<script>
const distinctColors = [
  'rgba(255, 0, 0, 0.8)', // 红色 (色相0°)
  'rgba(63, 255, 0, 0.8)', // 亮绿 (色相90°)
  'rgba(0, 191, 255, 0.8)', // 天蓝 (色相195°)
  'rgba(255, 191, 0, 0.8)', // 橙黄 (色相45°)
  'rgba(127, 0, 255, 0.8)', // 蓝紫 (色相270°)
  'rgba(0, 255, 159, 0.8)', // 碧绿 (色相150°)
  'rgba(255, 0, 191, 0.8)', // 玫红 (色相315°)
  'rgba(0, 255, 63, 0.8)', // 酸橙 (色相135°)
  'rgba(191, 0, 255, 0.8)', // 紫晶 (色相285°)
  'rgba(255, 63, 0, 0.8)', // 橙红 (色相15°)
]

export default {
  props: ['n', 'spans', 'progress', 'currentSpan', 'isEditing'],
  data() {
    return {
      tooltip: {
        visible: false,
        annotation: '',
        used_for_vlm: false,
        l: -1,
        r: -1,
        x: 0,
        y: 0,
      },
    }
  },
  methods: {
    getSpanStyle({ start_index, end_index }, idx) {
      return {
        left: (start_index / this.n) * 100 + '%',
        width: ((end_index - start_index + 1) / this.n) * 100 + '%',
        backgroundColor: distinctColors[idx % distinctColors.length],
      }
    },
    getProgressLineStyle() {
      return {
        left: (this.progress / this.n) * 100 + '%',
      }
    },
    showTooltip(index, event, span) {
      // this.tooltip.text = `Start: ${span[0]}, End: ${span[1]}`;
      this.tooltip.l = span.start_index
      this.tooltip.r = span.end_index
      this.tooltip.annotation = span.annotation
      this.tooltip.used_for_vlm = span.used_for_vlm
      this.tooltip.x = event.clientX + 10
      this.tooltip.y = event.clientY + 10
      this.tooltip.visible = true
      // console.log(this.spans)
    },
    hideTooltip() {
      this.tooltip.visible = false
    },
    handleClick(span) {
      this.$emit('span-click', span)
    },
    handleContainerDoubleClick(event) {
      const rect = this.$el.getBoundingClientRect()
      const x = event.clientX - rect.left
      const val = (x / rect.width) * this.n
      // console.log(`container double click ${val}`)
      this.$emit('jump-to', Math.floor(val))
    },
  },
}
</script>

<style scoped>
.bar-container {
  position: relative;
  width: 100%;
  height: 35px;
  border-radius: 5px;
  border: 2px solid #ccc;
  background: linear-gradient(to right, #f8f9fa, #e9ecef);
  overflow: hidden;
}

.highlight {
  position: absolute;
  height: 100%;
  /* background-color: rgba(0, 123, 255, 0.6); */
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  cursor: pointer;
  border-radius: 3px;
}

.highlight:hover {
  transform: scaleY(1.2);
  box-shadow: 0 0 8px rgba(0, 123, 255, 0.8);
}

.progress-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 3px;
  background-color: red;
  box-shadow: 0 0 5px rgba(255, 0, 0, 0.8);
}

.tooltip {
  position: fixed;
  padding: 5px 10px;
  background: rgba(0, 0, 0, 0.75);
  color: #fff;
  border-radius: 5px;
  font-size: 12px;
  white-space: nowrap;
  pointer-events: none;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
  z-index: 10000;
}
</style>
